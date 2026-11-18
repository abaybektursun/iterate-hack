import sys
import time
import random
import heapq
import math

def main():
    start = time.perf_counter()
    deadline = start + 2.78
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        print(0)
        return
    n, m = data[:2]
    size = n * n
    rng = random.Random(714031)
    initial = [data[2 + 2*i] + n * data[3 + 2*i] for i in range(m)]
    xs = [p % n for p in range(size)]
    ys = [p // n for p in range(size)]
    center = (n - 1) // 2
    weights = [(xs[p]-center)**2 + (ys[p]-center)**2 + 1
               for p in range(size)]
    bits = [1 << i for i in range(n)]
    lowm = [(1 << i)-1 for i in range(n+1)]
    lines = [
        [ys[p] for p in range(size)],
        [n + xs[p] for p in range(size)],
        [3*n-1 + xs[p]-ys[p] for p in range(size)],
        [4*n-1 + xs[p]+ys[p] for p in range(size)]
    ]
    positions = [xs, ys, ys, ys]
    steps = (1, n, n+1, n-1)
    intervals = [[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1, n):
            intervals[a][b] = lowm[b] ^ lowm[a]
            intervals[b][a] = intervals[a][b]

    best = []
    best_score = -1
    trial = 0

    while time.perf_counter() < deadline - 0.045:
        dot = bytearray(size)
        occupied = [0] * (6*n-2)
        used = [0] * (6*n-2)
        operations = []
        score = 0
        heap = []
        seen = set()
        serial = 0

        def put(p):
            dot[p] = 1
            x, y = xs[p], ys[p]
            occupied[y] |= bits[x]
            occupied[n+x] |= bits[y]
            occupied[3*n-1+x-y] |= bits[y]
            occupied[4*n-1+x+y] |= bits[y]

        for p in initial:
            put(p)

        # Keep a dependency-closed part of the incumbent.
        if best and trial % 5 != 0:
            removed = set()
            rate = rng.choice((0.015, 0.025, 0.045, 0.075, 0.12))
            forced = rng.randrange(len(best))
            for i, op in enumerate(best):
                a, c, b, d, edges = op
                if (i == forced or rng.random() < rate or
                        c in removed or b in removed or d in removed):
                    removed.add(a)
                else:
                    put(a)
                    for line, mask in edges:
                        used[line] |= mask
                    operations.append(op)
                    score += weights[a]

        if trial == 0:
            alpha, beta, noise = 1.5, 0.45, 0.12
        else:
            alpha = rng.uniform(1.1, 2.0)
            beta = rng.uniform(0.20, 0.75)
            noise = rng.uniform(0.08, 0.55)
        base_weight = center * center * rng.uniform(0.08, 0.35) + 3
        point_factor = [(w + base_weight) ** (-beta) for w in weights]
        length_factor = [(i + 1.0) ** alpha for i in range(4*n+1)]

        def neighbors(p):
            result = []
            for axis in range(4):
                pos = positions[axis][p]
                line = lines[axis][p]
                mask = occupied[line]
                left = mask & lowm[pos]
                if left:
                    qpos = left.bit_length()-1
                    q = p + (qpos-pos)*steps[axis]
                    result.append(q)
                right = mask >> (pos+1)
                if right:
                    qpos = pos + (right & -right).bit_length()
                    q = p + (qpos-pos)*steps[axis]
                    result.append(q)
            return result

        def generate(b):
            nonlocal serial
            bx, by = xs[b], ys[b]
            ns = [None] * 4
            for axis in range(4):
                pos = positions[axis][b]
                line = lines[axis][b]
                mask = occupied[line]
                opts = []
                left = mask & lowm[pos]
                if left:
                    qpos = left.bit_length()-1
                    edge = intervals[pos][qpos]
                    if not used[line] & edge:
                        opts.append((b + (qpos-pos)*steps[axis],
                                     line, edge, abs(qpos-pos)))
                right = mask >> (pos+1)
                if right:
                    qpos = pos + (right & -right).bit_length()
                    edge = intervals[pos][qpos]
                    if not used[line] & edge:
                        opts.append((b + (qpos-pos)*steps[axis],
                                     line, edge, abs(qpos-pos)))
                ns[axis] = opts

            for u, v in ((0, 1), (2, 3)):
                for c, lc, mc, dc in ns[u]:
                    cx, cy = xs[c], ys[c]
                    for d, ld, md, dd in ns[v]:
                        ax = cx + xs[d] - bx
                        ay = cy + ys[d] - by
                        if ax < 0 or ax >= n or ay < 0 or ay >= n:
                            continue
                        a = ay*n + ax
                        if dot[a]:
                            continue
                        key = a*size + b
                        if key in seen:
                            continue

                        # Opposite edges have the same lengths, translated.
                        shift = (xs[d]-bx) if u == 0 else (ys[d]-by)
                        mcu = (mc << shift) if shift >= 0 else (mc >> -shift)
                        shift = (cx-bx) if v == 0 else (cy-by)
                        mdv = (md << shift) if shift >= 0 else (md >> -shift)
                        lcu = lines[u][d]
                        ldv = lines[v][c]
                        if used[lcu] & mcu or used[ldv] & mdv:
                            continue
                        interior1 = mcu ^ (mcu & -mcu)
                        interior2 = mdv ^ (mdv & -mdv)
                        if occupied[lcu] & interior1 or occupied[ldv] & interior2:
                            continue

                        seen.add(key)
                        edges = ((lc, mc), (ld, md), (lcu, mcu), (ldv, mdv))
                        length = 2*(dc+dd)
                        priority = (length_factor[length] * point_factor[a] *
                                    (1.0 + noise*rng.random()))
                        serial += 1
                        heapq.heappush(heap, (priority, serial, a, c, b, d, edges))

        for p in initial:
            generate(p)
        for op in operations:
            generate(op[0])

        pops = 0
        while heap:
            if pops & 127 == 0 and time.perf_counter() >= deadline:
                break
            pops += 1
            _, _, a, c, b, d, edges = heapq.heappop(heap)
            if dot[a]:
                continue
            valid = True
            for line, mask in edges:
                if used[line] & mask or occupied[line] & (mask ^ (mask & -mask)):
                    valid = False
                    break
            if not valid:
                continue
            put(a)
            for line, mask in edges:
                used[line] |= mask
            operations.append((a, c, b, d, edges))
            score += weights[a]
            generate(a)
            for p in neighbors(a):
                generate(p)

        if score > best_score:
            best_score = score
            best = operations[:]
        trial += 1

    out = [str(len(best))]
    for a, c, b, d, _ in best:
        out.append(f"{xs[a]} {ys[a]} {xs[c]} {ys[c]} "
                   f"{xs[b]} {ys[b]} {xs[d]} {ys[d]}")
    sys.stdout.write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
