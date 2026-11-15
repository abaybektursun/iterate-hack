"""k=2: among non-self-opened T3 rows (cap hits included) where first_score != v3_last, the share with first_score == 1."""
import json
import pathlib
import subprocess

from studies.rlneurons.lib import rln4_lib as R
from studies.theory.lib.noise import bootstrap, report, not_computable

S3 = "s3://pg-lineage-769063704696/results/rlneurons/r4/modal_t3-01/t3/T3.jsonl"
LOCAL = pathlib.Path("runs/theory-tests/s3/r4/modal_t3-01/t3/T3.jsonl")
BOXED = "\\boxed{"


def fetch():
    if not LOCAL.exists():
        LOCAL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["aws", "s3", "cp", S3, str(LOCAL), "--profile", "iterate-ecr", "--only-show-errors"], check=True)


def first_rows():
    out, seen = [], set()
    for line in open(LOCAL):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["problem_index"] in seen:
            continue
        seen.add(r["problem_index"])
        out.append(r)
    return out


def first_marker(text):
    """(start, content, end) of the earliest marker, or None."""
    cands = []
    pos = 0
    for ln in text.split("\n"):
        st = ln.lstrip()
        if st.startswith("Answer:"):
            cands.append((pos + len(ln) - len(st), st[len("Answer:"):], pos + len(ln)))
            break
        pos += len(ln) + 1
    i = text.find(BOXED)
    if i >= 0:
        depth, j = 1, i + len(BOXED)
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        if depth == 0:
            cands.append((i, text[i + len(BOXED):j - 1], j))
        else:
            cands.append((i, text[i + len(BOXED):], len(text)))
    return min(cands, key=lambda c: c[0]) if cands else None


def v3(gold, text):
    s = R.grade_v3(gold, text)["score_v3"]
    return int(s or 0)


def main():
    try:
        fetch()
        rows = first_rows()
    except Exception as e:  # file not readable
        not_computable(f"T3.jsonl not readable: {e!r}")
        return
    for f in ("text", "gold", "cap_hit", "problem_index"):
        if any(f not in r for r in rows):
            not_computable(f"field {f} missing in T3.jsonl rows")
            return
    recs = []
    for r in rows:
        text = r["text"] or ""
        if "\nOkay" in text[:60]:
            continue
        last = v3(r["gold"], text)
        m = first_marker(text)
        first = 0 if m is None else v3(r["gold"], "Answer: " + m[1])
        recs.append({"r": r, "last": last, "first": first, "cap": bool(r["cap_hit"]), "marker": m})
    disc = [x for x in recs if x["first"] != x["last"]]
    if not disc:
        not_computable("no discordant rows (recipe: report nothing)")
        return

    def stat(sample):
        return sum(x["first"] == 1 for x in sample) / len(sample)

    measured = stat(disc)
    nocap = [x for x in disc if not x["cap"]]
    alt = stat(nocap) if nocap else None
    ex = next((x for x in disc if x["first"] == 1), disc[0])
    er = dict(ex["r"])
    er["text"] = er["text"][:1500] + ("...[truncated]" if len(er["text"]) > 1500 else "")
    er.update({"v3_last": ex["last"], "first_score": ex["first"], "first_content": None if ex["marker"] is None else ex["marker"][1][:300]})
    report(measured, len(disc), bootstrap(stat, disc), "bootstrap", refuted_by_met=False, alt_measured=alt, example_row=er)


main()
