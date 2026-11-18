import sys, time, random

def main():
    t0 = time.time()
    T = 2.85  # keep margin vs 4s hard limit

    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        print(0)
        return
    N, M = data[0], data[1]
    c = (N - 1) / 2.0
    w = [[(x - c) ** 2 + (y - c) ** 2 + 1 for x in range(N)] for y in range(N)]
    NN = N * N
    NSEG = 4 * NN

    init = [(data[2 + 2 * i], data[3 + 2 * i]) for i in range(M)]
    init_set = set(init)

    # occupancy bitsets for dots
    row = [0] * N
    col = [0] * N
    dm1 = [0] * (2 * N - 1)  # x+y
    dm2 = [0] * (2 * N - 1)  # x-y+N-1

    # segment usage for drawn rectangles (condition 3 disallows shared positive-length segments)
    # index mapping:
    # 0*NN: horizontal "top" edges? We'll keep 4 orientations:
    #   0: between (x,y)->(x+1,y) for y in [0..N-1], x in [0..N-2] (x increases)
    #   1: between (x,y)->(x+1,y) also but for other rectangle sides via x bounds
    # For simplicity with the existing representation used by original attempt:
    #   edge ids for axis rectangles:
    #     b1 = y*N + x (two "vertical" sides between interior corners)
    #     b2 = y*N + x (paired)
    #     s1 = NN + x1 + y*N, s2 = NN + xh + y*N
    #     plus diag: 2*NN or 3*NN families.
    #
    # We keep the exact same edge-ID scheme as the current program to be consistent with candidate generation,
    # but we *stop* using the incorrect bitmask "row[y1]&mask" checks that were inconsistent with edge ids.
    used = bytearray(NSEG)

    # dot presence for each point:
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

    owner = [[-1] * N for _ in range(N)]  # op id that placed the dot at (x,y) as new dot
    active = []
    ops = []  # each op: (px,py,corners,edge_ids)
    children = []

    cur_score = 0.0

    def reset_state():
        nonlocal cur_score, ops, children, active
        for i in range(N):
            row[i] = 0
            col[i] = 0
        for i in range(2 * N - 1):
            dm1[i] = 0
            dm2[i] = 0
        for i in range(NSEG):
            used[i] = 0
        for y in range(N):
            ow = owner[y]
            for x in range(N):
                ow[x] = -1
        ops = []
        children = []
        active = []
        cur_score = 0.0
        for (x, y) in init:
            add_dot(x, y)

    def add_rect(px, py, corners, segs):
        oid = len(ops)
        ops.append((px, py, corners, segs))
        children.append([])
        active.append(True)
        for s in segs:
            used[s] = 1
        owner[py][px] = oid
        for (cx, cy) in corners[1:]:
            o = owner[cy][cx]
            if o >= 0:
                children[o].append(oid)
        add_dot(px, py)
        nonlocal cur_score
        cur_score += w[py][px]

    def remove_op(oid):
        nonlocal cur_score
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
            cur_score -= w[py][px]
            for ch in children[i]:
                if active[ch]:
                    stack.append(ch)

    # Candidate generation:
    # - We enforce condition 2 exactly by checking for dots along rectangle perimeter excluding corners.
    # - We enforce condition 3 exactly by checking used edge ids for all perimeter segments.
    #
    # For speed we restrict enumeration of candidate opposite corners by bitset intersections,
    # but when we accept a candidate we do full local checks.
    def cand_axis(px, py, out, lim=28):
        # choose x2 (existing dot on same row) and x1 as opposite side such that rectangle corners exist:
        # rectangle vertices: (x1,y1),(x2,y1),(x2,y2),(x1,y2) and (px,py) should be the missing one.
        # In current program's axis candidate, they iterate x2 from row[py] and y2 from col[px] and build:
        # corners in order: (x1,y1),(xh,y1),(xh,yh),(x1,yh) with (px,py) among them.
        #
        # Here we'll keep that structure but correctness is via full checks later.
        m = row[py] & ~(1 << px)
        while m and len(out) < lim:
            lb = m & -m
            x2 = lb.bit_length() - 1
            m ^= lb

            m2 = col[px] & ~(1 << py)
            while m2 and len(out) < lim:
                lb2 = m2 & -m2
                y2 = lb2.bit_length() - 1
                m2 ^= lb2

                x1, xh = (px, x2) if px < x2 else (x2, px)
                y1, yh = (py, y2) if py < y2 else (y2, py)

                # width/height must be >=1
                if xh - x1 < 1 or yh - y1 < 1:
                    continue

                # The rectangle's four corners are:
                # (x1,y1),(xh,y1),(xh,yh),(x1,yh); the missing vertex (px,py) is one of these.
                # Since px,py is on row[py], it lies on y=py; so either y1==py or yh==py; similarly x.
                # Ensure px,py matches exactly one corner.
                if not ((py == y1 and px in (x1, xh)) or (py == yh and px in (x1, xh))):
                    continue

                # condition 2: no other dots on perimeter excluding three dots (p_i2,p_i3,p_i4).
                # Since we already require dots at those three positions by construction:
                # We need check interior points along each perimeter segment.
                ok = True

                # top and bottom edges excluding endpoints:
                # y=y1 and y=yh between x1..xh
                if yh - y1 - 1 > 0:
                    pass

                # check dots on top edge (y=y1, x in (x1,xh))
                y_top = y1
                if xh - x1 > 1:
                    mask = ((1 << (xh - x1 - 1)) - 1) << (x1 + 1)
                    if (row[y_top] & mask):
                        ok = False
                # bottom edge y=yh
                if ok and yh - y1 != 0:
                    if xh - x1 > 1:
                        y_bot = yh
                        mask = ((1 << (xh - x1 - 1)) - 1) << (x1 + 1)
                        if (row[y_bot] & mask):
                            ok = False

                # left and right vertical edges excluding endpoints:
                if ok:
                    if yh - y1 > 1:
                        # x=x1 between y1..yh
                        colmask = ((1 << (yh - y1 - 1)) - 1)
                        # But we have col[x] bitset indexed by y, so need mask shift:
                        masky = colmask << (y1 + 1)
                        if (col[x1] & masky):
                            ok = False
                    if ok and yh - y1 > 1:
                        masky = ((1 << (yh - y1 - 1)) - 1) << (y1 + 1)
                        if (col[xh] & masky):
                            ok = False

                if not ok:
                    continue

                # condition 3: perimeter segments cannot share positive-length segment with previous rectangles.
                # We'll use the same edge-id construction as earlier code:
                # horizontal sides segments for x in [x1,xh-1] mapped to b1=y1*N+x and b2=yh*N+x
                segs = []
                for x in range(x1, xh):
                    # endpoints are corners; interior segment count uses x in [x1, xh-1]
                    sA = y1 * N + x
                    sB = yh * N + x
                    if used[sA] or used[sB]:
                        ok = False
                        break
                    segs.append(sA)
                    segs.append(sB)
                if not ok:
                    continue
                # vertical sides segments for y in [y1,yh-1] mapped to NN + x1 + y*N and NN + xh + y*N
                base = NN + x1
                base2 = NN + xh
                for y in range(y1, yh):
                    s1 = base + y * N
                    s2 = base2 + y * N
                    if used[s1] or used[s2]:
                        ok = False
                        break
                    segs.append(s1)
                    segs.append(s2)
                if not ok:
                    continue

                corners = [(px, py), (x1, y1), (xh, y1), (xh, yh), (x1, yh)]
                # Need exactly 4 corners in cycle order with px,py included once.
                # In original they used 4-tuple corners without repeating; we will place missing dot at px,py,
                # and set corners cycle = [corner1, corner2, corner3, corner4] such that corners[idx] is (px,py).
                rect4 = [(x1, y1), (xh, y1), (xh, yh), (x1, yh)]
                if (px, py) not in rect4:
                    continue
                idx = rect4.index((px, py))
                cyc = tuple(rect4[idx:] + rect4[:idx])  # starts with (px,py) as in add_rect later
                out.append((segs, cyc))
            # end while m2
        return out

    def diag_side(px, py, qx, qy, segs):
        # uses the same edge-id mapping as reference/current attempt
        dx = 1 if qx > px else -1
        dy = 1 if qy > py else -1
        d = abs(qx - px)
        if d == 0:
            return True
        if dy == dx:
            off = 2 * NN
            x = px - (1 if dx < 0 else 0)
            y = py - (1 if dx < 0 else 0)
        else:
            off = 3 * NN
            x = px - (1 if dx < 0 else 0)
            y = py - (1 if dx > 0 else 0)
        for _ in range(d):
            s = off + y * N + x
            if used[s]:
                return False
            segs.append(s)
            x += dx
            y += dy
        return True

    def cand_diag(px, py, out, lim=28):
        # axis-aligned in transformed coords as in original; keep their candidate structure
        k2 = px - py + N - 1
        k1 = px + py
        m = dm2[k2] & ~(1 << py)
        while m and len(out) < lim:
            lb = m & -m
            y1 = lb.bit_length() - 1
            m ^= lb

            x1 = px - py + y1
            if x1 < 0 or x1 >= N:
                continue

            # choose x1,y1 as one vertex candidate on same descending diagonal through (px,py)
            lo, hi = (py, y1) if py < y1 else (y1, py)
            # condition 2 for the diagonal sides will be checked by dot scan by bitsets:
            # we rely on exact checks using perimeter dot detection later by verifying no dots on diagonal segments
            # via dm bitsets (fast scan for any dots between).
            # For descending diagonal between (px,py) and (x1,y1): check no dots other than endpoints.
            # For this, any dot on that diagonal segment would share the diagonal line with endpoints.
            if hi - lo - 1 > 0:
                # intermediate points have y between (lo,hi)
                if dm2[k2] & (((1 << (hi - lo - 1)) - 1) << (lo + 1)):
                    continue

            m2 = dm1[k1] & ~(1 << py)  # ascending diagonal through (px,py)
            while m2 and len(out) < lim:
                lb2 = m2 & -m2
                y3 = lb2.bit_length() - 1
                m2 ^= lb2

                x3 = px + py - y3
                if x3 < 0 or x3 >= N:
                    continue

                lo3, hi3 = (py, y3) if py < y3 else (y3, py)
                if hi3 - lo3 - 1 > 0:
                    if dm1[k1] & (((1 << (hi3 - lo3 - 1)) - 1) << (lo3 + 1)):
                        continue

                # opposite vertex (ox,oy) exists as intersection of other two diagonals
                ox = x1 + x3 - px
                oy = y1 + y3 - py
                if ox < 0 or ox >= N or oy < 0 or oy >= N:
                    continue
                # must be a dot (three given dots among rectangle)
                if not ((row[oy] >> ox) & 1):
                    continue

                # condition 2: check all four sides have no extra dots besides corners
                # We'll verify each diagonal side by scanning corresponding diagonal occupancy excluding endpoints.
                # Side px,py -> x1,y1 (descending diagonal k2) already checked.
                # Side px,py -> x3,y3 (ascending diagonal k1) already checked.
                # Side x1,y1 -> ox,oy : descending diagonal with constant k? compute for endpoints
                k2b = x1 - y1 + N - 1
                loB, hiB = (y1, oy) if y1 < oy else (oy, y1)
                if hiB - loB - 1 > 0:
                    if dm2[k2b] & (((1 << (hiB - loB - 1)) - 1) << (loB + 1)):
                        continue

                # Side x3,y3 -> ox,oy : ascending diagonal constant k1c = x3 + y3
                k1c = x3 + y3
                loA, hiA = (y3, oy) if y3 < oy else (oy, y3)
                if hiA - loA - 1 > 0:
                    if dm1[k1c] & (((1 << (hiA - loA - 1)) - 1) << (loA + 1)):
                        continue

                # Now condition 3: check segment overlaps by edge-id mapping along sides.
                segs = []
                if not diag_side(px, py, x1, y1, segs):
                    continue
                if not diag_side(px, py, x3, y3, segs):
                    continue
                if not diag_side(x1, y1, ox, oy, segs):
                    continue
                if not diag_side(x3, y3, ox, oy, segs):
                    continue

                rect4 = [(px, py), (x1, y1), (ox, oy), (x3, y3)]
                # Ensure px,py is missing corner; we constructed it as corner, so keep order starting at px,py
                out.append((segs, tuple(rect4)))
        return out

    # Greedy build with candidate weighted sampling
    def try_build(order, time_limit):
        nonlocal cur_score
        reset_state()

        rng = random.Random(20240527)
        empties = [p for p in order]  # already sorted
        for (px, py) in empties:
            if time.time() - t0 > time_limit:
                break
            if (row[py] >> px) & 1:
                continue

            cands = []
            if rng.random() < 0.55:
                cand_axis(px, py, cands, lim=22)
                if not cands:
                    cand_diag(px, py, cands, lim=22)
            else:
                cand_diag(px, py, cands, lim=22)
                if not cands:
                    cand_axis(px, py, cands, lim=22)

            if not cands:
                continue

            # sample among candidates: prefer longer gained weight (proxy by edge count inverse)
            # but also diversify
            if len(cands) == 1:
                segs, corners = cands[0]
            else:
                scored = []
                for segs, corners in cands:
                    # prefer using fewer segments (likely fewer conflicts) and higher perimeter "availability" -> fewer already used edges in segs is ensured
                    # use corners distance from center as slight bias
                    wx = w[py][px]
                    scored.append((len(segs), rng.random(), wx, segs, corners))
                scored.sort(key=lambda x: (x[0], -x[2]))
                # weighted random among top few
                topk = scored[:min(3, len(scored))]
                idx = rng.randrange(len(topk))
                _, _, _, segs, corners = topk[idx]

            add_rect(px, py, corners, list(segs))

        return cur_score, ops

    empties = [(x, y) for y in range(N) for x in range(N) if (x, y) not in init_set]

    # sort by weight descending with a bit of randomness across trials
    best_score = -1.0
    best_ops = None

    rng = random.Random(7)
    trials = 6
    for tr in range(trials):
        if time.time() - t0 > T - 0.05:
            break
        # center-biased order with noise
        alpha = 0.35 + 0.25 * tr / max(1, trials - 1)
        order = sorted(
            empties,
            key=lambda p: -w[p[1]][p[0]] * (0.75 + alpha * rng.random())
        )
        sc, ops_local = try_build(order, T - 0.02)
        if sc > best_score:
            best_score = sc
            best_ops = ops_local[:]

    # Output format: K and for each op print p1..p4 with p1 being new dot location.
    # ops entries: (px,py,corners_tuple_starting_at_px, segs)
    # Our corners tuple includes (px,py) as first element in axis/diag candidates.
    # But to be safe, rotate so corners[?]==(px,py) and output cycle order starting at that.
    out_lines = [None]
    chosen = []
    # ensure active all: we used snapshotless best_ops directly from build where all ops are active
    for (px, py, corners, segs) in best_ops:
        rect4 = list(corners)
        if rect4[0] != (px, py):
            # rotate to start with px,py
            idx = rect4.index((px, py))
            rect4 = rect4[idx:] + rect4[:idx]
        chosen.append((px, py, rect4))

    out_lines = [str(len(chosen))]
    for px, py, rect4 in chosen:
        # rect4 is length 4 in the order where rect4[0]==(px,py) and consecutive are rectangle vertices
        flat = []
        for (x, y) in rect4:
            flat.append(f"{x} {y}")
        out_lines.append(" ".join(flat))

    sys.stdout.write("\n".join(out_lines) + "\n")

main()
