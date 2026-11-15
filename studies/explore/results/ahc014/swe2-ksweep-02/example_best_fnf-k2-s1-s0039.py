import sys
from bisect import bisect_left, insort
from collections import deque
from time import perf_counter
from random import Random
from math import atan2


def main():
    t0 = perf_counter()
    data = sys.stdin.buffer.read().split()
    it = iter(data)
    N = int(next(it)); M = int(next(it))
    init = [(int(next(it)), int(next(it))) for _ in range(M)]
    c = (N - 1) / 2.0
    flat_w = [(x - c) ** 2 + (y - c) ** 2 for y in range(N) for x in range(N)]
    rng = Random(31337)
    TL = 2.85
    NN = N * N

    def solve(order, deadline, eps, prefix=None):
        dot = bytearray(NN)
        rows = [[] for _ in range(N)]
        cols = [[] for _ in range(N)]
        ndiag = 2 * N - 1
        diag = [[] for _ in range(ndiag)]
        anti = [[] for _ in range(ndiag)]
        for x, y in init:
            dot[y * N + x] = 1
            insort(rows[y], x)
            insort(cols[x], y)
            insort(diag[x + y], x)
            insort(anti[x - y + N - 1], x)
        vrow = [0] * N
        vcol = [0] * N
        vdg = [0] * ndiag
        van = [0] * ndiag
        gver = [1]
        lastchk = [0] * NN
        used = [bytearray(NN) for _ in range(4)]
        ops = []
        placed_seq = []
        score = 0.0

        def side_ok(x1, y1, x2, y2):
            dx = x2 - x1; dy = y2 - y1
            if dx == 0:
                d = 2; ux, uy = 0, 1; L = dy if dy > 0 else -dy
                sx, sy = (x1, y1) if dy > 0 else (x1, y2)
            elif dy == 0:
                d = 0; ux, uy = 1, 0; L = dx if dx > 0 else -dx
                sx, sy = (x1, y1) if dx > 0 else (x2, y1)
            elif (dx > 0) == (dy > 0):
                d = 1; ux, uy = 1, 1; L = dx if dx > 0 else -dx
                sx, sy = (x1, y1) if dx > 0 else (x2, y2)
            else:
                d = 3; ux, uy = 1, -1; L = dx if dx > 0 else -dx
                sx, sy = (x1, y1) if dx > 0 else (x2, y2)
            u = used[d]
            x, y = sx, sy
            for i in range(L):
                if u[y * N + x] or (i and dot[y * N + x]):
                    return None
                x += ux; y += uy
            return (d, sx, sy, ux, uy, L)

        def use_side(s):
            d, sx, sy, ux, uy, L = s
            u = used[d]
            x, y = sx, sy
            for _ in range(L):
                u[y * N + x] = 1
                x += ux; y += uy

        def place(x, y, ax, ay, bx, by, cx_, cy_):
            for s in (side_ok(x, y, ax, ay), side_ok(ax, ay, bx, by),
                      side_ok(bx, by, cx_, cy_), side_ok(cx_, cy_, x, y)):
                use_side(s)
            idx = y * N + x
            dot[idx] = 1
            insort(rows[y], x)
            insort(cols[x], y)
            insort(diag[x + y], x)
            insort(anti[x - y + N - 1], x)
            gver[0] += 1
            v = gver[0]
            vrow[y] = v; vcol[x] = v
            vdg[x + y] = v; van[x - y + N - 1] = v
            ops.append((x, y, ax, ay, bx, by, cx_, cy_))
            placed_seq.append((x, y))
            return flat_w[idx]

        if prefix:
            for (x, y, ax, ay, bx, by, cx_, cy_) in prefix:
                score += place(x, y, ax, ay, bx, by, cx_, cy_)

        def cands_at(x, y, out):
            rl = rows[y]
            i = bisect_left(rl, x)
            cl = cols[x]
            j = bisect_left(cl, y)
            for i2 in (i - 1, i):
                if 0 <= i2 < len(rl):
                    x2 = rl[i2]
                    for j2 in (j - 1, j):
                        if 0 <= j2 < len(cl):
                            y2 = cl[j2]
                            if not dot[y2 * N + x2]:
                                continue
                            s1 = side_ok(x, y, x2, y)
                            s2 = s1 and side_ok(x2, y, x2, y2)
                            s3 = s2 and side_ok(x, y2, x2, y2)
                            s4 = s3 and side_ok(x, y, x, y2)
                            if s4:
                                per = abs(x2 - x) + abs(y2 - y)
                                out.append((per, 0, (x2, y), (x2, y2), (x, y2), (s1, s2, s3, s4)))
            dl_ = diag[x + y]
            i = bisect_left(dl_, x)
            an = anti[x - y + N - 1]
            j = bisect_left(an, x)
            sxy = x + y; dxy = x - y
            for i2 in (i - 1, i):
                if 0 <= i2 < len(dl_):
                    a = dl_[i2]
                    p2x, p2y = a, sxy - a
                    for j2 in (j - 1, j):
                        if 0 <= j2 < len(an):
                            b = an[j2]
                            p4x, p4y = b, b - dxy
                            p3x = p2x + p4x - x
                            p3y = p2y + p4y - y
                            if not (0 <= p3x < N and 0 <= p3y < N) or not dot[p3y * N + p3x]:
                                continue
                            s1 = side_ok(x, y, p2x, p2y)
                            s2 = s1 and side_ok(p2x, p2y, p3x, p3y)
                            s3 = s2 and side_ok(p4x, p4y, p3x, p3y)
                            s4 = s3 and side_ok(x, y, p4x, p4y)
                            if s4:
                                per = abs(p2x - x) + abs(p4x - x)
                                out.append((per, 1, (p2x, p2y), (p3x, p3y), (p4x, p4y), (s1, s2, s3, s4)))

        improved = True
        while improved and perf_counter() - t0 < deadline:
            improved = False
            for (x, y) in order:
                idx = y * N + x
                if dot[idx]:
                    continue
                lc = lastchk[idx]
                if lc and not (vrow[y] > lc or vcol[x] > lc or
                               vdg[x + y] > lc or van[x - y + N - 1] > lc):
                    continue
                cands = []
                cands_at(x, y, cands)
                gver[0] += 1
                lastchk[idx] = gver[0]
                if not cands:
                    continue
                if len(cands) > 1:
                    cands.sort(key=lambda t: t[:2])
                    if rng.random() < eps:
                        k = min(len(cands), 3)
                        pick = cands[rng.randrange(k)]
                    else:
                        pick = cands[0]
                else:
                    pick = cands[0]
                per, tilt, (ax, ay), (bx, by), (cx_, cy_), sides = pick
                for s in sides:
                    use_side(s)
                dot[idx] = 1
                insort(rows[y], x)
                insort(cols[x], y)
                insort(diag[x + y], x)
                insort(anti[x - y + N - 1], x)
                gver[0] += 1
                v = gver[0]
                vrow[y] = v; vcol[x] = v
                vdg[x + y] = v; van[x - y + N - 1] = v
                ops.append((x, y, ax, ay, bx, by, cx_, cy_))
                placed_seq.append((x, y))
                score += flat_w[idx]
                improved = True
        return score, ops, placed_seq

    initset = set(init)
    base = [(x, y) for y in range(N) for x in range(N) if (x, y) not in initset]
    wdesc = sorted(base, key=lambda p: -flat_w[p[1] * N + p[0]])

    dist = [NN] * NN
    dq = deque()
    for x, y in init:
        dist[y * N + x] = 0
        dq.append((x, y))
    while dq:
        x, y = dq.popleft()
        nd = dist[y * N + x] + 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and dist[ny * N + nx] > nd:
                dist[ny * N + nx] = nd
                dq.append((nx, ny))

    drow = [[] for _ in range(N)]
    dcol = [[] for _ in range(N)]
    ddg = {}
    dan = {}
    for x, y in init:
        insort(drow[y], x)
        insort(dcol[x], y)
        insort(ddg.setdefault(x + y, []), x)
        insort(dan.setdefault(x - y, []), x)

    def init_difficulty(x, y):
        cnt = 0
        rl = drow[y]
        i = bisect_left(rl, x)
        cnt += (i > 0) + (i < len(rl))
        cl = dcol[x]
        j = bisect_left(cl, y)
        cnt += (j > 0) + (j < len(cl))
        dl_ = ddg.get(x + y, ())
        i = bisect_left(dl_, x)
        cnt += (i > 0) + (i < len(dl_))
        an = dan.get(x - y, ())
        j = bisect_left(an, x)
        cnt += (j > 0) + (j < len(an))
        return cnt

    diff = {p: init_difficulty(*p) for p in base}

    def perturb(order, strength):
        o = list(order)
        nsw = 1 + int(strength * len(o) * rng.random())
        for _ in range(nsw):
            i = rng.randrange(len(o)); j = rng.randrange(len(o))
            o[i], o[j] = o[j], o[i]
        r = rng.random()
        if r < 0.3:
            k = rng.randrange(len(o))
            o = o[k:] + o[:k]
        elif r < 0.45:
            i = rng.randrange(len(o))
            j = min(len(o), i + 8 + rng.randrange(len(o) // 4 + 1))
            o[i:j] = reversed(o[i:j])
        return o

    def random_order():
        order = list(base)
        kind = rng.randrange(8)
        if kind == 0:
            scale = rng.choice((0.25, 0.5, 1.0, 2.0, 4.0))
            order.sort(key=lambda p: -(flat_w[p[1] * N + p[0]] *
                                       (1.0 - scale + 2 * scale * rng.random())))
        elif kind == 1:
            order.sort(key=lambda p: flat_w[p[1] * N + p[0]])
        elif kind == 2:
            a0 = rng.random() * 6.2832
            order.sort(key=lambda p: atan2(p[1] - c, p[0] - c) - a0)
        elif kind == 3:
            order.sort(key=lambda p: (diff[p], -flat_w[p[1] * N + p[0]]))
        elif kind == 4:
            order.sort(key=lambda p: -flat_w[p[1] * N + p[0]] * rng.uniform(0.5, 1.5))
        elif kind == 5:
            order.sort(key=lambda p: (dist[p[1] * N + p[0]],
                                      -flat_w[p[1] * N + p[0]]))
        elif kind == 6:
            order.sort(key=lambda p: (dist[p[1] * N + p[0]], diff[p],
                                      -flat_w[p[1] * N + p[0]]))
        else:
            rng.shuffle(order)
        return order

    best_score = -1.0
    best_ops = []
    best_order = None
    pool = []
    incumbent = None
    inc_score = -1.0
    seed_orders = [
        wdesc,
        sorted(base, key=lambda p: flat_w[p[1] * N + p[0]]),
        sorted(base, key=lambda p: (diff[p], -flat_w[p[1] * N + p[0]])),
        sorted(base, key=lambda p: (dist[p[1] * N + p[0]],
                                    -flat_w[p[1] * N + p[0]])),
        sorted(base, key=lambda p: (dist[p[1] * N + p[0]], diff[p],
                                    -flat_w[p[1] * N + p[0]])),
        sorted(base, key=lambda p: (-dist[p[1] * N + p[0]],
                                    -flat_w[p[1] * N + p[0]])),
        sorted(base, key=lambda p: (-diff[p], -flat_w[p[1] * N + p[0]])),
    ]
    seed_eps = [0.0, 0.0, 0.0, 0.1, 0.1, 0.2, 0.1]
    trial = 0
    while perf_counter() - t0 < TL * 0.75:
        if trial < len(seed_orders):
            order = seed_orders[trial]
            eps = seed_eps[trial]
        elif incumbent is not None and rng.random() < 0.55:
            order = perturb(incumbent, rng.choice((0.02, 0.05, 0.1, 0.2)))
            eps = rng.choice((0.0, 0.1, 0.2, 0.35, 0.6))
        elif pool and rng.random() < 0.75:
            sc, seq = pool[rng.randrange(len(pool))]
            pr = {p: i for i, p in enumerate(seq)}
            order = sorted(base, key=lambda p: pr.get(p, len(pr)))
            order = perturb(order, rng.choice((0.05, 0.1, 0.25)))
            eps = rng.choice((0.0, 0.1, 0.25, 0.5))
        else:
            order = random_order()
            eps = rng.random() * 0.6
        s, ops, seq = solve(order, TL, eps)
        if s >= inc_score or rng.random() < 0.1:
            pr = {p: i for i, p in enumerate(seq)}
            incumbent = sorted(base, key=lambda p: pr.get(p, len(pr)))
            inc_score = s
        if s > best_score:
            best_score = s
            best_ops = ops
            pr = {p: i for i, p in enumerate(seq)}
            best_order = sorted(base, key=lambda p: pr.get(p, len(pr)))
            pool.append((s, seq))
            pool.sort(key=lambda t: -t[0])
            pool = pool[:4]
        trial += 1
        if trial >= 400:
            break

    # Final phase: alternate LNS restarts from best-op prefixes and
    # micro-perturbation refinement of the best order
    while best_order is not None and perf_counter() - t0 < TL:
        if best_ops and rng.random() < 0.55:
            k = len(best_ops)
            cut = max(1, int(k * rng.uniform(0.4, 0.9)))
            prefix = best_ops[:cut]
            pset = set(placed[:cut] if False else
                       [(o[0], o[1]) for o in prefix])
            tail = [p for p in best_order if p not in pset]
            order = perturb(tail, rng.choice((0.02, 0.05, 0.1, 0.2)))
            eps = rng.choice((0.0, 0.05, 0.1, 0.2))
            s, ops, seq = solve(order, TL, eps, prefix=prefix)
        else:
            order = perturb(best_order, rng.choice((0.0, 0.01, 0.02, 0.05)))
            eps = rng.choice((0.0, 0.05, 0.1))
            s, ops, seq = solve(order, TL, eps)
        if s > best_score:
            best_score = s
            best_ops = ops
            pr = {p: i for i, p in enumerate(seq)}
            best_order = sorted(base, key=lambda p: pr.get(p, len(pr)))

    res = [str(len(best_ops))]
    res += [' '.join(map(str, o)) for o in best_ops]
    sys.stdout.write('\n'.join(res) + '\n')


main()
