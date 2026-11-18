import sys, time, random

def main():
    t0 = time.time()
    T = 2.7
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        print(0); return
    N, M = data[0], data[1]
    c = (N - 1) / 2.0
    w = [[(x - c) ** 2 + (y - c) ** 2 + 1 for x in range(N)] for y in range(N)]
    NN = N * N
    init = [(data[2 + 2 * i], data[3 + 2 * i]) for i in range(M)]
    NSEG = 4 * NN

    best_ops = []
    best_score = -1.0
    rng = random.Random(12345)

    def run(order, alpha):
        row = [0] * N
        col = [0] * N
        dm1 = [0] * (2 * N - 1)
        dm2 = [0] * (2 * N - 1)
        used = bytearray(NSEG)
        ops = []
        gained = 0.0

        def add(x, y):
            row[y] |= 1 << x
            col[x] |= 1 << y
            dm1[x + y] |= 1 << y
            dm2[x - y + N - 1] |= 1 << y

        for (x, y) in init:
            add(x, y)

        def take(px, py, corners):
            idx = corners.index((px, py))
            cyc = corners[idx:] + corners[:idx]
            ops.append((px, py, cyc[1][0], cyc[1][1], cyc[2][0], cyc[2][1], cyc[3][0], cyc[3][1]))
            add(px, py)

        def cand_axis(px, py, out):
            m = row[py] & ~(1 << px)
            while m and len(out) < 24:
                lb = m & -m; x2 = lb.bit_length() - 1; m ^= lb
                m2 = col[px] & ~(1 << py)
                while m2 and len(out) < 24:
                    lb2 = m2 & -m2; y2 = lb2.bit_length() - 1; m2 ^= lb2
                    if not (row[y2] >> x2) & 1:
                        continue
                    x1, xh = (px, x2) if px < x2 else (x2, px)
                    y1, yh = (py, y2) if py < y2 else (y2, py)
                    bw = xh - x1 - 1
                    if bw > 0:
                        mask = ((1 << bw) - 1) << (x1 + 1)
                        if (row[y1] & mask) or (row[yh] & mask):
                            continue
                    bh = yh - y1 - 1
                    if bh > 0:
                        mask = ((1 << bh) - 1) << (y1 + 1)
                        if (col[x1] & mask) or (col[xh] & mask):
                            continue
                    segs = []
                    ok = True
                    for x in range(x1, xh):
                        b1 = y1 * N + x
                        b2 = yh * N + x
                        if used[b1] or used[b2]:
                            ok = False; break
                        segs.append(b1); segs.append(b2)
                    if not ok:
                        continue
                    base = NN + x1
                    base2 = NN + xh
                    for y in range(y1, yh):
                        s1 = base + y * N
                        s2 = base2 + y * N
                        if used[s1] or used[s2]:
                            ok = False; break
                        segs.append(s1); segs.append(s2)
                    if not ok:
                        continue
                    out.append((segs, [(x1, y1), (xh, y1), (xh, yh), (x1, yh)]))
            return out

        def diag_side(px, py, qx, qy, segs):
            dx = 1 if qx > px else -1
            dy = 1 if qy > py else -1
            d = abs(qx - px)
            if dy == dx:
                off = 2 * NN
                x = px - (1 if dx < 0 else 0)
                y = py - (1 if dx < 0 else 0)
            else:
                off = 3 * NN
                x = px - (1 if dx < 0 else 0)
                y = py - (1 if dx > 0 else 0)
            for i in range(d):
                s = off + y * N + x
                if used[s]:
                    return False
                segs.append(s)
                x += dx; y += dy
            return True

        def cand_diag(px, py, out):
            k2 = px - py + N - 1
            k1 = px + py
            m = dm2[k2] & ~(1 << py)
            while m and len(out) < 24:
                lb = m & -m; y1 = lb.bit_length() - 1; m ^= lb
                x1 = px - py + y1
                if x1 < 0 or x1 >= N:
                    continue
                lo, hi = (py, y1) if py < y1 else (y1, py)
                d = hi - lo - 1
                if d > 0 and dm2[k2] & (((1 << d) - 1) << (lo + 1)):
                    continue
                m2 = dm1[k1] & ~(1 << py)
                while m2 and len(out) < 24:
                    lb2 = m2 & -m2; y3 = lb2.bit_length() - 1; m2 ^= lb2
                    x3 = px + py - y3
                    if x3 < 0 or x3 >= N:
                        continue
                    lo3, hi3 = (py, y3) if py < y3 else (y3, py)
                    d3 = hi3 - lo3 - 1
                    if d3 > 0 and dm1[k1] & (((1 << d3) - 1) << (lo3 + 1)):
                        continue
                    ox = x1 + x3 - px
                    oy = y1 + y3 - py
                    if ox < 0 or ox >= N or oy < 0 or oy >= N or not (row[oy] >> ox) & 1:
                        continue
                    loA, hiA = (y1, oy) if y1 < oy else (oy, y1)
                    dA = hiA - loA - 1
                    if dA > 0 and dm1[x1 + y1] & (((1 << dA) - 1) << (loA + 1)):
                        continue
                    loB, hiB = (y3, oy) if y3 < oy else (oy, y3)
                    dB = hiB - loB - 1
                    if dB > 0 and dm2[x3 - y3 + N - 1] & (((1 << dB) - 1) << (loB + 1)):
                        continue
                    segs = []
                    if diag_side(px, py, x1, y1, segs) and diag_side(px, py, x3, y3, segs) \
                       and diag_side(x1, y1, ox, oy, segs) and diag_side(x3, y3, ox, oy, segs):
                        out.append((segs, [(px, py), (x1, y1), (ox, oy), (x3, y3)]))
            return out

        improved = True
        while improved and time.time() - t0 < T:
            improved = False
            for (px, py) in order:
                if time.time() - t0 > T:
                    break
                if (row[py] >> px) & 1:
                    continue
                cands = []
                if rng.random() < 0.5:
                    cand_axis(px, py, cands)
                    cand_diag(px, py, cands)
                else:
                    cand_diag(px, py, cands)
                    cand_axis(px, py, cands)
                if not cands:
                    continue
                if alpha == 0.0:
                    segs, corners = cands[rng.randrange(len(cands))]
                else:
                    tot = 0.0
                    wts = []
                    for cc in cands:
                        ww = 1.0 / (len(cc[0]) ** alpha)
                        wts.append(ww)
                        tot += ww
                    r = rng.random() * tot
                    acc = 0.0
                    pick = cands[-1]
                    for cc, ww in zip(cands, wts):
                        acc += ww
                        if acc >= r:
                            pick = cc
                            break
                    segs, corners = pick
                for s in segs:
                    used[s] = 1
                take(px, py, corners)
                gained += w[py][px]
                improved = True
        return ops, gained

    init_set = set(init)
    empties = [(x, y) for x in range(N) for y in range(N) if (x, y) not in init_set]
    trial = 0
    while time.time() - t0 < T - 0.12:
        if trial == 0:
            order = sorted(empties, key=lambda p: -w[p[1]][p[0]])
            alpha = 0.0
        else:
            order = sorted(empties, key=lambda p: -(w[p[1]][p[0]] * (0.5 + rng.random())))
            alpha = rng.choice((0.0, 0.5, 1.0))
        ops, gained = run(order, alpha)
        if gained > best_score:
            best_score = gained
            best_ops = ops
        trial += 1

    out = [str(len(best_ops))]
    out += [" ".join(map(str, o)) for o in best_ops]
    sys.stdout.write("\n".join(out) + "\n")

main()
