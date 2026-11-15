import sys
import time
import math

input = sys.stdin.readline
start = time.perf_counter()
TL = 2.85

N, M = map(int, input().split())
dots = set()
rows = [set() for _ in range(N)]
cols = [set() for _ in range(N)]
for _ in range(M):
    x, y = map(int, input().split())
    dots.add((x, y))
    rows[y].add(x)
    cols[x].add(y)

c = (N - 1) / 2.0


def wt(x, y):
    dx = x - c
    dy = y - c
    return dx * dx + dy * dy + 1.0


def segkey(a, b):
    return (a, b) if a <= b else (b, a)


used = set()


def add_rect(rect):
    for i in range(4):
        x1, y1 = rect[i]
        x2, y2 = rect[(i + 1) % 4]
        dx = x2 - x1
        dy = y2 - y1
        g = math.gcd(abs(dx), abs(dy))
        sx = dx // g
        sy = dy // g
        x, y = x1, y1
        for _ in range(g):
            nx, ny = x + sx, y + sy
            used.add(segkey((x, y), (nx, ny)))
            x, y = nx, ny


def has_overlap(rect):
    for i in range(4):
        x1, y1 = rect[i]
        x2, y2 = rect[(i + 1) % 4]
        dx = x2 - x1
        dy = y2 - y1
        g = math.gcd(abs(dx), abs(dy))
        sx = dx // g
        sy = dy // g
        x, y = x1, y1
        for _ in range(g):
            nx, ny = x + sx, y + sy
            if segkey((x, y), (nx, ny)) in used:
                return True
            x, y = nx, ny
    return False


def clear_perimeter(rect):
    for i in range(4):
        x1, y1 = rect[i]
        x2, y2 = rect[(i + 1) % 4]
        dx = x2 - x1
        dy = y2 - y1
        g = math.gcd(abs(dx), abs(dy))
        if g <= 1:
            continue
        sx = dx // g
        sy = dy // g
        x, y = x1, y1
        for _ in range(g - 1):
            x += sx
            y += sy
            if (x, y) in dots:
                return False
    return True


ops = []


def valid(rect):
    if rect[0] in dots:
        return False
    # exactly three existing dots among 4 corners
    cnt = 0
    for p in rect:
        if p in dots:
            cnt += 1
    if cnt != 3:
        return False
    if not clear_perimeter(rect):
        return False
    if has_overlap(rect):
        return False
    return True


def apply(rect):
    p1 = rect[0]
    ops.append(rect)
    dots.add(p1)
    rows[p1[1]].add(p1[0])
    cols[p1[0]].add(p1[1])
    add_rect(rect)


def score_move(rect):
    x, y = rect[0]
    base = wt(x, y)
    # Prefer positions that expand around the new dot and touch denser lines.
    fut = len(rows[y]) + len(cols[x])
    # Slight preference for center-adjacent growth to keep completions available.
    fut += max(0.0, 6.0 - 0.35 * (abs(x - c) + abs(y - c)))
    return base + 0.08 * fut


def axis_candidates_for_point(x, y):
    if (x, y) in dots:
        return
    xs = rows[y]
    ys = cols[x]
    if not xs or not ys:
        return
    # Try high-weight line intersections first.
    xlist = sorted(xs, key=lambda xx: abs(xx - c))
    ylist = sorted(ys, key=lambda yy: abs(yy - c))
    for x2 in xlist:
        if x2 == x:
            continue
        for y2 in ylist:
            if y2 == y:
                continue
            rect = [(x, y), (x2, y), (x2, y2), (x, y2)]
            yield rect


def diamond_candidates_for_point(x, y):
    if (x, y) in dots:
        return
    # Axis-aligned candidates are usually better; enumerate diamonds only when possible.
    # Rectangle vertices: (cx,cy+r),(cx+r,cy),(cx,cy-r),(cx-r,cy)
    # Each loop tries to place (x,y) as one of the four vertices.
    max_r = N - 1
    for r in range(1, max_r + 1):
        # top
        cx, cy = x, y - r
        if 0 <= cx - r and cx + r < N and 0 <= cy - r and cy + r < N:
            rect = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
            if rect[0] == (x, y):
                yield rect
        # right
        cx, cy = x - r, y
        if 0 <= cx - r and cx + r < N and 0 <= cy - r and cy + r < N:
            rect = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
            if rect[1] == (x, y):
                yield rect[1:] + rect[:1]
        # bottom
        cx, cy = x, y + r
        if 0 <= cx - r and cx + r < N and 0 <= cy - r and cy + r < N:
            rect = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
            if rect[2] == (x, y):
                yield rect[2:] + rect[:2]
        # left
        cx, cy = x + r, y
        if 0 <= cx - r and cx + r < N and 0 <= cy - r and cy + r < N:
            rect = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
            if rect[3] == (x, y):
                yield rect[3:] + rect[:3]


# High-weight points first, but keep a bit of spread.
all_points = [(wt(x, y), x, y) for x in range(N) for y in range(N)]
all_points.sort(reverse=True)

# Precompute a filtered pool around the center and extremes.
prefix_limit = min(len(all_points), 260)

while time.perf_counter() - start < TL:
    best_rect = None
    best_sc = -1e18

    # Main scan: high-weight empty cells.
    for idx in range(prefix_limit):
        if time.perf_counter() - start > TL:
            break
        _, x, y = all_points[idx]
        if (x, y) in dots:
            continue

        # Axis aligned
        for rect in axis_candidates_for_point(x, y):
            if valid(rect):
                sc = score_move(rect)
                if sc > best_sc:
                    best_sc = sc
                    best_rect = rect
        # If we already found something very good, don't waste too much time.
        if best_rect is not None and best_sc > wt(x, y) + 15.0:
            break

        # Diamond
        for rect in diamond_candidates_for_point(x, y):
            if valid(rect):
                sc = score_move(rect)
                if sc > best_sc:
                    best_sc = sc
                    best_rect = rect
        if best_rect is not None and best_sc > wt(x, y) + 15.0:
            break

    # Fallback scan over remaining cells if needed.
    if best_rect is None:
        for _, x, y in all_points[prefix_limit:]:
            if time.perf_counter() - start > TL:
                break
            if (x, y) in dots:
                continue
            found = False
            for rect in axis_candidates_for_point(x, y):
                if valid(rect):
                    best_rect = rect
                    found = True
                    break
            if found:
                break
            for rect in diamond_candidates_for_point(x, y):
                if valid(rect):
                    best_rect = rect
                    found = True
                    break
            if found:
                break

    if best_rect is None:
        break

    apply(best_rect)

out = [str(len(ops))]
for p1, p2, p3, p4 in ops:
    out.append(f"{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]} {p4[0]} {p4[1]}")
sys.stdout.write("\n".join(out) + "\n")
