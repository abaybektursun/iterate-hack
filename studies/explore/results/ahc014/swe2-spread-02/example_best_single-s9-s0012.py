import sys, time, heapq, random

def main():
    t0 = time.time()
    LIMIT = 2.85
    data = sys.stdin.read().split()
    it = iter(data)
    N = int(next(it)); M = int(next(it))
    init_dots = [(int(next(it)), int(next(it))) for _ in range(M)]
    init_set = set(init_dots)

    DX = [1, 1, 0, -1, -1, -1, 0, 1]
    DY = [0, 1, 1, 1, 0, -1, -1, -1]
    PAIRS = [(0, 2), (2, 4), (4, 6), (6, 0), (1, 3), (3, 5), (5, 7), (7, 1)]
    OFF2 = N - 1
    c = (N - 1) / 2.0

    W = [0] * (N * N)
    for x in range(N):
        for y in range(N):
            W[y * N + x] = int((x - c) ** 2 + (y - c) ** 2) + 1

    def inside(x, y):
        return 0 <= x < N and 0 <= y < N

    def side_key(ax, ay, bx, by):
        dx = bx - ax; dy = by - ay
        if dy == 0:
            lo, hi = (ax, bx) if ax < bx else (bx, ax)
            return 0, ay, lo, hi
        if dx == 0:
            lo, hi = (ay, by) if ay < by else (by, ay)
            return 1, ax, lo, hi
        if dx == dy:
            lo, hi = (ax, bx) if ax < bx else (bx, ax)
            return 2, ax - ay + OFF2, lo, hi
        lo, hi = (ax, bx) if ax < bx else (bx, ax)
        return 3, ax + ay, lo, hi

    def side_mask(lo, hi):
        return ((1 << (hi - lo)) - 1) << lo

    def clean_prefix(ops):
        have = set(init_set)
        out = []
        for op in ops:
            rx, ry, qx, qy, px, py, sx, sy = op
            if (rx, ry) in have:
                continue
            if (qx, qy) in have and (px, py) in have and (sx, sy) in have:
                out.append(op)
                have.add((rx, ry))
        return out

    def solve(prefix_ops, lam, topk, rng, deadline):
        isdot = bytearray(N * N)
        for (x, y) in init_dots:
            isdot[y * N + x] = 1
        used = [[0] * N, [0] * N, [0] * (2 * N - 1), [0] * (2 * N - 1)]

        ops = []
        gain = 0
        for op in prefix_ops:
            rx, ry, qx, qy, px, py, sx, sy = op
            for (ax, ay, bx, by) in ((px, py, qx, qy), (px, py, sx, sy),
                                     (qx, qy, rx, ry), (sx, sy, rx, ry)):
                fam, line, lo, hi = side_key(ax, ay, bx, by)
                used[fam][line] |= side_mask(lo, hi)
            isdot[ry * N + rx] = 1
            gain += W[ry * N + rx]
            ops.append(op)

        nxt = [[-1] * (N * N) for _ in range(8)]
        for d in range(8):
            dx, dy = DX[d], DY[d]
            nd = nxt[d]
            for sx in range(N):
                for sy in range(N):
                    if inside(sx - dx, sy - dy):
                        continue
                    last = -1
                    cx, cy = sx, sy
                    cells = []
                    while inside(cx, cy):
                        cells.append(cy * N + cx)
                        cx += dx; cy += dy
                    for cp in reversed(cells):
                        nd[cp] = last
                        if isdot[cp]:
                            last = cp

        def try_candidate(p, d1, d2):
            px, py = p % N, p // N
            q = nxt[d1][p]
            if q < 0:
                return None
            s = nxt[d2][p]
            if s < 0:
                return None
            qx, qy = q % N, q // N
            sx, sy = s % N, s // N
            rx, ry = qx + sx - px, qy + sy - py
            if not inside(rx, ry):
                return None
            rp = ry * N + rx
            if isdot[rp]:
                return None
            f = nxt[d2][q]
            if f >= 0:
                fx, fy = f % N, f // N
                if abs(fx - qx) <= abs(rx - qx) and abs(fy - qy) <= abs(ry - qy):
                    return None
            f = nxt[d1][s]
            if f >= 0:
                fx, fy = f % N, f // N
                if abs(fx - sx) <= abs(rx - sx) and abs(fy - sy) <= abs(ry - sy):
                    return None
            for (ax, ay, bx, by) in ((px, py, qx, qy), (px, py, sx, sy),
                                     (qx, qy, rx, ry), (sx, sy, rx, ry)):
                fam, line, lo, hi = side_key(ax, ay, bx, by)
                if used[fam][line] & side_mask(lo, hi):
                    return None
            dist = abs(qx - px) + abs(sx - px) + abs(qy - py) + abs(sy - py)
            return (rp, q, s, dist)

        heap = []

        def push_from(p):
            for (d1, d2) in PAIRS:
                r = try_candidate(p, d1, d2)
                if r:
                    pri = -(W[r[0]] * 64 - int(lam * r[3] * 64))
                    heapq.heappush(heap, (pri, r[0], p, d1, d2))

        for i in range(N * N):
            if isdot[i]:
                push_from(i)

        cnt = 0
        while heap:
            cnt += 1
            if cnt & 1023 == 0 and time.time() > deadline:
                return ops, gain
            picked = heapq.heappop(heap)
            stash = []
            for _ in range(topk - 1):
                if not heap:
                    break
                e = heapq.heappop(heap)
                if rng.random() < 1.0 / (len(stash) + 2):
                    stash.append(picked)
                    picked = e
                else:
                    stash.append(e)
            for e in stash:
                heapq.heappush(heap, e)
            _, rp, p, d1, d2 = picked
            res = try_candidate(p, d1, d2)
            if res is None:
                continue
            rp2, q, s, dist = res
            if rp2 != rp or isdot[rp]:
                push_from(p)
                continue
            px, py = p % N, p // N
            rx, ry = rp % N, rp // N
            qx, qy = q % N, q // N
            sx, sy = s % N, s // N
            for (ax, ay, bx, by) in ((px, py, qx, qy), (px, py, sx, sy),
                                     (qx, qy, rx, ry), (sx, sy, rx, ry)):
                fam, line, lo, hi = side_key(ax, ay, bx, by)
                used[fam][line] |= side_mask(lo, hi)
            isdot[rp] = 1
            gain += W[rp]
            ops.append((rx, ry, qx, qy, px, py, sx, sy))
            affected = [rp]
            for d in range(8):
                dx, dy = DX[d], DY[d]
                cx, cy = rx - dx, ry - dy
                pred = -1
                while inside(cx, cy):
                    cp = cy * N + cx
                    if isdot[cp]:
                        pred = cp
                        break
                    cx -= dx; cy -= dy
                cx2, cy2 = rx + dx, ry + dy
                fwd = -1
                while inside(cx2, cy2):
                    cp = cy2 * N + cx2
                    if isdot[cp]:
                        fwd = cp
                        break
                    cx2 += dx; cy2 += dy
                nxt[d][rp] = fwd
                if pred >= 0:
                    nxt[d][pred] = rp
                    affected.append(pred)
            for a in affected:
                push_from(a)
        return ops, gain

    rng = random.Random(12345)
    deadline = t0 + LIMIT
    phase1_end = t0 + LIMIT * 0.5
    best_ops, best_gain = solve([], 0.5, 1, rng, deadline)
    elites = [(best_gain, best_ops)]

    def add_elite(gain, ops):
        # keep pool of up to 4 solutions with differing dot sets
        sig = frozenset((op[0], op[1]) for op in ops)
        for (g, e) in elites:
            esig = frozenset((op[0], op[1]) for op in e)
            if sig == esig:
                if gain > g:
                    elites.remove((g, e))
                    elites.append((gain, ops))
                return
        elites.append((gain, ops))
        elites.sort(key=lambda t: -t[0])
        del elites[4:]

    i = 0
    while time.time() < deadline:
        i += 1
        r = rng.random()
        if time.time() < phase1_end or r < 0.12:
            lam = rng.choice([0.0, 0.25, 0.5, 0.75, 1.0]) if rng.random() < 0.7 else rng.uniform(-0.3, 1.5)
            topk = rng.choice([1, 2, 3, 4, 6, 10])
            ops, gain = solve([], lam, topk, rng, deadline)
        else:
            base = rng.choice(elites)[1]
            L = len(base)
            if r < 0.5:
                k = max(1, int(L * rng.uniform(0.05, 0.6)))
                prefix = base[:L - k]
            elif r < 0.8:
                rs = rng.randint(N // 6, N // 2)
                cx0 = rng.randint(0, N - rs)
                cy0 = rng.randint(0, N - rs)
                prefix = clean_prefix([op for op in base
                          if not (cx0 <= op[0] < cx0 + rs and cy0 <= op[1] < cy0 + rs)])
            else:
                rs = rng.randint(N // 8, N // 4)
                rem = [(rng.randint(0, N - rs), rng.randint(0, N - rs)) for _ in range(2)]
                prefix = clean_prefix([op for op in base
                          if not any(cx0 <= op[0] < cx0 + rs and cy0 <= op[1] < cy0 + rs
                                     for (cx0, cy0) in rem)])
            lam = rng.uniform(-0.2, 1.0)
            topk = rng.choice([1, 2, 3, 4, 6])
            ops, gain = solve(prefix, lam, topk, rng, deadline)
        if gain > best_gain:
            best_gain = gain
            best_ops = ops
        if ops:
            add_elite(gain, ops)
        if i > 600:
            break

    out = [str(len(best_ops))]
    for (rx, ry, qx, qy, px, py, sx, sy) in best_ops:
        out.append(f"{rx} {ry} {qx} {qy} {px} {py} {sx} {sy}")
    sys.stdout.write("\n".join(out) + "\n")

main()
