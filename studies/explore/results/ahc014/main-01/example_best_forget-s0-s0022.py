import sys
import time
from math import gcd

START = time.time()
LIMIT = 3.0
TIME_MARGIN = 0.92

def time_up():
    return time.time() - START > LIMIT * TIME_MARGIN

data = list(map(int, sys.stdin.buffer.read().split()))
if not data:
    print(0)
    raise SystemExit

it = iter(data)
N = next(it)
M = next(it)

occ = set()
for _ in range(M):
    occ.add((next(it), next(it)))

center = (N - 1) / 2.0

drawn_edges = set()

def norm_edge(a, b):
    return (a, b) if a <= b else (b, a)

def add_segment(a, b):
    x1, y1 = a
    x2, y2 = b
    dx = x2 - x1
    dy = y2 - y1
    g = gcd(abs(dx), abs(dy))
    if g == 0:
        return
    sx = dx // g
    sy = dy // g
    x, y = x1, y1
    for _ in range(g):
        nx, ny = x + sx, y + sy
        drawn_edges.add(norm_edge((x, y), (nx, ny)))
        x, y = nx, ny

def segment_overlaps(a, b):
    x1, y1 = a
    x2, y2 = b
    dx = x2 - x1
    dy = y2 - y1
    g = gcd(abs(dx), abs(dy))
    if g == 0:
        return True
    sx = dx // g
    sy = dy // g
    x, y = x1, y1
    for _ in range(g):
        nx, ny = x + sx, y + sy
        if norm_edge((x, y), (nx, ny)) in drawn_edges:
            return True
        x, y = nx, ny
    return False

def perimeter_clear(v):
    allow = {v[1], v[2], v[3]}
    for i in range(4):
        a = v[i]
        b = v[(i + 1) % 4]
        if segment_overlaps(a, b):
            return False
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        g = gcd(abs(dx), abs(dy))
        if g <= 1:
            continue
        sx = dx // g
        sy = dy // g
        x, y = a
        for _ in range(g - 1):
            x += sx
            y += sy
            if (x, y) in occ and (x, y) not in allow:
                return False
    return True

ops = []

# Sort occupied points by desirability: farther from center first.
def weight(p):
    return (p[0] - center) ** 2 + (p[1] - center) ** 2

# Main greedy loop: repeatedly try to create a new point in a high-weight location.
while not time_up():
    occ_list = list(occ)
    occ_list.sort(key=lambda p: -weight(p))

    made = False

    # 1) Axis-aligned rectangles: if three corners of an axis rectangle exist, fill the fourth.
    for i in range(len(occ_list)):
        if time_up():
            break
        x1, y1 = occ_list[i]
        for j in range(i + 1, len(occ_list)):
            x2, y2 = occ_list[j]
            if x1 == x2 or y1 == y2:
                continue

            corners = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
            empty = [c for c in corners if c not in occ]
            if len(empty) != 1:
                continue

            p1 = empty[0]
            others = [c for c in corners if c != p1]

            # Try both possible cyclic orders of the three occupied corners.
            candidates = [
                [p1, others[0], others[1], others[2]],
                [p1, others[0], others[2], others[1]],
                [p1, others[1], others[0], others[2]],
                [p1, others[1], others[2], others[0]],
                [p1, others[2], others[0], others[1]],
                [p1, others[2], others[1], others[0]],
            ]

            for v in candidates:
                good = True
                for k in range(4):
                    a = v[k]
                    b = v[(k + 1) % 4]
                    dx = abs(a[0] - b[0])
                    dy = abs(a[1] - b[1])
                    if dx != 0 and dy != 0:
                        good = False
                        break
                    if dx == 0 and dy == 0:
                        good = False
                        break
                if not good:
                    continue
                if perimeter_clear(v):
                    ops.append((v[0], v[1], v[2], v[3]))
                    occ.add(v[0])
                    add_segment(v[0], v[1])
                    add_segment(v[1], v[2])
                    add_segment(v[2], v[3])
                    add_segment(v[3], v[0])
                    made = True
                    break
            if made:
                break
        if made:
            break
    if made:
        continue

    # 2) 45-degree rectangles: use diagonals with one endpoint as the new point.
    # For a point A, if B and C are occupied and B-A and C-A are perpendicular with equal length,
    # then D = B + C - A completes a 45-degree rectangle. We fill D if exactly one corner is empty.
    occ_list = list(occ)
    occ_set = occ
    for a in occ_list:
        if time_up():
            break
        ax, ay = a
        # Search a limited neighborhood in all 4 diagonal directions.
        # This keeps runtime reasonable while still finding many opportunities.
        for dx1, dy1 in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for l1 in range(1, N):
                b = (ax + dx1 * l1, ay + dy1 * l1)
                if not (0 <= b[0] < N and 0 <= b[1] < N):
                    break
                if b not in occ_set:
                    continue
                # Perpendicular diagonal direction
                dx2, dy2 = dy1, -dx1
                for l2 in range(1, N):
                    c = (ax + dx2 * l2, ay + dy2 * l2)
                    if not (0 <= c[0] < N and 0 <= c[1] < N):
                        break
                    if c not in occ_set:
                        continue
                    d = (b[0] + c[0] - ax, b[1] + c[1] - ay)
                    if not (0 <= d[0] < N and 0 <= d[1] < N):
                        continue
                    if d in occ_set:
                        continue

                    # Determine cyclic order a-b-d-c or a-c-d-b.
                    cand1 = [d, b, a, c]
                    cand2 = [d, c, a, b]

                    for v in (cand1, cand2):
                        # Check rectangle sides: consecutive segments must be valid diagonals/axis.
                        ok = True
                        for k in range(4):
                            x1, y1 = v[k]
                            x2, y2 = v[(k + 1) % 4]
                            dx = abs(x1 - x2)
                            dy = abs(y1 - y2)
                            if not (dx == 0 or dy == 0 or dx == dy):
                                ok = False
                                break
                            if dx == 0 and dy == 0:
                                ok = False
                                break
                        if not ok:
                            continue
                        if perimeter_clear(v):
                            ops.append((v[0], v[1], v[2], v[3]))
                            occ.add(v[0])
                            add_segment(v[0], v[1])
                            add_segment(v[1], v[2])
                            add_segment(v[2], v[3])
                            add_segment(v[3], v[0])
                            made = True
                            break
                    if made:
                        break
                if made:
                    break
            if made:
                break
        if made:
            break

    if not made:
        break

out = [str(len(ops))]
out.extend(f"{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]} {p4[0]} {p4[1]}" for p1, p2, p3, p4 in ops)
sys.stdout.write("\n".join(out))
