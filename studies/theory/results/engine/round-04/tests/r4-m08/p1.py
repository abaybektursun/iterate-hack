"""r4-m08 prediction 1: length-matched (RL minus cued base) gap, post-cutoff minus pre-cutoff, harder 328."""
import json
import os
import subprocess

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
BASE_JOB = "abaybektursun-1114-151534-e72c"  # base cue
RL_JOB = "abaybektursun-1114-151540-86ef"    # RL plain
OVERLAP = "studies/rlneurons/results/rln3/rln3_overlap.json"
POST_SOURCES = {"aime2025", "hmmt_feb2025"}


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def fetch(job):
    path = f"runs/theory-tests/{job}/answers.jsonl"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{job}/answers.jsonl", path,
                            "--profile", "iterate-ecr", "--only-show-errors"])
        if r.returncode != 0 or not os.path.exists(path):
            subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path])
    if not os.path.exists(path):
        return None
    return path


def load(path):
    rows = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                rows[r["unique_id"]] = r
    return rows


def slim(r):
    return {k: v for k, v in r.items() if k not in ("text", "prompt")}


def main():
    bp, rp = fetch(BASE_JOB), fetch(RL_JOB)
    if bp is None or rp is None:
        out(None, False, None, "answers.jsonl could not be fetched", None)
        return
    base, rl = load(bp), load(rp)
    flags = json.load(open(OVERLAP))["sets"]["hard"]["flags"]

    uids = sorted(set(base) & set(rl))  # drop any unique_id missing from either file
    items = []
    for u in uids:
        b, r = base[u], rl[u]
        key = str(r["problem_index"])
        if key not in flags:
            out(None, False, None, f"problem_index {key} of {u} not in rln3_overlap.json", None)
            return
        src = flags[key]["source"]
        if src != u.split("/")[0]:
            out(None, False, None, f"source mismatch for {u}: overlap says {src}", None)
            return
        items.append({
            "uid": u,
            "group": "post" if src in POST_SOURCES else "pre",
            "len": r["n_generated"],
            "d": (1 if r["score_v3"] == 1 else 0) - (1 if b["score_v3"] == 1 else 0),
            "b": b, "r": r,
        })

    n = len(items)
    if n < 4:
        out(None, False, None, "fewer than 4 joined problems", None)
        return
    items.sort(key=lambda x: (x["len"], x["uid"]))
    size = n // 4
    strata = [items[i * size:(i + 1) * size] for i in range(3)] + [items[3 * size:]]

    n_post = sum(1 for x in items if x["group"] == "post")
    if n_post == 0:
        out(None, False, None, "no post-cutoff problems in the joined set", None)
        return

    weights, dpost, dpre = [], [], []
    for s in strata:
        post = [x["d"] for x in s if x["group"] == "post"]
        pre = [x["d"] for x in s if x["group"] == "pre"]
        if not post:
            continue  # w_s = 0
        if not pre:
            continue  # drop stratum with post but no pre; renormalised below
        weights.append(len(post) / n_post)
        dpost.append(sum(post) / len(post))
        dpre.append(sum(pre) / len(pre))
    if not weights:
        out(None, False, None, "no stratum has both post and pre problems", None)
        return
    tw = sum(weights)
    w = [x / tw for x in weights]
    g_post = sum(wi * d for wi, d in zip(w, dpost))
    g_pre = sum(wi * d for wi, d in zip(w, dpre))
    stat = 100.0 * (g_post - g_pre)

    ex_item = next(x for x in items if x["group"] == "post")
    ex = {"unique_id": ex_item["uid"], "group": ex_item["group"],
          "source": flags[str(ex_item["r"]["problem_index"])]["source"],
          "rl_n_generated": ex_item["r"]["n_generated"],
          "rl_score_v3": ex_item["r"]["score_v3"], "base_score_v3": ex_item["b"]["score_v3"],
          "rl_cap_hit": ex_item["r"]["cap_hit"], "base_cap_hit": ex_item["b"]["cap_hit"],
          "base_row": slim(ex_item["b"]), "rl_row": slim(ex_item["r"])}
    out(stat, stat < -3, None, None, ex)


if __name__ == "__main__":
    main()
