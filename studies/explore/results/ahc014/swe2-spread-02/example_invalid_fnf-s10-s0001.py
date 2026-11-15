import sys
import time
import random


def solve(n, m, init_points, weight, deadline, rng, noise, perim_pen):
    N2 = n * n
    occ = bytearray(N2)
    occupied = []
    for p in init_points:
        if not occ[p]:
            occ[p] = 1
            occupied.append(p)

    used_edges = set()
    moves = []

    def rect_edges_and_clear(vs):
        edges = []
        for i in range(4):
            a = vs[i]
            b = vs[(i + 1) & 3]
            ax, ay = divmod(a, n)
            bx, by = divmod(b, n)
            dx = bx - ax
            dy = by - ay
            steps = abs(dx) if abs(dx) > abs(dy) else abs(dy)
            sx = 0 if dx == 0 else (1 if dx > 0 else -1)
            sy = 0 if dy == 0 else (1 if dy > 0 else -1)
            x, y = ax, ay
            for _ in range(steps):
                x += sx
                y += sy
                p1 = x * n + y - n * sx - sy
                p2 = x * n + y
                e = p1 * N2 + p2 if p1 < p2 else p2 * N2 + p1
                edges.append(e)
                if (x != bx or y != by) and occ[x * n + y]:
                    return None, 0
        return edges, len(edges)

    def push(missing, vs):
        k = vs.index(missing)
        rect = vs[k:] + vs[:k]
        key = -weight[missing] + rng.random() * noise + perim_pen * (abs(rect[1] - rect[0]) + abs(rect[3] - rect[0]))
        moves.append((key, missing, rect))

    def try_quad(missing, vs):
        if occ[missing]:
            return
        push(missing, vs)

    def pair_candidates(p, q):
        x1, y1 = divmod(p, n)
        x2, y2 = divmod(q, n)
        dx = x2 - x1
        dy = y2 - y1
        adx = dx if dx >= 0 else -dx
        ady = dy if dy >= 0 else -dy

        # axis-aligned rectangle, p/q diagonal corners
        if dx and dy:
            a = x1 * n + y2
            b = x2 * n + y1
            if occ[a] != occ[b]:
                missing = b if occ[a] else a
                xl = x1 if x1 < x2 else x2
                xh = x2 if x1 < x2 else x1
                yl = y1 if y1 < y2 else y2
                yh = y2 if y1 < y2 else y1
                vs = (xl * n + yl, xh * n + yl, xh * n + yh, xl * n + yh)
                k = vs.index(missing)
                rect = vs[k:] + vs[:k]
                key = -weight[missing] + rng.random() * noise
                moves.append((key, missing, rect))

        # axis-aligned, p/q vertical side
        if x1 == x2:
            s = ady
            for sx in (s, -s):
                nx1 = x1 + sx
                if 0 <= nx1 < n:
                    a = nx1 * n + y1
                    b = nx1 * n + y2
                    if occ[a] != occ[b]:
                        missing = b if occ[a] else a
                        if sx > 0:
                            vs = (p, q, b, a)
                        else:
                            vs = (a, b, q, p)
                        k = vs.index(missing)
                        rect = vs[k:] + vs[:k]
                        moves.append((-weight[missing] + rng.random() * noise, missing, rect))

        # axis-aligned, p/q horizontal side
        if y1 == y2:
            s = adx
            for sy in (s, -s):
                ny1 = y1 + sy
                if 0 <= ny1 < n:
                    a = x1 * n + ny1
                    b = x2 * n + ny1
                    if occ[a] != occ[b]:
                        missing = b if occ[a] else a
                        if sy > 0:
                            vs = (q, p, a, b)
                        else:
                            vs = (b, a, p, q)
                        k = vs.index(missing)
                        rect = vs[k:] + vs[:k]
                        moves.append((-weight[missing] + rng.random() * noise, missing, rect))

        # tilted square, p/q vertical or horizontal diagonal
        if x1 == x2 and (ady & 1) == 0:
            r = ady >> 1
            cx = x1
            cy = (y1 + y2) >> 1
            if 0 <= cx - r and cx + r < n:
                a = (cx - r) * n + cy
                b = (cx + r) * n + cy
                if occ[a] != occ[b]:
                    missing = b if occ[a] else a
                    vs = (cx * n + cy + r * n, (cx + r) * n + cy, cx * n + cy - r * n, (cx - r) * n + cy)
                    k = vs.index(missing)
                    rect = vs[k:] + vs[:k]
                    moves.append((-weight[missing] + rng.random() * noise, missing, rect))
        if y1 == y2 and (adx & 1) == 0:
            r = adx >> 1
            cx = (x1 + x2) >> 1
            cy = y1
            if 0 <= cy - r and cy + r < n:
                a = cx * n + cy - r
                b = cx * n + cy + r
                if occ[a] != occ[b]:
                    missing = b if occ[a] else a
                    vs = (cx * n + cy + r * n, (cx + r) * n + cy, cx * n + cy - r * n, (cx - r) * n + cy)
                    k = vs.index(missing)
                    rect = vs[k:] + vs[:k]
                    moves.append((-weight[missing] + rng.random() * noise, missing, rect))

        # tilted square, p/q as a side (dx,dy)=(±s,±s)
        if adx == ady:
            wx = -dy
            wy = dx
            ax = x1 + wx
            ay = y1 + wy
            bx = x2 + wx
            by = y2 + wy
            if 0 <= ax < n and 0 <= ay < n and 0 <= bx < n and 0 <= by < n:
                a = ax * n + ay
                b = bx * n + by
                if occ[a] != occ[b]:
                    missing = b if occ[a] else a
                    vs = (p, q, b, a)
                    k = vs.index(missing)
                    rect = vs[k:] + vs[:k]
                    moves.append((-weight[missing] + rng.random() * noise, missing, rect))
            ax = x1 - wx
            ay = y1 - wy
            bx = x2 - wx
            by = y2 - wy
            if 0 <= ax < n and 0 <= ay < n and 0 <= bx < n and 0 <= by < n:
                a = ax * n + ay
                b = bx * n + by
                if occ[a] != occ[b]:
                    missing = b if occ[a] else a
                    vs = (q, p, a, b)
                    k = vs.index(missing)
                    rect = vs[k:] + vs[:k]
                    moves.append((-weight[missing] + rng.random() * noise, missing, rect))

    ln = len(occupied)
    for i in range(ln):
        pi = occupied[i]
        for j in range(i + 1, ln):
            pair_candidates(pi, occupied[j])

    import heapq
    heapq.heapify(moves)

    answer = []
    total = 0
    checks = 0

    while moves and time.time() < deadline:
        key, missing, rect = heapq.heappop(moves)
        if occ[missing]:
            continue
        if not (occ[rect[1]] and occ[rect[2]] and occ[rect[3]]):
            continue
        edges, _ = rect_edges_and_clear(rect)
        if edges is None:
            continue
        bad = False
        for e in edges:
            if e in used_edges:
                bad = True
                break
        if bad:
            continue
        for e in edges:
            used_edges.add(e)
        occ[missing] = 1
        total += weight[missing]
        answer.append(rect)
        for q in occupied:
            pair_candidates(missing, q)
            checks += 1
            if checks >= 128:
                checks = 0
                if time.time() >= deadline:
                    occupied.append(missing)
                    return answer, total
        occupied.append(missing)

    return answer, total


def main():
    start = time.time()
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        print(0)
        return
    it = iter(data)
    n = next(it)
    m = next(it)
    init = []
    for _ in range(m):
        x = next(it)
        y = next(it)
        init.append(x * n + y)

    c = (n - 1) * 0.5
    weight = [0] * (n * n)
    for x in range(n):
        dx = x - c
        base = x * n
        for y in range(n):
            dy = y - c
            weight[base + y] = int(dx * dx + dy * dy) + 1

    deadline = start + 2.8
    rng = random.Random(12345)

    best_ans = []
    best_total = -1

    ans, tot = solve(n, m, init, weight, deadline, rng, 0.0, 0.0)
    best_ans, best_total = ans, tot

    trial = 0
    while time.time() < deadline:
        trial += 1
        noise = 50.0 * (1 + (trial % 5))
        pen = 0.0 if (trial % 3) else 0.02
        ans, tot = solve(n, m, init, weight, deadline, rng, noise, pen)
        if tot > best_total:
            best_ans, best_total = ans, tot

    out = [str(len(best_ans))]
    for rect in best_ans:
        vals = []
        for p in rect:
            x, y = divmod(p, n)
            vals.append(str(x))
            vals.append(str(y))
        out.append(" ".join(vals))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
