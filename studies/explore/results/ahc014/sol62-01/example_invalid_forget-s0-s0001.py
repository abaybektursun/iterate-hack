import sys
import time
import math
import random
import heapq

START = time.perf_counter()
DEADLINE = START + 2.87


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, m = data[:2]
    initial = [x * n + y for x, y in zip(data[2::2], data[3::2])]
    size = n * n
    xs = [p // n for p in range(size)]
    ys = [p % n for p in range(size)]
    c = n // 2
    weights = [(x - c) ** 2 + (y - c) ** 2 + 1 for x, y in zip(xs, ys)]
    norm = 1.0 / (c * c)
    steps = (n, 1, n + 1, n - 1)
    lines = (
        ys,
        [n + x for x in xs],
        [2 * n + y - x + n - 1 for x, y in zip(xs, ys)],
        [4 * n - 1 + x + y for x, y in zip(xs, ys)],
    )
    powers = [1 << (i * 2) for i in range(n)]
    bx = [powers[x] for x in xs]
    by = [powers[y] for y in ys]
    bits = (bx, by, bx, bx)
    rng = random.Random(934607 + sum(initial) * 37 + n)
    rand = rng.random
    clock = time.perf_counter
    push = heapq.heappush
    pop = heapq.heappop

    base_grid = [0] * (6 * n - 2)
    base_used = bytearray(size)
    for p in initial:
        base_used[p] = 1
        for f in range(4):
            base_grid[lines[f][p]] |= bits[f][p]
    base_link = [[-1] * size for _ in range(8)]
    for p in initial:
        for f in range(4):
            bit = bits[f][p]
            obs = base_grid[lines[f][p]]
            hi = obs & -2 * bit
            if hi:
                q = p + (((hi & -hi).bit_length() - bit.bit_length()) // 2) * steps[f]
                base_link[2 * f][p] = q
                base_link[2 * f + 1][q] = p

    def run(prefix, params):
        exponent, radial, offset, noise, diag, shape = params
        grid = base_grid[:]
        used = base_used[:]
        link = [row[:] for row in base_link]
        points = initial[:]
        ops = []
        heap = []
        value = 0
        scale = [(offset + w * norm) ** radial for w in weights]
        dil = [k ** (-exponent) for k in range(2 * n + 1)]
        serial = 0

        def apply(op):
            p, a, b, d, i, j = op
            used[p] = 1
            for f in range(4):
                li = lines[f][p]
                bit = bits[f][p]
                obs = grid[li]
                lo = (obs & (bit - 1)).bit_length()
                upper = obs & (-bit)
                hi = (upper & -upper).bit_length()
                e = 2 * f
                pos = bit.bit_length()
                if lo & 1:
                    q = p - ((pos - lo) // 2) * steps[f]
                    link[e][q] = p
                    link[e + 1][p] = q
                if hi & 1:
                    q = p + ((hi - pos) // 2) * steps[f]
                    link[e + 1][q] = p
                    link[e][p] = q
                grid[li] = obs | bit

            f = i >> 1
            bf = bits[f]
            # Sides b-a and d-p, both oriented in direction i.
            if i & 1:
                grid[lines[f][b]] |= bf[b] - 2 * bf[a]
                grid[lines[f][d]] |= bf[d] - 2 * bf[p]
            else:
                grid[lines[f][b]] |= bf[a] - 2 * bf[b]
                grid[lines[f][d]] |= bf[p] - 2 * bf[d]
            link[i][b] = link[i][d] = -1
            link[i ^ 1][a] = link[i ^ 1][p] = -1

            f = j >> 1
            bf = bits[f]
            # Sides b-d and a-p, both oriented in direction j.
            if j & 1:
                grid[lines[f][b]] |= bf[b] - 2 * bf[d]
                grid[lines[f][a]] |= bf[a] - 2 * bf[p]
            else:
                grid[lines[f][b]] |= bf[d] - 2 * bf[b]
                grid[lines[f][a]] |= bf[p] - 2 * bf[a]
            link[j][b] = link[j][a] = -1
            link[j ^ 1][d] = link[j ^ 1][p] = -1
            points.append(p)
            ops.append(op)

        def add(a, b, d, i, j):
            nonlocal serial
            x = xs[a] + xs[d] - xs[b]
            y = ys[a] + ys[d] - ys[b]
            if not (0 <= x < n and 0 <= y < n):
                return
            p = a + d - b
            if used[p]:
                return
            f = i >> 1
            bf = bits[f]
            if grid[lines[f][d]] & ((bf[d] - 2 * bf[p]) if i & 1 else (bf[p] - 2 * bf[d])):
                return
            f = j >> 1
            bf = bits[f]
            if grid[lines[f][a]] & ((bf[a] - 2 * bf[p]) if j & 1 else (bf[p] - 2 * bf[a])):
                return
            u = abs(xs[a] - xs[b]) if i >> 1 != 1 else abs(ys[a] - ys[b])
            v = abs(xs[d] - xs[b]) if j >> 1 != 1 else abs(ys[d] - ys[b])
            priority = scale[p] * dil[u + v]
            if i >= 4:
                priority *= diag
            if shape:
                priority *= 1.0 + shape * (2 * min(u, v) / (u + v) - 0.5)
            priority *= 1.0 + noise * rand()
            serial += 1
            push(heap, (-priority, serial, p, a, b, d, i, j))

        def center(b):
            for k in (0, 4):
                d0 = link[k + 2][b]
                d1 = link[k + 3][b]
                if d0 < 0 and d1 < 0:
                    continue
                for i in (k, k + 1):
                    a = link[i][b]
                    if a >= 0:
                        if d0 >= 0:
                            add(a, b, d0, i, k + 2)
                        if d1 >= 0:
                            add(a, b, d1, i, k + 3)

        for op in prefix:
            apply(op)
            value += weights[op[0]]
        for b in points:
            center(b)

        checks = 0
        while heap:
            checks += 1
            if checks & 31 == 0 and clock() >= DEADLINE:
                break
            _, _, p, a, b, d, i, j = pop(heap)
            if used[p] or link[i][b] != a or link[j][b] != d:
                continue
            f = i >> 1
            bf = bits[f]
            if grid[lines[f][d]] & ((bf[d] - 2 * bf[p]) if i & 1 else (bf[p] - 2 * bf[d])):
                continue
            f = j >> 1
            bf = bits[f]
            if grid[lines[f][a]] & ((bf[a] - 2 * bf[p]) if j & 1 else (bf[p] - 2 * bf[a])):
                continue
            apply((p, a, b, d, i, j))
            value += weights[p]
            center(p)
            for k in range(8):
                mid = link[k][p]
                if mid < 0:
                    continue
                back = k ^ 1
                side = back ^ 2
                q = link[side][mid]
                if q >= 0:
                    add(p, mid, q, back, side)
                side ^= 1
                q = link[side][mid]
                if q >= 0:
                    add(p, mid, q, back, side)
        return value, ops

    presets = [
        (1.65, 0.85, 0.23, 0.28, 0.91, 0.0),
        (2.55, 0.68, 0.30, 0.38, 1.00, 0.0),
        (1.15, 1.18, 0.19, 0.34, 0.88, 0.0),
        (2.0, 1.35, 0.12, 0.47, 1.05, -0.12),
        (1.65, 0.44, 0.34, 0.53, 0.80, 0.15),
        (0.85, 1.30, 0.18, 0.28, 0.93, 0.0),
    ]

    best = []
    best_score = -1
    elite = []
    iteration = 0
    last_duration = 0.0
    while clock() < DEADLINE - min(0.018, last_duration * 0.18):
        tick = clock()
        prefix = []
        if iteration < len(presets):
            params = presets[iteration]
        elif elite and rand() >= 0.22:
            idx = min(len(elite) - 1, int(rand() ** 2.1 * len(elite)))
            _, _, parent, old = elite[idx]
            r = rand()
            if r < 0.30:
                frac = 0.15 + 0.60 * rand()
            else:
                frac = 0.53 + 0.44 * rand()
            prefix = parent[:int(frac * len(parent))]
            e, r, o, q, g, s = old
            params = (
                max(0.55, e + (rand() - 0.5) * 0.66),
                max(0.12, r + (rand() - 0.5) * 0.55),
                o,
                0.16 + rand() * 0.77,
                max(0.58, min(1.44, g + (rand() - 0.5) * 0.27)),
                max(-0.45, min(0.45, s + (rand() - 0.5) * 0.40)),
            )
        else:
            params = (
                0.80 + rand() * 2.05, 0.25 + rand() * 1.32,
                0.12 + rand() * 0.32, 0.22 + rand() * 0.63,
                0.73 + rand() * 0.46, (rand() - 0.5) * 0.48,
            )
        score, ops = run(prefix, params)
        if score > best_score:
            best_score, best = score, ops
        if not elite or (score >= elite[0][0] * 0.82 and all(score != e[0] for e in elite)):
            elite.append((score, iteration, ops, params))
            elite.sort(reverse=True)
            del elite[7:]
        iteration += 1
        last_duration = clock() - tick

    output = [str(len(best))]
    for p, a, b, d, _, _ in best:
        output.append(f"{xs[p]} {ys[p]} {xs[a]} {ys[a]} {xs[b]} {ys[b]} {xs[d]} {ys[d]}")
    sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
