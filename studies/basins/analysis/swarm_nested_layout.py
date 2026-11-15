"""Swarm map, layout of two levels for a page (laptop, no judge call): where each cluster and each theme lies on a slab.

    python3 -m studies.basins.analysis.swarm_nested_layout studies/basins/results/swarm/<map run> studies/basins/results/swarm/themes-<nn>

Prints JSON with no board text: the input of tools/proof_idea_basins.py (branch ali/basin-atlas-page). x runs 0 to 1
and y 0 to wh. A cluster is a disc whose radius grows with the square root of its items; its items are packed in it
in the order they were posted, so a place inside a cluster carries no meaning. Each item also lists p, the places in
that order of the earlier items it builds on (the idea tree of the map run). Cluster centres start at the centroids
of the judge's map and are moved until clusters of one theme stand SAME apart and clusters of different themes at least
OTHER apart. A theme is the convex hull of its clusters' discs, widened by PAD.
"""
import json
import math
import pathlib
import sys

WH, S, SAME, OTHER, PAD, EDGE = 0.84, 0.0138, 0.042, 0.095, 0.026, 0.03

run, themes_run = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
SUM = json.loads((run / "summary.json").read_text())
MAP = json.loads((run / "map.json").read_text())
TH = json.loads((themes_run / "metrics.json").read_text())
board = sorted((n for n in MAP["nodes"] if n["kind"] != "possible" and not n.get("control_of")), key=lambda n: n["at_ns"])
theme_of = {c: i for i, t in enumerate(TH["themes"]) for c in t["clusters"]}
ids = sorted(theme_of, key=lambda c: (theme_of[c], c))
name = {b["basin"]: b["name"] for b in SUM["basins"]}
count = {c: sum(n["basin"] == c for n in board) for c in ids}
R = {c: S * (math.sqrt(count[c]) + 0.9) for c in ids}


def rank(vals, lo, hi):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    for k, i in enumerate(order):
        out[i] = lo + (hi - lo) * k / (len(vals) - 1)
    return out


cx = rank([sum(n["x"] for n in board if n["basin"] == c) / count[c] for c in ids], 0.16, 0.84)
cy = rank([sum(n["y"] for n in board if n["basin"] == c) / count[c] for c in ids], 0.16, WH - 0.16)
P = {c: [x, y] for c, x, y in zip(ids, cx, cy)}
for it in range(4000):
    for i in ids:
        for j in ids:
            if i >= j:
                continue
            same = theme_of[i] == theme_of[j]
            dx, dy = P[j][0] - P[i][0], P[j][1] - P[i][1]
            d = math.hypot(dx, dy) or 1e-6
            want = R[i] + R[j] + (SAME if same else OTHER)
            move = (want - d) / 2 if d < want else (-(d - want) * 0.04 if same and it < 3600 else 0.0)  # the last passes only push apart
            for c, sgn in ((i, -1), (j, 1)):
                P[c][0] += sgn * move * dx / d
                P[c][1] += sgn * move * dy / d
    for c in ids:  # a weak pull to the middle keeps the whole compact, and every disc stays on the slab
        if it < 3600:
            P[c][0] += (0.5 - P[c][0]) * 0.002
            P[c][1] += (WH / 2 - P[c][1]) * 0.002
        P[c][0] = min(1 - EDGE - R[c] - PAD, max(EDGE + R[c] + PAD, P[c][0]))
        P[c][1] = min(WH - EDGE - R[c] - PAD, max(EDGE + R[c] + PAD, P[c][1]))
lo = [min(P[c][k] - R[c] for c in ids) for k in (0, 1)]  # the whole is centred on the slab
hi = [max(P[c][k] + R[c] for c in ids) for k in (0, 1)]
for c in ids:
    P[c][0] += 0.5 - (lo[0] + hi[0]) / 2
    P[c][1] += WH / 2 - (lo[1] + hi[1]) / 2
for i in ids:
    for j in ids:
        if i < j:
            gap = math.hypot(P[j][0] - P[i][0], P[j][1] - P[i][1]) - R[i] - R[j]
            need = SAME if theme_of[i] == theme_of[j] else OTHER
            if gap < need * 0.97:
                sys.exit(f"layout failed: clusters {i} and {j} are {gap:.3f} apart, need {need}")


def hull(points):
    points = sorted(points)
    turn = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    def half(seq):
        out = []
        for q in seq:
            while len(out) > 1 and turn(out[-2], out[-1], q) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]
    return half(points) + half(points[::-1])


def inside(poly, q):
    return all((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0 for a, b in zip(poly, poly[1:] + poly[:1])) or \
           all((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) <= 0 for a, b in zip(poly, poly[1:] + poly[:1]))


themes = []
for t, th in enumerate(TH["themes"]):
    mine = [c for c in ids if theme_of[c] == t]
    pts = [(P[c][0] + (R[c] + PAD) * math.cos(a * math.pi / 18), P[c][1] + (R[c] + PAD) * math.sin(a * math.pi / 18)) for c in mine for a in range(36)]
    h = hull(pts)
    for c in ids:
        if theme_of[c] != t and any(inside(h, (P[c][0] + R[c] * math.cos(a * math.pi / 6), P[c][1] + R[c] * math.sin(a * math.pi / 6))) for a in range(12)):
            sys.exit(f"layout failed: cluster {c} lies inside theme {th['name']}")
    n = sum(count[c] for c in mine)
    themes.append({"name": th["name"], "n": n, "x": round(sum(P[c][0] * count[c] for c in mine) / n, 4), "y": round(sum(P[c][1] * count[c] for c in mine) / n, 4),
                   "hull": [[round(x, 4), round(y, 4)] for x, y in h]})
place = {c: i for i, c in enumerate(ids)}
seen = {c: 0 for c in ids}
at = {n["id"]: i for i, n in enumerate(board)}
items = []
for n in board:
    items.append({"kind": n["kind"], "c": place[n["basin"]], "k": seen[n["basin"]], "p": sorted(at[q["id"]] for q in n["parents"])})
    seen[n["basin"]] += 1
print(json.dumps({"wh": WH, "s": S, "themes": themes, "items": items,
                  "clusters": [{"name": TH["short"][str(c)], "full": name[c], "theme": theme_of[c], "n": count[c],
                                "x": round(P[c][0], 4), "y": round(P[c][1], 4), "r": round(R[c], 4)} for c in ids]}))
