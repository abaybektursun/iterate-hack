import sys
import time
import heapq
from collections import defaultdict

def main():
    input = sys.stdin.readline
    N, M = map(int, input().split())
    dots = set()
    for _ in range(M):
        x, y = map(int, input().split())
        dots.add((x, y))

    t0 = time.perf_counter()
    TL = 2.75

    c2 = (N - 1)
    def w(x, y):
        dx = 2 * x - c2
        dy = 2 * y - c2
        return dx * dx + dy * dy + 4  # proportional to original weight

    # Used segments: store normalized unit segments between adjacent grid points.
    used = set()

    def segs_of_rect(p1, p2, p3, p4):
        pts = [p1, p2, p3, p4]
        segs = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            x1, y1 = a
            x2, y2 = b
            dx = x2 - x1
            dy = y2 - y1
            g = abs(dx) if dx else abs(dy)
            sx = 0 if dx == 0 else (1 if dx > 0 else -1)
            sy = 0 if dy == 0 else (1 if dy > 0 else -1)
            x, y = x1, y1
            for _ in range(g):
                nx, ny = x + sx, y + sy
                segs.append((x, y, nx, ny))
                x, y = nx, ny
        return segs

    def on_perimeter_only_three(pts):
        # ensure exactly p2,p3,p4 are on perimeter among existing dots
        p1, p2, p3, p4 = pts
        per = set()
        for a, b in zip(pts, pts[1:] + pts[:1]):
            x1, y1 = a
            x2, y2 = b
            dx = x2 - x1
            dy = y2 - y1
            g = abs(dx) if dx else abs(dy)
            sx = 0 if dx == 0 else (1 if dx > 0 else -1)
            sy = 0 if dy == 0 else (1 if dy > 0 else -1)
            x, y = x1, y1
            for _ in range(g + 1):
                per.add((x, y))
                x += sx
                y += sy
        cnt = 0
        for p in dots:
            if p in per:
                cnt += 1
                if cnt > 3:
                    return False
        return True

    def valid_rect(p1, p2, p3, p4):
        # perimeter segments must not overlap used segments
        segs = segs_of_rect(p1, p2, p3, p4)
        for s in segs:
            if s in used or (s[2], s[3], s[0], s[1]) in used:
                return False
        return on_perimeter_only_three((p1, p2, p3, p4))

    # Build initial candidate heap from triples of dots.
    # We search for axis-aligned and 45-degree rectangles in a lightweight way.
    pts_list = list(dots)
    dotset = dots

    # For efficient existence checks.
    by_x = defaultdict(set)
    by_y = defaultdict(set)
    diag1 = defaultdict(set)  # x - y
    diag2 = defaultdict(set)  # x + y
    for x, y in dots:
        by_x[x].add(y)
        by_y[y].add(x)
        diag1[x - y].add((x, y))
        diag2[x + y].add((x, y))

    heap = []

    def push_candidate(p1, p2, p3, p4):
        if p1 in dots:
            return
        if valid_rect(p1, p2, p3, p4):
            # prefer high weight addition and shorter perimeter
            per = 0
            pts = [p1, p2, p3, p4]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                per += abs(a[0] - b[0]) + abs(a[1] - b[1])
            score = -(w(*p1) * 1000 - per * 10)
            heapq.heappush(heap, (score, p1, p2, p3, p4))

    # Enumerate plausible rectangles by using existing dot pairs as potential sides.
    # Axis-aligned rectangles
    ys_by_x = {x: sorted(list(s)) for x, s in by_x.items()}
    xs_by_y = {y: sorted(list(s)) for y, s in by_y.items()}

    for x1, ys in ys_by_x.items():
        ln = len(ys)
        for i in range(ln):
            y1 = ys[i]
            for j in range(i + 1, ln):
                y2 = ys[j]
                # other vertical side at x3
                for x3 in xs_by_y.get(y1, []):
                    if x3 == x1:
                        continue
                    if y2 in by_x.get(x3, ()):
                        # rectangle corners: (x1,y1),(x1,y2),(x3,y2),(x3,y1)
                        # try 4 possible placements for p1 as missing corner if not occupied
                        corners = [(x1, y1), (x1, y2), (x3, y2), (x3, y1)]
                        for idx in range(4):
                            p1 = corners[idx]
                            if p1 in dots:
                                continue
                            p2 = corners[(idx + 1) % 4]
                            p3 = corners[(idx + 2) % 4]
                            p4 = corners[(idx + 3) % 4]
                            push_candidate(p1, p2, p3, p4)

    # 45-degree rectangles based on diagonals
    # Use pairs with same x+y or x-y relationships.
    for s, pts in diag2.items():
        arr = list(pts)
        ln = len(arr)
        for i in range(ln):
            x1, y1 = arr[i]
            for j in range(i + 1, ln):
                x2, y2 = arr[j]
                if x1 == x2 or y1 == y2:
                    continue
                # candidate square/diamond: use center relation
                dx = x2 - x1
                dy = y2 - y1
                if abs(dx) != abs(dy):
                    continue
                # The other two corners of the axis-parallel rotated rectangle
                pA = (x1, y2)
                pB = (x2, y1)
                if 0 <= pA[0] < N and 0 <= pA[1] < N and 0 <= pB[0] < N and 0 <= pB[1] < N:
                    for p1, p2, p3, p4 in [
                        (pA, (x1, y1), pB, (x2, y2)),
                        (pB, (x1, y1), pA, (x2, y2)),
                    ]:
                        push_candidate(p1, p2, p3, p4)

    # Main greedy loop.
    ops = []
    while heap and time.perf_counter() - t0 < TL:
        _, p1, p2, p3, p4 = heapq.heappop(heap)
        if p1 in dots:
            continue
        if not valid_rect(p1, p2, p3, p4):
            continue

        # apply operation
        ops.append((p1, p2, p3, p4))
        dots.add(p1)
        by_x[p1[0]].add(p1[1])
        by_y[p1[1]].add(p1[0])
        diag1[p1[0] - p1[1]].add(p1)
        diag2[p1[0] + p1[1]].add(p1)

        # mark used segments
        for s in segs_of_rect(p1, p2, p3, p4):
            used.add(s)

        # Local candidate regeneration: use the new dot with nearby dots to form more rectangles.
        x0, y0 = p1
        # axis-aligned: combine with dots sharing x or y
        for y1 in list(by_x.get(x0, [])):
            if y1 == y0:
                continue
            for x2 in list(by_y.get(y0, [])):
                if x2 == x0:
                    continue
                if y1 in by_x.get(x2, ()):
                    corners = [(x0, y0), (x0, y1), (x2, y1), (x2, y0)]
                    for idx in range(4):
                        q1 = corners[idx]
                        if q1 in dots and q1 != p1:
                            continue
                        q2 = corners[(idx + 1) % 4]
                        q3 = corners[(idx + 2) % 4]
                        q4 = corners[(idx + 3) % 4]
                        if q1 not in dots:
                            push_candidate(q1, q2, q3, q4)

        # diagonal/45-degree local regeneration
        for d in (-1, 1):
            for dx in range(1, N):
                for sign in (-1, 1):
                    x2 = x0 + sign * dx
                    y2 = y0 + d * sign * dx
                    if not (0 <= x2 < N and 0 <= y2 < N):
                        continue
                    if (x2, y2) not in dots:
                        continue
                    # form candidate with another point on opposite diagonal if possible
                    x3, y3 = x0, y2
                    x4, y4 = x2, y0
                    if 0 <= x3 < N and 0 <= y3 < N and 0 <= x4 < N and 0 <= y4 < N:
                        for q1, q2, q3, q4 in [
                            ((x3, y3), (x0, y0), (x4, y4), (x2, y2)),
                            ((x4, y4), (x0, y0), (x3, y3), (x2, y2)),
                        ]:
                            if q1 not in dots:
                                push_candidate(q1, q2, q3, q4)

    out = []
    out.append(str(len(ops)))
    for p1, p2, p3, p4 in ops:
        out.append(f"{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]} {p4[0]} {p4[1]}")
    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    main()
