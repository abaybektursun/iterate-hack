"""Swarm map, step 3 (laptop, no model): basins, coverage and moves of the team's board, from swarm_judge.py output.

    python3 -m studies.basins.analysis.swarm_analyze runs/swarm/judge-<t> studies/basins/results/swarm/<arm>-<nn>

Basins are the judge's groups (partition 0); partition 1 and k-means on the t-STE map are checks on them.
Coverage: share of the judge's possible directions that sit in a basin with at least one board item, and
(stricter) directions that the judge says at least one board item pursues (coverage.jsonl, two board orders).
Moves: consecutive board items of one person in different basins; "new" if that person had not been in the basin.
Writes summary.json and map.json (nodes with x, y, basin) to the output folder.
"""
import json
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from studies.basins.lib.embed import tste, tste_acc

J, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
nodes = json.loads((J / "nodes.json").read_text())
parts = [json.loads(l) for l in open(J / "partitions.jsonl")]
rows = [json.loads(l) for l in open(J / "triplets.jsonl")]
ids = [n["id"] for n in nodes]
pos = {i: k for k, i in enumerate(ids)}
by = {n["id"]: n for n in nodes}
labels = [{i: g for g, grp in enumerate(p["groups"]) for i in grp["ids"]} for p in parts]
names = [g["name"] for g in parts[0]["groups"]]

# order consistency: the same (a, {b, c}) asked in both orders must pick the same item
pairs = defaultdict(list)
for r in rows:
    pairs[(r["a"], frozenset((r["b"], r["c"])))].append(r["pick"])
consistent, trips = 0, []
for (a, bc), picks in pairs.items():
    if len(picks) == 2 and picks[0] is not None and picks[0] == picks[1]:
        consistent += 1
        w = picks[0]
        trips.append((pos[a], pos[w], pos[next(iter(bc - {w}))]))
n_pairs = sum(len(p) == 2 for p in pairs.values())

# t-STE: held-out accuracy vs the same map scored on shuffled ids, then one map from all triplets
random.Random(0).shuffle(trips)
cut = int(0.9 * len(trips))
X = tste(len(ids), trips[:cut])
held = tste_acc(X, trips[cut:])
perm = list(range(len(ids)))
random.Random(1).shuffle(perm)
null = tste_acc(X, [(perm[a], perm[b], perm[c]) for a, b, c in trips[cut:]])
X = tste(len(ids), trips)

# k-means on the map (3-8 clusters by silhouette, as in the Bespoke post) as a check on the judge's groups
km = {k: KMeans(k, n_init=20, random_state=0).fit_predict(X) for k in range(3, 9)}
best_k = max(km, key=lambda k: silhouette_score(X, km[k]))
lab0 = [labels[0][i] for i in ids]

# control: copies must share the original's group in both partitions and be its nearest neighbours on the map
ctl = [n for n in nodes if n.get("control_of")]
ctl_checks = []
for c in ctl:
    o = c["control_of"]
    d = np.linalg.norm(X - X[pos[c["id"]]], axis=1)
    rank = int((d < d[pos[o]]).sum()) - 1  # nodes closer than the original, excluding itself
    ctl_checks.append({"copy": c["id"], "of": o, "same_group": [lb[c["id"]] == lb[o] for lb in labels], "closer_than_original": rank})

# swarm metrics over real board items (controls excluded)
board = sorted([n for n in nodes if n["kind"] != "possible" and not n.get("control_of")], key=lambda n: int(n["at_ns"]))
possible = [n for n in nodes if n["kind"] == "possible"]
basin_board = Counter(labels[0][n["id"]] for n in board)
basin_poss = Counter(labels[0][n["id"]] for n in possible)
visited = set(basin_board)
cover = [labels[0][n["id"]] in visited for n in possible]
p = np.array(list(basin_board.values()), float) / len(board)
moves, seen, last = [], defaultdict(set), {}
for n in board:
    b, who = labels[0][n["id"]], n["who"]
    if who in last and last[who] != b:
        moves.append({"who": who, "at": n["at"], "from": names[last[who]], "to": names[b], "new": b not in seen[who]})
    seen[who].add(b)
    last[who] = b

# direct coverage: board items the judge says pursue each possible direction, in two orders of the board
covs = [json.loads(l)["coverage"] for l in open(J / "coverage.jsonl")] if (J / "coverage.jsonl").exists() else []
direction = {}
for n in possible:
    sets = [set(next(c["items"] for c in cov if c["direction"] == n["id"])) for cov in covs]
    direction[n["id"]] = {"id": n["id"], "name": n["text"].split(":")[0], "items_both": sorted(set.intersection(*sets)) if sets else [],
                          "items_either": sorted(set.union(*sets)) if sets else [], "orders_agree": len({bool(x) for x in sets}) == 1}

# leaderboard: scored configurations from result items (swarm_scores.py), joined to basins and directions
scores = json.loads((J / "scores.json").read_text()) if (J / "scores.json").exists() else []
dir_of = defaultdict(list)
for dd in direction.values():
    for i in dd["items_either"]:
        dir_of[i].append(dd["name"])
board_v3 = [r for r in scores if r["grader"] == "v3"]
leaderboard = []
for r in sorted(scores, key=lambda r: (r["grader"] != "v3", -r["score_pct"])):
    leaderboard.append({**{k: r[k] for k in ("item", "model", "method", "setting", "benchmark", "n", "correct", "score_pct", "grader", "quote")},
                        "basin": names[labels[0][r["item"]]], "directions": dir_of.get(r["item"], []),
                        "more_tokens": any(w in r["method"].lower() for w in ("restart", "vote", "best-of", "attempt")),
                        "superseded": r["grader"] != "v3"})
best_base = max((r for r in board_v3 if r["model"] == "base"), key=lambda r: r["score_pct"], default=None)
best_base_one = max((r for r in leaderboard if r["model"] == "base" and not r["superseded"] and not r["more_tokens"]), key=lambda r: r["score_pct"], default=None)
rl_ref = max((r for r in board_v3 if r["model"] == "rl" and r["setting"].startswith("T 1.0")), key=lambda r: r["score_pct"], default=None)  # AI2 setting, as in DIRECTION.md
basin_best = defaultdict(float)
for r in board_v3:
    if r["model"] == "base":
        g = labels[0][r["item"]]
        basin_best[g] = max(basin_best[g], r["score_pct"])

basins = [{"basin": g, "name": names[g], "board_items": basin_board.get(g, 0), "possible": basin_poss.get(g, 0), "best_base_pct": basin_best.get(g),
           "kinds": dict(Counter(by[i]["kind"] for i in parts[0]["groups"][g]["ids"] if not by[i].get("control_of")))}
          for g in range(len(names))]
summary = {
    "n_board_items": len(board), "n_possible": len(possible), "n_basins": len(names),
    "basins_visited": len(visited), "basins_only_possible": [b["name"] for b in basins if b["board_items"] == 0],
    "coverage_of_possible_directions": [int(sum(cover)), len(cover)],
    "largest_basin_share": float(p.max()), "effective_basins": float(np.exp(-(p * np.log(p)).sum())),
    "moves": len(moves), "moves_to_new_basin": sum(m["new"] for m in moves),
    "triplet_order_consistency": [consistent, n_pairs], "tste_heldout_acc": held, "tste_shuffled_id_null": null,
    "partition_ari_order0_vs_order1": adjusted_rand_score(lab0, [labels[1][i] for i in ids]),
    "kmeans_best_k": best_k, "partition_ari_vs_kmeans": adjusted_rand_score(lab0, km[best_k]),
    "directions_pursued_both_orders": [sum(bool(d["items_both"]) for d in direction.values()), len(direction)],
    "directions_pursued_either_order": [sum(bool(d["items_either"]) for d in direction.values()), len(direction)],
    "directions_pursued_agree_across_orders": [sum(d["orders_agree"] for d in direction.values()), len(direction)],
    "directions_untouched": [d["name"] for d in direction.values() if not d["items_either"]],
    "directions": list(direction.values()),
    "leaderboard": leaderboard,
    "best_base_pct": best_base and best_base["score_pct"], "best_base_one_sample_pct": best_base_one and best_base_one["score_pct"],
    "rl_reference_pct": rl_ref and rl_ref["score_pct"],
    "control": ctl_checks, "basins": sorted(basins, key=lambda b: -b["board_items"]), "move_list": moves,
}
(out / "summary.json").write_text(json.dumps(summary, indent=1))
(out / "map.json").write_text(json.dumps({"names": names, "nodes": [
    {**{k: n.get(k) for k in ("id", "kind", "who", "at", "at_ns", "text", "control_of")},
     "x": float(X[pos[n["id"]], 0]), "y": float(X[pos[n["id"]], 1]), "basin": labels[0][n["id"]]} for n in nodes]}))
print(json.dumps({k: v for k, v in summary.items() if k not in ("basins", "move_list", "directions", "control", "leaderboard")}))
for b in summary["basins"]:
    print(f"  {b['board_items']:3d} board  {b['possible']:2d} possible  {b['name']}")
