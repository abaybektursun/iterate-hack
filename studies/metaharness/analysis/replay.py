"""SPEC1 Part B readout: one rlneurons cell run three ways (whole on H100, N shards on H100, whole on B200), from the
jobs' own records. Run after `uv run tools/gpu.py get <job>` for every job:

    uv run --with modal --with boto3 python -m studies.metaharness.analysis.replay \
        --arm whole_h100=<job> --arm shard4_h100=<job>,<job>,<job>,<job> --arm whole_b200=<job> --reference whole_h100

Per job: queue minutes (submit to container start) and container minutes (start to end) from the Modal job record
(tools/gpu.py load), and wall, engine load, generation seconds, tokens and v3 counts from runs/<job>/metrics.json.
Per arm: cell minutes = the longest job of the arm (its jobs run at the same time), GPU minutes = their sum, and the
rows of answers.jsonl compared with the reference arm by problem_index (same text, same v3 score).
Writes results/replay/<arm>-01/ (run.json, metrics.json, examples.json) and refuses an existing folder.
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import gpu  # noqa: E402

OUT = ROOT / "studies" / "metaharness" / "results" / "replay"


def job(job_id, records):
    r, run = records[job_id], ROOT / "runs" / job_id
    assert gpu.state(r) == "done", f"{job_id} is {gpu.state(r)}: score only finished jobs"
    m = json.loads((run / "metrics.json").read_text())
    assert m["status"] == "done" and m["job_id"] == job_id
    rows = [json.loads(line) for line in (run / "answers.jsonl").read_text().splitlines()]
    container = (r["end"]["at"] - r["start"]["at"]) / 60
    return {"job_id": job_id, "gpu": r["start"]["gpu"], "commit": r["job"]["sha"], "command": r["job"]["cmd"],
            "queue_min": (r["start"]["at"] - r["job"]["at"]) / 60, "container_min": container,
            "setup_min": container - m["wall_s"] / 60, "load_min": m["engine"]["load_s"] / 60,
            "generation_min": m["counts"]["generation_s"] / 60, "n": m["counts"]["n"], "correct_v3": m["counts"]["correct_v3"],
            "cap_hits": m["counts"]["cap_hits"], "generated_tokens": m["counts"]["generated_tokens"],
            "tokens_per_s": m["counts"]["tokens_per_s"], "num_gpu_blocks": m["engine"]["num_gpu_blocks"]}, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True, help="name=job[,job...]")
    ap.add_argument("--reference", required=True)
    a = ap.parse_args()
    arms = {name: ids.split(",") for name, ids in (s.split("=") for s in a.arm)}
    records, done = gpu.load(), {}
    for name, ids in arms.items():
        jobs, rows = zip(*(job(i, records) for i in ids))
        by_index = {r["problem_index"]: r for part in rows for r in part}
        assert len(by_index) == sum(j["n"] for j in jobs), f"{name}: a problem appears in two jobs"
        done[name] = (list(jobs), by_index)
    reference = done[a.reference][1]
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=ROOT).stdout.strip()
    for name, (jobs, by_index) in done.items():
        assert set(by_index) == set(reference), f"{name} and {a.reference} hold different problems"
        metrics = {"arm": name, "jobs": jobs, "n": len(by_index),
                   "cell_min": max(j["container_min"] for j in jobs), "gpu_min": sum(j["container_min"] for j in jobs),
                   "queue_min_max": max(j["queue_min"] for j in jobs),
                   "generation_min_max": max(j["generation_min"] for j in jobs),
                   "correct_v3": sum(j["correct_v3"] for j in jobs), "cap_hits": sum(j["cap_hits"] for j in jobs),
                   "generated_tokens": sum(j["generated_tokens"] for j in jobs),
                   "against_reference": {"arm": a.reference,
                                         "same_text": sum(by_index[i]["text"] == reference[i]["text"] for i in by_index),
                                         "same_score_v3": sum(by_index[i]["score_v3"] == reference[i]["score_v3"] for i in by_index)}}
        folder = OUT / f"{name}-01"
        folder.mkdir(parents=True)  # fails when the run folder exists: a rerun gets the next number
        keep = ("problem_index", "unique_id", "seed", "prompt", "text", "extracted_v3", "gold", "score_v3", "n_new", "cap_hit")
        right = next(r for r in by_index.values() if r["score_v3"] == 1)
        wrong = next(r for r in by_index.values() if r["score_v3"] == 0)
        (folder / "examples.json").write_text(json.dumps({"right": {k: right[k] for k in keep}, "wrong": {k: wrong[k] for k in keep}}, indent=1))
        (folder / "metrics.json").write_text(json.dumps(metrics, indent=1))
        (folder / "run.json").write_text(json.dumps({"commit": sha, "command": " ".join(sys.argv), "job_ids": [j["job_id"] for j in jobs],
                                                       "raw_answers": "runs/<job id>/answers.jsonl after `uv run tools/gpu.py get <job id>` (sameraslan's Modal workspace)"}, indent=1))
        m = metrics
        print(f"{name}: cell {m['cell_min']:.1f} min, GPU {m['gpu_min']:.1f} min, generation {m['generation_min_max']:.1f} min, "
              f"queue {m['queue_min_max']:.1f} min, {m['correct_v3']}/{m['n']} v3, same text as {a.reference} "
              f"{m['against_reference']['same_text']}/{m['n']}, same score {m['against_reference']['same_score_v3']}/{m['n']}")


if __name__ == "__main__":
    main()
