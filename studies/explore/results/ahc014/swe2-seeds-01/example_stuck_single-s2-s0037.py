import sys
import time
import heapq
import random

def main():
    data = sys.stdin.read().split()
    t0 = time.time()
    it = iter(data)
    N = int(next(it)); M = int(next(it))
    init = []
    for _ in range(M):
        x = int(next(it)); y = int(next(it))
        init.append((x, y))

    c = (N - 1) / 2.0
    W = [0.0] * (N * N)
    for x in range(N):
        for y in range(N):
            W[x * N + y] = (x - c) * (x - c) + (y - c) * (y - c) + 1.0

    pairs = [(a, b) for i, a in enumerate(init) for b in init[i + 1:]]

    def edge_id(x, y, nx, ny):
        dx = nx - x; dy = ny - y
        if dy == 0:
            return ((x if x < nx else nx) * N + y)
        if dx == 0:
            return N * N + (x * N + (y if y < ny else ny))
        if dx == dy:
            sx, sy = (x, y) if x < nx else (nx, ny)
            return 2 * N * N + sx * N + sy
        sx, sy = (x, y) if x < nx else (nx, ny)
        return 3 * N * N + sx * N + sy

    # each op stored as (coords8, edges); returns (ops, gain)
    def run(mode, noise, deadline, seed, prefix=None):
        dots = bytearray(N * N)
        for (x, y) in init:
            dots[x * N + y] = 1
        used = bytearray(4 * N * N)
        rnd = random.Random(seed)

        def check(corners):
            empty = -1
            for i in range(4):
                x, y = corners[2 * i], corners[2 * i + 1]
                if not (0 <= x < N and 0 <= y < N):
                    return None
                if not dots[x * N + y]:
                    if empty != -1:
                        return None
                    empty = i
            if empty == -1:
                return None
            edges = []
            for i in range(4):
                x = corners[2 * i]; y = corners[2 * i + 1]
                j = (i + 1) & 3
                x2 = corners[2 * j]; y2 = corners[2 * j + 1]
                dx = x2 - x; dy = y2 - y
                if dx == 0 and dy == 0:
                    return None
                if not (dx == 0 or dy == 0 or dx == dy or dx == -dy):
                    return None
                sx = (dx > 0) - (dx < 0); sy = (dy > 0) - (dy < 0)
                n = abs(dx) if dx else abs(dy)
                cx, cy = x, y
                for k in range(n):
                    nx = cx + sx; ny = cy + sy
                    e = edge_id(cx, cy, nx, ny)
                    if used[e]:
                        return None
                    edges.append(e)
                    if k + 1 < n and dots[nx * N + ny]:
                        return None
                    cx, cy = nx, ny
            return edges, empty

        def rects(a, b):
            x1, y1 = a; x2, y2 = b
            dx = x2 - x1; dy = y2 - y1
            if x1 != x2 and y1 != y2:
                yield (x1, y1, x2, y1, x2, y2, x1, y2)
            elif x1 == x2:
                if dy % 2 == 0:
                    hh = dy // 2; my = y1 + hh
                    yield (x1, y1, x1 + hh, my, x2, y2, x1 - hh, my)
            else:
                if dx % 2 == 0:
                    hh = dx // 2; mx = x1 + hh
                    yield (x1, y1, mx, y1 + hh, x2, y2, mx, y1 - hh)

        heap = []
        seen = set()
        dot_list = list(init)
        ops = []
        gain = 0.0

        if prefix:
            for coords, edges in prefix:
                nx_, ny_ = coords[0], coords[1]
                for e in edges:
                    used[e] = 1
                dots[nx_ * N + ny_] = 1
                gain += W[nx_ * N + ny_]
                dot_list.append((nx_, ny_))
            ops = list(prefix)

        def push(a, b):
            for cn in rects(a, b):
                key = (cn[0] * N + cn[1], cn[2] * N + cn[3],
                       cn[4] * N + cn[5], cn[6] * N + cn[7])
                key = tuple(sorted(key))
                if key in seen:
                    continue
                seen.add(key)
                r = check(cn)
                if r is None:
                    continue
                edges, ei = r
                nx_ = cn[2 * ei]; ny_ = cn[2 * ei + 1]
                w = W[nx_ * N + ny_]
                heapq.heappush(heap, (-w + w * noise * rnd.random(), key, cn))

        if prefix:
            for i in range(len(dot_list)):
                for j in range(i + 1, len(dot_list)):
                    push(dot_list[i], dot_list[j])
        else:
            for a, b in pairs:
                push(a, b)

        cnt = 0
        stash = []
        while heap or stash:
            cnt += 1
            if cnt & 63 == 0 and time.time() > deadline:
                return ops, gain
            if not heap:
                heapq.heappush(heap, stash.pop())
            it = heapq.heappop(heap)
            if mode == 1 and heap and rnd.random() < noise:
                stash.append(it)
                it = heapq.heappop(heap)
            while stash and len(heap) > 4 and rnd.random() < 0.3:
                heapq.heappush(heap, stash.pop())
            cn = it[2]
            r = check(cn)
            if r is None:
                continue
            edges, ei = r
            nx_ = cn[2 * ei]; ny_ = cn[2 * ei + 1]
            dots[nx_ * N + ny_] = 1
            gain += W[nx_ * N + ny_]
            for e in edges:
                used[e] = 1
            j1 = (ei + 1) & 3; j2 = (ei + 2) & 3; j3 = (ei + 3) & 3
            ops.append(((nx_, ny_, cn[2 * j1], cn[2 * j1 + 1],
                         cn[2 * j2], cn[2 * j2 + 1],
                         cn[2 * j3], cn[2 * j3 + 1]), edges))
            nd = (nx_, ny_)
            for q in dot_list:
                push(nd, q)
            dot_list.append(nd)
        return ops, gain

    deadline = t0 + 2.85
    best, best_gain = run(0, 0.0, deadline, 0)
    second = None
    configs = [
        (0, 0.02), (0, 0.05), (0, 0.1), (0, 0.2), (0, 0.4), (0, 0.8),
        (1, 0.1), (1, 0.2), (1, 0.35), (1, 0.5),
    ]
    keeps = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]
    lns_modes = [(0, 0.1), (0, 0.15), (0, 0.25), (1, 0.15), (1, 0.3)]
    i = 0
    while time.time() < deadline - 0.2:
        if best and i % 3 == 2:
            keep = max(1, int(len(best) * keeps[i % len(keeps)]))
            lm, ln = lns_modes[i % len(lns_modes)]
            ops, gain = run(lm, ln, deadline, 5000 + i, prefix=best[:keep])
        elif second is not None and i % 7 == 5:
            keep = max(1, int(len(second) * 0.6))
            ops, gain = run(0, 0.15, deadline, 7000 + i, prefix=second[:keep])
        else:
            mode, noise = configs[i % len(configs)]
            ops, gain = run(mode, noise, deadline, 1000 + i)
        i += 1
        if ops is not None and gain > best_gain:
            second, best = best, ops
            best_gain = gain
        elif ops is not None and (second is None or gain > (sum(W[p[0][0]*N+p[0][1]] for p in second))):
            second = ops

    out = [str(len(best))]
    for coords, _ in best:
        out.append(' '.join(map(str, coords)))
    sys.stdout.write('\n'.join(out) + '\n')

main()
