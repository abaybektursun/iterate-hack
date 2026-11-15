import sys, time, heapq, random
from math import gcd, exp

def main():
    t0 = time.time()
    data = sys.stdin.buffer.read().split()
    it = iter(data)
    N = int(next(it)); M = int(next(it))
    c = (N - 1) / 2.0
    w = [[(x - c) ** 2 + (y - c) ** 2 + 1 for y in range(N)] for x in range(N)]
    init = []
    for _ in range(M):
        x = int(next(it)); y = int(next(it))
        init.append((x * N + y))

    rays = [(1,0,(0,1)), (-1,0,(0,1)), (0,1,(1,0)), (0,-1,(1,0)),
            (1,1,(1,-1)), (1,-1,(1,1)), (-1,1,(1,1)), (-1,-1,(1,-1))]
    N2 = N * N
    N4 = N2 * N2
    rng = random.Random(12345)

    def solve(mode, jitter, temp, topk):
        dots = [bytearray(N) for _ in range(N)]
        for pid in init:
            dots[pid // N][pid % N] = 1
        used = set()      # int edge ids
        seen = set()      # int corner keys
        heap = []
        cnt = 0
        ops = []
        gain = 0.0
        stash = []

        def side_edges(a, b):
            ax, ay = a // N, a % N
            bx, by = b // N, b % N
            dx = bx - ax; dy = by - ay
            k = gcd(abs(dx), abs(dy))
            ux = dx // k; uy = dy // k
            x, y = ax, ay
            edges = []
            for i in range(k):
                nx = x + ux; ny = y + uy
                if i < k - 1 and dots[nx][ny]:
                    return None
                i1 = x * N + y; i2 = nx * N + ny
                edges.append(i1 * N2 + i2 if i1 < i2 else i2 * N2 + i1)
                x = nx; y = ny
            for e in edges:
                if e in used:
                    return None
            return edges

        def rect_check(corners):
            edges = []
            for i in range(4):
                r = side_edges(corners[i], corners[(i + 1) % 4])
                if r is None:
                    return None
                edges.extend(r)
            return edges

        def push(corners, newidx, nedges):
            nonlocal cnt
            ids = sorted(corners)
            key = (ids[0] * N2 + ids[1]) * N4 + ids[2] * N2 + ids[3]
            if key in seen:
                return
            seen.add(key)
            np_ = corners[newidx]
            wv = w[np_ // N][np_ % N]
            if mode == 0:
                p = wv
            elif mode == 1:
                p = wv / (nedges + 1)
            else:
                p = wv / ((nedges + 1) ** 0.5)
            if jitter:
                p *= 1.0 + jitter * (rng.random() * 2 - 1)
            cnt += 1
            heapq.heappush(heap, (-p, cnt, corners, newidx))

        def gen(px, py):
            for dx, dy, (ux, uy) in rays:
                a = 0
                while True:
                    a += 1
                    qx = px + a * dx; qy = py + a * dy
                    if not (0 <= qx < N and 0 <= qy < N):
                        break
                    if dots[qx][qy]:
                        q = qx * N + qy
                        for s in (1, -1):
                            vx = ux * s; vy = uy * s
                            b = 0
                            while True:
                                b += 1
                                r1x = px + b * vx; r1y = py + b * vy
                                r2x = qx + b * vx; r2y = qy + b * vy
                                if not (0 <= r1x < N and 0 <= r1y < N and
                                        0 <= r2x < N and 0 <= r2y < N):
                                    break
                                d1 = dots[r1x][r1y]; d2 = dots[r2x][r2y]
                                if d1 == d2:
                                    continue
                                corners = (px * N + py, q, r2x * N + r2y, r1x * N + r1y)
                                newidx = 2 if d1 else 3
                                ed = rect_check(corners)
                                if ed is not None:
                                    push(corners, newidx, len(ed))
                        break

        for pid in init:
            gen(pid // N, pid % N)

        pops = 0
        while heap:
            pops += 1
            if (pops & 255) == 0 and time.time() - t0 > 2.7:
                return None
            if temp > 0:
                stash.clear()
                tries = 0
                while heap and len(stash) < topk and tries < topk * 4:
                    item = heapq.heappop(heap)
                    tries += 1
                    cn = item[2]; ni = item[3]
                    np_ = cn[ni]
                    if dots[np_ // N][np_ % N]:
                        continue
                    stash.append(item)
                if not stash:
                    break
                mx = -stash[0][0]
                if len(stash) == 1 or mx <= 0:
                    idx = 0
                else:
                    logs = [(-it2[0]) / (mx * temp) for it2 in stash]
                    m = max(logs)
                    exps = [exp(l - m) for l in logs]
                    tot = sum(exps)
                    r = rng.random() * tot
                    acc = 0.0
                    idx = 0
                    for i, e in enumerate(exps):
                        acc += e
                        if acc >= r:
                            idx = i
                            break
                chosen = stash.pop(idx)
                for it2 in stash:
                    heapq.heappush(heap, it2)
            else:
                chosen = heapq.heappop(heap)

            _, _, corners, newidx = chosen
            np_ = corners[newidx]
            if dots[np_ // N][np_ % N]:
                continue
            ok = True
            for i in range(4):
                if i != newidx:
                    ci = corners[i]
                    if not dots[ci // N][ci % N]:
                        ok = False
                        break
            if not ok:
                continue
            edges = rect_check(corners)
            if edges is None:
                continue
            for e in edges:
                used.add(e)
            dots[np_ // N][np_ % N] = 1
            gain += w[np_ // N][np_ % N]
            ops.append([corners[(newidx + i) % 4] for i in range(4)])
            gen(np_ // N, np_ % N)
        return gain, ops

    configs = [(0, 0.0, 0.0, 4), (1, 0.0, 0.0, 4), (2, 0.0, 0.0, 4)]
    best = None
    ci = 0
    first = True
    while True:
        if ci < len(configs):
            mode, jit, temp, topk = configs[ci]; ci += 1
        else:
            mode = rng.randrange(3)
            r_ = rng.random()
            if r_ < 0.4:
                jit = rng.choice([0.05, 0.15, 0.4]); temp = 0.0; topk = 4
            elif r_ < 0.85:
                jit = 0.0; temp = rng.choice([0.5, 1.0, 2.0, 4.0]); topk = rng.choice([3, 4, 6])
            else:
                jit = rng.choice([0.05, 0.15]); temp = rng.choice([0.5, 1.0, 2.0]); topk = 4
        if not first and time.time() - t0 > 2.55:
            break
        first = False
        r = solve(mode, jit, temp, topk)
        if r is None:
            break
        if best is None or r[0] > best[0]:
            best = r
        if time.time() - t0 > 2.55:
            break

    ops = best[1] if best else []
    out = [str(len(ops))]
    for o in ops:
        out.append(' '.join(f'{p // N} {p % N}' for p in o))
    sys.stdout.write('\n'.join(out) + '\n')

main()
