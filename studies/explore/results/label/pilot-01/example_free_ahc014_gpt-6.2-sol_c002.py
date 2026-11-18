import sys
import time
import random
import heapq


def main():
    start = time.perf_counter()
    deadline = start + 2.89
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        print(0)
        return
    n, m = data[:2]
    size = n * n
    init = [data[i] + n * data[i + 1] for i in range(2, 2 + 2 * m, 2)]
    x = [p % n for p in range(size)]
    y = [p // n for p in range(size)]
    center = n // 2
    w = [(x[p] - center) ** 2 + (y[p] - center) ** 2 + 1
         for p in range(size)]
    lines = (
        y, [n + v for v in x],
        [3 * n - 1 + x[p] - y[p] for p in range(size)],
        [4 * n - 1 + x[p] + y[p] for p in range(size)]
    )
    # Horizontal positions use x; all other directions use y.
    bits = [1 << k for k in range(n)]
    bx = [bits[v] for v in x]
    by = [bits[v] for v in y]
    posbits = (bx, by, by, by)
    lower = [b - 1 for b in bits]
    higher = [-2 * b for b in bits]
    strides = (1, n, n + 1, n - 1)
    nlines = 6 * n - 2
    rng = random.Random(645821)
    rand = rng.random
    push, pop = heapq.heappush, heapq.heappop
    initial_dots = [0] * nlines
    initial_occ = bytearray(size)
    for p in init:
        initial_occ[p] = 1
        initial_dots[lines[0][p]] |= bx[p]
        initial_dots[lines[1][p]] |= by[p]
        initial_dots[lines[2][p]] |= by[p]
        initial_dots[lines[3][p]] |= by[p]

    def grow(keep, banned, alpha, radial, noise, diag, direct):
        dots = initial_dots.copy()
        occ = initial_occ[:]
        edges = [0] * nlines
        points = init.copy()
        solution = keep.copy()
        score = 0
        heap = []

        for p, b, a, c, l0, e0, l1, e1, l2, e2, l3, e3 in keep:
            occ[p] = 1
            points.append(p)
            score += w[p]
            pb = by[p]
            dots[lines[0][p]] |= bx[p]
            dots[lines[1][p]] |= pb
            dots[lines[2][p]] |= pb
            dots[lines[3][p]] |= pb
            edges[l0] |= e0
            edges[l1] |= e1
            edges[l2] |= e2
            edges[l3] |= e3

        base = n * n * radial
        reward = [base + v for v in w]
        length_factor = [0.0] + [(k + 0.35) ** (-alpha) for k in range(1, 2 * n)]
        minweight = max(1, n * n // 100)
        blocked = []
        adj = [None] * size

        def neighbors(a, d):
            z = x[a] if d == 0 else y[a]
            line = lines[d][a]
            mask = dots[line]
            edge = edges[line]
            bit = bits[z]
            stride = strides[d]
            ans = []
            lo = mask & lower[z]
            if lo:
                q = lo.bit_length() - 1
                e = bit - bits[q]
                if not edge & e:
                    ans.append((a + (q - z) * stride, e))
            hi = mask & higher[z]
            if hi:
                lb = hi & -hi
                e = lb - bit
                if not edge & e:
                    ans.append((a + (lb.bit_length() - 1 - z) * stride, e))
            return ans

        def emit(a, b, c, i, j, e0, e1):
            p = b + c - a
            if p < 0 or p >= size or occ[p]:
                return
            xx = x[b] + x[c] - x[a]
            if xx < 0 or xx >= n:
                return
            li, lj = lines[i], lines[j]
            bi = posbits[i]
            e2 = abs(bi[p] - bi[c])
            e3 = abs(by[p] - by[b])
            l2 = li[c]
            l3 = lj[b]
            if edges[l2] & e2 or edges[l3] & e3:
                return
            if dots[l2] & (e2 & (e2 - 1)) or dots[l3] & (e3 & (e3 - 1)):
                return
            rect = (p, b, a, c, li[a], e0, lj[a], e1, l2, e2, l3, e3)
            length = abs(y[c] - y[a]) + (
                abs(x[b] - x[a]) if i == 0 else abs(y[b] - y[a]))
            value = reward[p] * length_factor[length]
            if i:
                value *= diag
            # Prefer moves that take a useful step beyond their supporting corner.
            value *= 1.0 + direct * (w[p] - w[a]) / (minweight + w[p] + w[a])
            value *= 1.0 - noise * rand()
            item = (-value, rect)
            if (p, a) in banned:
                blocked.append(item)
            else:
                push(heap, item)

        for a in points:
            for i, j in ((0, 1), (2, 3)):
                bs = neighbors(a, i)
                if not bs:
                    continue
                cs = neighbors(a, j)
                for b, e0 in bs:
                    for c, e1 in cs:
                        emit(a, b, c, i, j, e0, e1)

        steps = 0
        released = False
        while True:
            if not heap:
                if released or not blocked:
                    break
                heap = blocked
                blocked = []
                heapq.heapify(heap)
                released = True
            _, rect = pop(heap)
            steps += 1
            if steps & 63 == 0 and time.perf_counter() >= deadline:
                break
            p, b, a, c, l0, e0, l1, e1, l2, e2, l3, e3 = rect
            if occ[p] or (
                (edges[l0] & e0) or (edges[l1] & e1) or
                (edges[l2] & e2) or (edges[l3] & e3) or
                (dots[l0] & (e0 & (e0 - 1))) or
                (dots[l1] & (e1 & (e1 - 1))) or
                (dots[l2] & (e2 & (e2 - 1))) or
                (dots[l3] & (e3 & (e3 - 1)))
            ):
                continue
            solution.append(rect)
            score += w[p]
            occ[p] = 1
            pb = by[p]
            dots[lines[0][p]] |= bx[p]
            dots[lines[1][p]] |= pb
            dots[lines[2][p]] |= pb
            dots[lines[3][p]] |= pb
            edges[l0] |= e0
            edges[l1] |= e1
            edges[l2] |= e2
            edges[l3] |= e3
            if released and banned:
                banned = ()
            # Only rectangles using p as a supporting vertex can become legal.
            for i, j in ((0, 1), (2, 3)):
                bs = neighbors(p, i)
                cs = neighbors(p, j)
                for b, f in bs:
                    for c, g in cs:
                        emit(p, b, c, i, j, f, g)
                    for c, g in neighbors(b, j):
                        emit(b, p, c, i, j, f, g)
                for c, g in cs:
                    for b, f in neighbors(c, i):
                        emit(c, b, p, i, j, f, g)
        return score, solution

    best_score = -1
    best = []
    current = []
    current_score = -1
    elite = []
    phase = 0
    stale = 0
    trials = 0
    randrange = rng.randrange
    while time.perf_counter() < deadline - 0.012:
        elapsed = (time.perf_counter() - start) / (deadline - start)
        restart = trials < 7 or (elapsed < 0.68 and rand() < 0.035)
        banned = set()
        if restart or not current:
            keep = []
        else:
            r = rand()
            if stale >= 38:
                if elite and rand() < 0.53:
                    current_score, current = rng.choice(elite)
                else:
                    current_score, current = best_score, best
                stale = 0
                phase += 1
            parent = best if r < 0.15 else current
            k = len(parent)
            if not k:
                keep = []
            elif r > 0.89 and k > 8:
                cutoff = max(0, k - 2 - int((rand() ** 2) * (k * 0.63)))
                keep = parent[:cutoff]
                for item in parent[cutoff:cutoff + 2]:
                    banned.add((item[0], item[2]))
            else:
                idx = randrange(k)
                if r < 0.39:
                    idx = max(idx, randrange(k))
                pivot = parent[idx][0]
                selected = [idx]
                if r > 0.60:
                    count = 2 + randrange(2 + (6 if phase % 3 == 2 else 3))
                    if r < 0.79:
                        px, py = x[pivot], y[pivot]
                        sample = rng.sample(range(k), min(k, 20 + 3 * count))
                        sample.sort(key=lambda q: abs(x[parent[q][0]] - px)
                                    + abs(y[parent[q][0]] - py))
                        selected.extend(sample[:count - 1])
                    else:
                        selected.extend(rng.sample(range(k), min(k, count - 1)))
                removed = bytearray(size)
                for q in selected:
                    rect = parent[q]
                    removed[rect[0]] = 1
                    banned.add((rect[0], rect[2]))
                if rand() < 0.13:
                    banned.clear()
                keep = []
                for rect in parent:
                    p, b, a, c = rect[:4]
                    if removed[p] or removed[a] or removed[b] or removed[c]:
                        removed[p] = 1
                    else:
                        keep.append(rect)

        alpha = 0.63 + rand() * 1.9
        radial = 0.018 + rand() ** 2 * 0.38
        noise = 0.22 + rand() * 0.63
        diag = 0.77 + rand() * 0.56
        direct = rand() * 0.83 - 0.11
        if trials < 7:
            alpha = (1.7, 2.4, 0.95, 1.6, 1.2, 2.0, 0.8)[trials]
            noise *= 0.66

        score, sol = grow(keep, banned, alpha, radial, noise, diag, direct)
        trials += 1
        if score > best_score:
            best_score, best = score, sol
            current_score, current = score, sol
            stale = 0
        else:
            stale += 1
            temperature = (n * n) * (0.008 + (1 - elapsed) * 0.039)
            if phase % 3 == 1:
                temperature *= 1.55
            if score + temperature * (-__import__('math').log(1.0 - rand())) >= current_score:
                current_score, current = score, sol
        if restart or trials % 15 == 0:
            if all(abs(score - v) > n * n * 0.014 for v, _ in elite):
                elite.append((score, sol))
                elite.sort(key=lambda t: -t[0])
                del elite[7:]

    out = [str(len(best))]
    for rect in best:
        p, b, a, c = rect[:4]
        out.append(f"{x[p]} {y[p]} {x[b]} {y[b]} {x[a]} {y[a]} {x[c]} {y[c]}")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == '__main__':
    main()
