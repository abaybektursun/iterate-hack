"""Pilot: past.dev recall against grep over the team's transcripts, on questions with a known answer.
Questions: N board score rows (model, benchmark, configuration); gold answer = "<right>/<n>" as posted on the board.
Arms: (A) POST /recall, maxTokens 2000, as tools/recall.py does; (B) grep over a local copy of every uploaded
transcript: the two longest words of the question, +-250 characters around each co-occurrence.
Reads only. Costs one past.dev credit per question (0.0003 USD). Writes metrics.json, rows.jsonl and examples.json
into a new run folder. Usage, from the repository root:
python3 -m studies.metaharness.analysis.recall_pilot --board <board dump .json> --traces <transcripts folder> --n 20 --out <new run folder>"""
import argparse, json, pathlib, random, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from past import IDENTITY, call
parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--board", required=True, type=Path, help="full board dump (.json with a 'scores' list)")
parser.add_argument("--traces", required=True, type=Path, help="local copy of the team's transcript store (*.jsonl below it)")
parser.add_argument("--n", required=True, type=int, help="number of questions")
parser.add_argument("--out", required=True, type=Path, help="run folder to create; must not exist")
args = parser.parse_args()
if args.out.exists(): raise SystemExit(f"{args.out} exists: a rerun gets the next number")
N = args.n
board = json.loads(args.board.read_text())
names = {"base": "untrained base model", "rl": "RL-Zero-Math checkpoint", "other": ""}
rows = [s for s in board["scores"] if s["benchmark"] in ("MATH-500", "hard328")]
random.seed(0); random.shuffle(rows)
seen, questions = set(), []
for s in rows:
    if s["config"] in seen: continue
    seen.add(s["config"])
    questions.append({"q": f"{names[s['model']]} {s['benchmark']} accuracy: {s['config']}".strip(), "right": s["right"], "n": s["n"], "result": s["result"]})
questions = questions[:N]
def match(text, q):
    return re.search(rf"(?<!\d){q['right']}\s*(/|of|out of)\s*{q['n']}(?!\d)", text)
def hit(text, q):
    return bool(match(text, q))
files = sorted(args.traces.rglob("*.jsonl"))
assert files, f"no *.jsonl under {args.traces}"
corpus_bytes = sum(f.stat().st_size for f in files)
STOP = {"accuracy", "untrained", "checkpoint", "math-500", "hard328", "model", "top-p"}
def grep(q):
    """Two timings. files_s: plain `grep -rIilF <word>`, the cheapest real grep (which transcripts mention the word).
    The evidence text comes from a scan in Python (faster than BSD grep -o on these files, whose lines are whole tool
    outputs: one `grep -rIihoE .{0,250}word.{0,250}` ran over 3 min 50 s on one question and was stopped)."""
    words = sorted({w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", q["q"]) if w.lower() not in STOP}, key=len, reverse=True)[:2]
    w1, w2 = words[0].lower().encode(), (words[1].lower().encode() if len(words) > 1 else b"")
    start = time.time()
    run = subprocess.run(["grep", "-rIilF", words[0], str(args.traces)], capture_output=True, text=True)
    assert run.returncode in (0, 1) and not run.stderr, run.stderr[:300]  # 1 = no match; anything else is a broken grep
    files_s, n_files = time.time() - start, len(run.stdout.splitlines())
    start, keep = time.time(), []
    for path in run.stdout.splitlines():
        raw = pathlib.Path(path).read_bytes(); low = raw.lower(); i = low.find(w1)
        while i != -1:
            lo, hi = max(0, i - 250), i + len(w1) + 250
            if w2 in low[lo:hi]: keep.append(raw[lo:hi].decode("utf-8", "replace")); i = low.find(w1, hi)
            else: i = low.find(w1, i + len(w1))
    return words, "\n".join(keep), files_s, time.time() - start, n_files
def example(q, text, extra):
    """The real input, output and score of one question (AGENTS.md, Results rule 6): `text` is what was scored."""
    m = match(text, q)
    return {"input": {"question": q["q"], "gold": f"{q['right']}/{q['n']}", "board_result": q["result"], **extra.pop("input", {})},
            "output": {"text_first_600_chars": text[:600], "text_chars": len(text), "matched": m.group(0) if m else None, "matched_at_char": m.start() if m else None, **extra},
            "score": {"hit": bool(m)}}
out, examples = [], {"recall": {"right": None, "wrong": None}, "grep_first_2000_tokens": {"right": None, "wrong": None}}
for q in questions:
    start = time.time()
    page = call("POST", "recall", {"query": q["q"], "identity": IDENTITY, "maxTokens": 2000})
    a_s = time.time() - start
    a_text = "\n".join(r["content"] + " " + " ".join(e for s in r["sources"] for e in s.get("excerpts", [])) for r in page["results"])
    a_ids = [s["sourceId"] for r in page["results"] for s in r["sources"]]
    words, b_text, files_s, scan_s, n_files = grep(q)
    row = {**q, "recall_s": round(a_s, 2), "recall_tokens": page["usedEvidenceTokens"], "recall_results": len(page["results"]), "recall_hit": hit(a_text, q),
           "recall_cites_result": f"board:{q['result']}" in a_ids,
           "grep_words": words, "grep_files_s": round(files_s, 2), "grep_files": n_files, "grep_s": round(files_s + scan_s, 2), "grep_tokens": len(b_text) // 4, "grep_hit_any": hit(b_text, q), "grep_hit_first_2000_tokens": hit(b_text[:8000], q)}
    out.append(row); print(json.dumps(row), flush=True)
    for arm, ok, made in (("recall", row["recall_hit"], lambda: example(q, a_text, {"tokens": row["recall_tokens"], "results": row["recall_results"], "source_ids": a_ids})),
                          ("grep_first_2000_tokens", row["grep_hit_first_2000_tokens"], lambda: example(q, b_text[:8000], {"input": {"grep_words": words}, "tokens_before_cut": row["grep_tokens"], "files_matched": n_files, "hit_anywhere_in_full_output": row["grep_hit_any"]}))):
        side = "right" if ok else "wrong"
        if examples[arm][side] is None: examples[arm][side] = made()
def med(k): v = sorted(r[k] for r in out); return v[len(v) // 2]
summary = {"n": len(out), "corpus_files": len(files), "corpus_MB": round(corpus_bytes / 1e6),
           "recall_hit": sum(r["recall_hit"] for r in out), "recall_cites_result": sum(r["recall_cites_result"] for r in out),
           "grep_hit_first_2000_tokens": sum(r["grep_hit_first_2000_tokens"] for r in out), "grep_hit_any": sum(r["grep_hit_any"] for r in out),
           "recall_s_median": med("recall_s"), "grep_s_median": med("grep_s"), "recall_tokens_median": med("recall_tokens"), "grep_tokens_median": med("grep_tokens"),
           "recall_tokens_mean": round(sum(r["recall_tokens"] for r in out) / len(out)), "grep_tokens_mean": round(sum(r["grep_tokens"] for r in out) / len(out))}
print("SUMMARY", json.dumps(summary))
examples["note"] = "First question of the run scored right and first scored wrong, per arm; null = no such question in this run. grep text is the first 8,000 characters (2,000 tokens at 4 characters per token) of the grep output, the part that was scored."
args.out.mkdir(parents=True)
(args.out / "metrics.json").write_text(json.dumps(summary, indent=1) + "\n")
(args.out / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
(args.out / "examples.json").write_text(json.dumps(examples, indent=1, ensure_ascii=False) + "\n")
