import sys, time, math
from collections import defaultdict

start = time.perf_counter()
TIME_LIMIT = 2.85  # leave margin under 3s

data = list(map(int, sys.stdin.buffer.read().split()))
if not data:
    sys.exit()

it = iter(data)
N = next(it)
M = next(it)
pts = [(next(it), next(it)) for _ in range(M)]

S = 0
c = (N - 1) / 2.0
for x in range(N):
    dx = (x - c) * (x - c)
    for y in range(N):
        dy = (y - c) * (y - c)
        S += dx + dy + 1

def w(x, y):
    return (x - c) * (x - c) + (y - c) * (y - c) + 1

dots = set(pts)
drawn_segments = set()

def seg_key(a, b):
    if a > b:
        a, b = b, a
    return (a, b)

ops = []

# Candidate generation for axis-aligned and diagonal rectangles.
# We only use rectangles where three corners already have dots and the fourth is empty.
# Condition 2 checked by enumerating perimeter lattice points.
# Condition 3 checked by edge segments.
def perimeter_points_axis(x1, y1, x2, y2):
    # rectangle corners: (x1,y1), (x2,y1), (x2,y2), (x1,y2)
    pts = []
    if x1 == x2 or y1 == y2:
        return pts
    for x in range(min(x1, x2), max(x1, x2) + 1):
        pts.append((x, y1))
        pts.append((x, y2))
    for y in range(min(y1, y2) + 1, max(y1, y2)):
        pts.append((x1, y))
        pts.append((x2, y))
    return pts

def perimeter_points_diag(a, b, c1, d):
    # rectangle in rotated coords: corners are
    # p1 = ((a+c1)//2, (b+d)//2), p2 = ((a+d)//2, (b+c1)//2), etc.
    # Here use center-based formulation from two opposite corners?
    return []

# Precompute all possible axis-aligned rectangles from current dots?
# Small N => feasible to search all pairs with same x or same y.
def try_add(op):
    global dots
    p1, p2, p3, p4 = op
    if p1 in dots:
        return False
    if p2 not in dots or p3 not in dots or p4 not in dots:
        return False
    # Check rectangle type
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    # axis aligned
    ok = False
    if len({x1, x2, x3, x4}) == 2 and len({y1, y2, y3, y4}) == 2:
        ok = True
    else:
        # 45 degree rectangle: side vectors alternate between (a,b) and (a,-b)
        ok = True if True else False
    if not ok:
        return False
    # simplistic validity check for perimeter overlap on edges
    # build segments of the 4 sides
    segs = [seg_key(p1, p2), seg_key(p2, p3), seg_key(p3, p4), seg_key(p4, p1)]
    for s in segs:
        if s in drawn_segments:
            return False
    # condition 2: no other dots on perimeter for axis-aligned only
    if len({x1, x2, x3, x4}) == 2 and len({y1, y2, y3, y4}) == 2:
        xs = sorted([x1, x2, x3, x4])
        ys = sorted([y1, y2, y3, y4])
        xmin, xmax = xs[0], xs[-1]
        ymin, ymax = ys[0], ys[-1]
        per = set()
        for x in range(xmin, xmax + 1):
            per.add((x, ymin))
            per.add((x, ymax))
        for y in range(ymin + 1, ymax):
            per.add((xmin, y))
            per.add((xmax, y))
        for q in per:
            if q != p2 and q != p3 and q != p4 and q in dots:
                return False
    dots.add(p1)
    ops.append((p1, p2, p3, p4))
    for s in segs:
        drawn_segments.add(s)
    return True

# Greedy: scan for axis-aligned rectangles with high-weight empty corner.
# This is a conservative valid strategy.
max_iter = 100000
for _ in range(max_iter):
    if time.perf_counter() - start > TIME_LIMIT:
        break
    best = None
    best_score = -1.0
    # Enumerate pairs of existing dots with same x and same y patterns.
    # Use only rectangles where new point is one corner and other three are dots.
    dot_list = list(dots)
    # light sample reduction if many dots
    if len(dot_list) > 500:
        dot_list.sort(key=lambda p: w(p[0], p[1]), reverse=True)
        dot_list = dot_list[:500]
    dot_set = dots
    for i in range(len(dot_list)):
        x1, y1 = dot_list[i]
        if time.perf_counter() - start > TIME_LIMIT:
            break
        for j in range(i + 1, len(dot_list)):
            x2, y2 = dot_list[j]
            # axis-aligned rectangle candidate based on opposite corners
            if x1 == x2 or y1 == y2:
                continue
            cand = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
            # choose empty corner with max weight among empties; need 3 dots only
            for p1 in cand:
                if p1 in dot_set:
                    continue
                others = [p for p in cand if p != p1]
                if all(p in dot_set for p in others):
                    # perimeter empty except the 3 dots
                    xmin, xmax = min(x1, x2), max(x1, x2)
                    ymin, ymax = min(y1, y2), max(y1, y2)
                    ok = True
                    for x in range(xmin, xmax + 1):
                        for y in (ymin, ymax):
                            q = (x, y)
                            if q != others[0] and q != others[1] and q != others[2] and q in dot_set:
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        continue
                    for y in range(ymin + 1, ymax):
                        for x in (xmin, xmax):
                            q = (x, y)
                            if q != others[0] and q != others[1] and q != others[2] and q in dot_set:
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        continue
                    sc = w(*p1)
                    if sc > best_score:
                        best_score = sc
                        # order can be any cycle
                        best = (p1, others[0], others[1], others[2])
    if best is None:
        break
    p1, p2, p3, p4 = best
    # add segments
    segs = [seg_key(p1, p2), seg_key(p2, p3), seg_key(p3, p4), seg_key(p4, p1)]
    if any(s in drawn_segments for s in segs):
        break
    dots.add(p1)
    ops.append(best)
    for s in segs:
        drawn_segments.add(s)

out = [str(len(ops))]
for p1, p2, p3, p4 in ops:
    out.append(f"{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]} {p4[0]} {p4[1]}")
sys.stdout.write("\n".join(out))
