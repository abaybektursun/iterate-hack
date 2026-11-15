"""Per-problem rows of T3 (base, plain prompt, T 1.0) and T1 (base with the cue, T 1.0) on MATH-500 under grader v3, saved rows only.

    python -m studies.rlneurons.analysis.rln4_t1_t3_items <T3.jsonl> <T1.jsonl> <out dir>

The two cell files are those of results/rln4/grader_v3/readout.json (files.base_plain_1.0, files.base_opener_1.0); their
sha256 must match. Every text is scored with rln4_lib.grade_v3. Written into <out dir>, which must not exist yet:
  per_problem.json  one row per problem: problem_index, t3_right, t1_right, t3_cap_hit, t1_cap_hit, t3_generated_tokens,
                    t1_generated_tokens, t3_extracted_v3, t1_extracted_v3 (cut at 60 characters), t3_start, t1_start (the
                    first START characters of the answer text; T1's text begins with the cue " line!\\n\\nOkay")
  metrics.json      right, cap hits and nothing extracted per cell, and the 2x2 of right and wrong
The page tools/finding_opening_cue.py draws these rows. Fail loud: no try/except, no fallback.
"""
import hashlib
import json
import pathlib
import sys

from studies.rlneurons.lib import rln4_lib as R

STUDY = pathlib.Path(__file__).resolve().parents[1]
MATH = STUDY / "data" / "rln4" / "math500.json"
READOUT = STUDY / "results" / "rln4" / "grader_v3" / "readout.json"
START = 240


def load(path, problems, sha):
    assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() == sha, f"{path}: sha256 differs from {READOUT}"
    rows = {}
    for line in open(path):
        r = json.loads(line)
        i = r["problem_index"]
        assert i not in rows, f"{path}: problem {i} twice"
        assert r["gold"] == problems[i]["answer"], f"{path}: problem {i} differs from {MATH}"
        g = R.grade_v3(r["gold"], r["text"])
        rows[i] = {"right": int(g["score_v3"]), "cap_hit": bool(r["cap_hit"]), "tokens": r["n_generated"],
                   "extracted": None if g["extracted_v3"] is None else g["extracted_v3"][:60], "start": r["text"][:START]}
    assert sorted(rows) == sorted(problems), f"{path}: {len(rows)} rows"
    return rows


def main():
    t3_path, t1_path, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
    problems = {p["index"]: p for p in json.load(open(MATH))}
    files = json.load(open(READOUT))["files"]
    a, b = load(t3_path, problems, files["base_plain_1.0"]["sha256"]), load(t1_path, problems, files["base_opener_1.0"]["sha256"])
    table = [{"problem_index": i, "t3_right": a[i]["right"], "t1_right": b[i]["right"], "t3_cap_hit": a[i]["cap_hit"],
              "t1_cap_hit": b[i]["cap_hit"], "t3_generated_tokens": a[i]["tokens"], "t1_generated_tokens": b[i]["tokens"],
              "t3_extracted_v3": a[i]["extracted"], "t1_extracted_v3": b[i]["extracted"], "t3_start": a[i]["start"],
              "t1_start": b[i]["start"]} for i in sorted(problems)]
    cell = lambda rows: {"right": sum(r["right"] for r in rows.values()), "cap_hits": sum(r["cap_hit"] for r in rows.values()),
                         "nothing_extracted": sum(r["extracted"] is None for r in rows.values())}
    metrics = {"n": len(table), "grader": "v3 (rln4_lib.grade_v3)", "t3": cell(a), "t1": cell(b),
               "two_by_two": {"both": sum(r["t3_right"] and r["t1_right"] for r in table),
                              "cue_only": sum(r["t1_right"] and not r["t3_right"] for r in table),
                              "plain_only": sum(r["t3_right"] and not r["t1_right"] for r in table),
                              "neither": sum(not r["t3_right"] and not r["t1_right"] for r in table)}}
    out.mkdir(parents=True)
    (out / "per_problem.json").write_text("[\n" + ",\n".join(json.dumps(row, ensure_ascii=False) for row in table) + "\n]\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
