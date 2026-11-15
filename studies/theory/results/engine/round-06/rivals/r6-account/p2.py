"""p2: hard328. RL plain's solve rate on the cued base's cap-hit problems minus the rate expected from RL's rate on the
base's finished-wrong problems with the same count k3 of right answers in three self-distilled cue arms."""
import json
import os
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5"
KEYS = {
    "B": "day1_hard328-01/abaybektursun-1114-151534-e72c",
    "RL": "day1_hard328-01/abaybektursun-1114-151540-86ef",
    "c1": "selfdistill-01/abaybektursun-1114-201021-095e",
    "c2": "selfdistill-01/abaybektursun-1114-201035-c6c0",
    "c3": "selfdistill-01/abaybektursun-1114-201132-3c04",
}


def local(key):
    return f"runs/theory-tests/s3k/r5/{key}/answers.jsonl"


def fetch(key):
    path = local(key)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{key}/answers.jsonl", path, "--profile", "iterate-ecr",
                        "--only-show-errors"], check=False)
    return path if os.path.exists(path) else None


def one_per_problem(path):
    """Smallest attempt per problem_index; first in file order if no attempt field (or on ties)."""
    best = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        pi = r.get("problem_index")
        if pi is None:
            continue
        if pi not in best:
            best[pi] = r
            continue
        a_new, a_old = r.get("attempt"), best[pi].get("attempt")
        if a_new is not None and a_old is not None and a_new < a_old:
            best[pi] = r
    return best


def right(r, cap_counts_as_right=False):
    if r is None:
        return False
    if r.get("score_v3") != 1:
        return False
    return cap_counts_as_right or r.get("cap_hit") is not True


def stratum(k):
    return 2 if k >= 2 else k


def stat(sample):
    f_n, f_r = {}, {}
    for e in sample:
        if e["group"] == "F":
            f_n[e["stratum"]] = f_n.get(e["stratum"], 0) + 1
            f_r[e["stratum"]] = f_r.get(e["stratum"], 0) + (1 if e["rl"] else 0)
    cs = [e for e in sample if e["group"] == "C" and f_n.get(e["stratum"], 0) > 0]
    if not cs:
        return 0.0  # no C problem left in this resample (bootstrap only; the main number is checked below)
    obs = sum(1 for e in cs if e["rl"]) / len(cs)
    exp = sum(f_r[e["stratum"]] / f_n[e["stratum"]] for e in cs) / len(cs)
    return obs - exp


def build(rows, cap_counts_as_right):
    B, RL = rows["B"], rows["RL"]
    entries = []
    for pi in sorted(set(B) & set(RL)):
        if right(B[pi], cap_counts_as_right):
            continue
        group = "C" if B[pi].get("cap_hit") is True else "F"
        k3 = sum(1 for c in ("c1", "c2", "c3") if right(rows[c].get(pi), cap_counts_as_right))
        entries.append({"problem_index": pi, "group": group, "k3": k3, "stratum": stratum(k3),
                        "rl": right(RL[pi], cap_counts_as_right)})
    return entries


def main():
    rows = {}
    for name, key in KEYS.items():
        p = fetch(key)
        if p is None:
            return not_computable(f"{BUCKET}/{key}/answers.jsonl not readable")
        rows[name] = one_per_problem(p)
    entries = build(rows, False)
    f_strata = {e["stratum"] for e in entries if e["group"] == "F"}
    cs = [e for e in entries if e["group"] == "C" and e["stratum"] in f_strata]
    if not cs:
        return not_computable("no C problem remains after dropping strata without F problems")
    measured = stat(entries)
    alt = stat(build(rows, True))
    pi = cs[0]["problem_index"]
    strip = lambda r: None if r is None else {k: v for k, v in r.items() if k not in ("text", "prompt")}
    ex = {"problem_index": pi, "group": "C", "k3": cs[0]["k3"], "B": strip(rows["B"][pi]),
          "RL": strip(rows["RL"][pi])}
    report(measured, len(entries), bootstrap(stat, entries), "bootstrap", refuted_by_met=False, alt_measured=alt,
           example_row=ex)


if __name__ == "__main__":
    main()
