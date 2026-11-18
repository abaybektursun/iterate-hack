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
    NSEG = 4 * NN
    init = [(data[2 + 2 * i], data[3 + 2 * i]) for i in range(M)]
    init_set = set(init)
    rng = random.Random(99991)

    row = [0] * N
    col = [0] * N
    dm1 = [0] * (2 * N - 1)
    dm2 = [0] * (2 * N - 1)
    used = bytearray(NSEG)
    ops = []
    children = []
    active = []
    owner = [[-1] * N for _ in range(N)]
    cur = [0.0]

    def add_dot(x, y):
        row[y] |= 1 << x
        col[x] |= 1 << y
        dm1[x + y] |= 1 << y
        dm2[x - y + N - 1] |= 1 << y

    def del_dot(x, y):
        row[y] &= ~(1 << x)
        col[x] &= ~(1 << y)
        dm1[x + y] &= ~(1 << y)
        dm2[x - y + N - 1] &= ~(1 << y)

    def reset_state():
        for i in range(N):
            row[i] = 0; col[i] = 0
        for i in range(2 * N - 1):
            dm1[i] = 0; dm2[i] = 0
        for i in range(NSEG):
            used[i] = 0
        ops.clear(); children.clear(); active.clear()
        for y in range(N):
            for x in range(N):
                owner[y][x] = -1
        cur[0] = 0.0
        for (x, y) in init:
            add_dot(x, y)

    def add_rect(px, py, corners, segs):
        oid = len(ops)
        ops.append((px, py, corners, segs))
        children.append([])
        active.append(True)
        for s in segs:
            used[s] = 1
        for (cx, cy) in corners[1:]:
            o = owner[cy][cx]
            if o >= 0:
                children[o].append(oid)
        owner[py][px] = oid
        add_dot(px, py)
        cur[0] += w[py][px]

    def remove_op(oid):
        stack = [oid]
        while stack:
            i = stack.pop()
            if not active[i]:
                continue
            active[i] = False
            px, py, corners, segs = ops[i]
            for s in segs:
                used[s] = 0
            owner[py][px] = -1
            del_dot(px, py)
            cur[0] -= w[py][px]
            for ch in children[i]:
                if active[ch]:
                    stack.append(ch)

    def cand_axis(px, py, out):
        m = row[py] & ~(1 << px)
        while m and len(out) < 20:
            lb = m & -m; x2 = lb.bit_length() - 1; m ^= lb
            m2 = col[px] & ~(1 << py)
            while m2 and len(out) < 20:
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
                    b1 = y1 * N + x; b2 = yh * N + x
                    if used[b1] or used[b2]:
                        ok = False; break
                    segs.append(b1); segs.append(b2)
                if not ok:
                    continue
                for y in range(y1, yh):
                    s1 = NN + y * N + x1; s2 = NN + y * N + xh
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
            x = px - (1 if dx < 0 else 0)
            y = py - (1 if dx < 0 else 0)
            for _ in range(d):
                s = 2 * NN + y * N + x
                if used[s]:
                    return False
                segs.append(s)
                x += dx; y += dy
        else:
            x = px - (1 if dx < 0 else 0)
            y = py - (1 if dx > 0 else 0)
            for _ in range(d):
                s = 3 * NN + y * N + x
                if used[s]:
                    return False
                segs.append(s)
                x += dx; y += dy
        return True

    def cand_diag(px, py, out):
        k2 = px - py + N - 1
        k1 = px + py
        m = dm2[k2] & ~(1 << py)
        while m and len(out) < 20:
            lb = m & -m; y1 = lb.bit_length() - 1; m ^= lb
            x1 = px - py + y1
            if x1 < 0 or x1 >= N:
                continue
            lo, hi = (py, y1) if py < y1 else (y1, py)
            d = hi - lo - 1
            if d > 0 and dm2[k2] & (((1 << d) - 1) << (lo + 1)):
                continue
            m2 = dm1[k1] & ~(1 << py)
            while m2 and len(out) < 20:
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

    def pick(cands, mode):
        if mode == 0:
            return cands[rng.randrange(len(cands))]
        if mode == 1:
            return min(cands, key=lambda c: len(c[0]))
        cs = sorted(cands, key=lambda c: len(c[0]))[:3]
        return cs[rng.randrange(len(cs))]

    def regrow(order, mode):
        # sweep until saturated: new dots may enable rectangles at later points,
        # and earlier-failed points can be retried on the next sweep.
        improved = True
        while improved and time.time() - t0 < T:
            improved = False
            for (px, py) in order:
                if time.time() - t0 > T:
                    return
                if (row[py] >> px) & 1:
                    continue
                cands = []
                if rng.random() < 0.5:
                    cand_axis(px, py, cands); cand_diag(px, py, cands)
                else:
                    cand_diag(px, py, cands); cand_axis(px, py, cands)
                if cands:
                    segs, corners = pick(cands, mode)
                    idx = corners.index((px, py))
                    cyc = tuple(corners[idx:] + corners[:idx])
                    add_rect(px, py, cyc, segs)
                    improved = True

    def snapshot():
        return [(ops[i][0], ops[i][1], ops[i][2], ops[i][3])
                for i in range(len(ops)) if active[i]]

    def rebuild(snap):
        reset_state()
        for (px, py, corners, segs) in snap:
            add_rect(px, py, corners, list(segs))

    empties = [(x, y) for x in range(N) for y in range(N) if (x, y) not in init_set]
    by_w = sorted(empties, key=lambda p: -w[p[1]][p[0]])

    reset_state()
    regrow(by_w, 1)
    best_score = cur[0]
    best_snap = snapshot()
    stagnant = 0

    while time.time() - t0 < T - 0.15:
        act = [i for i in range(len(ops)) if active[i]]
        if act:
            k = 1 + rng.randrange(5)
            if rng.random() < 0.4:
                ax, ay = rng.randrange(N), rng.randrange(N)
                act.sort(key=lambda i: (ops[i][0]-ax)**2 + (ops[i][1]-ay)**2)
                for i in act[:k]:
                    remove_op(i)
            else:
                for i in rng.sample(act, min(k, len(act))):
                    remove_op(i)
        mode = rng.randrange(3)
        order = sorted(empties, key=lambda p: -(w[p[1]][p[0]] * (0.4 + rng.random())))
        regrow(order, mode)
        if cur[0] > best_score:
            best_score = cur[0]
            best_snap = snapshot()
            stagnant = 0
        else:
            stagnant += 1
            if stagnant > 40 or cur[0] < best_score - 3 * N * N:
                rebuild(best_snap)
                stagnant = 0

    out = [str(len(best_snap))]
    for (px, py, corners, segs) in best_snap:
        pts = [(px, py)] + list(corners[1:])
        out.append(" ".join(f"{x} {y}" for (x, y) in pts))
    sys.stdout.write("\n".join(out) + "\n")

main()
