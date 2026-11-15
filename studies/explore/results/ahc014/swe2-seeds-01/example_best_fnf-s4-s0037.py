import sys, time, heapq, random
from math import gcd

def main():
    data = sys.stdin.buffer.read().split()
    N = int(data[0]); M = int(data[1])
    init_pts = [(int(data[i]), int(data[i+1])) for i in range(2, 2 + 2*M, 2)]
    c = (N - 1) / 2.0
    w = [[(x - c)**2 + (y - c)**2 + 1 for y in range(N)] for x in range(N)]
    wmax = w[0][0]
    t0 = time.time()
    TL = 2.75
    random.seed(12345)

    def side_segs(ax, ay, bx, by, segs, mids):
        dx = bx - ax; dy = by - ay
        g = gcd(abs(dx), abs(dy))
        ux = dx // g; uy = dy // g
        for i in range(1, g):
            mids.append((ax + ux*i) * N + (ay + uy*i))
        for i in range(g):
            x0 = ax + ux*i; y0 = ay + uy*i
            if ux == 1:
                if uy == 0: k = (x0, y0, 0)
                elif uy == 1: k = (x0, y0, 2)
                else: k = (x0, y0, 3)
            elif ux == -1:
                if uy == 0: k = (x0-1, y0, 0)
                elif uy == 1: k = (x0-1, y0+1, 3)
                else: k = (x0-1, y0-1, 2)
            else:
                if uy == 1: k = (x0, y0, 1)
                else: k = (x0, y0-1, 1)
            segs.append((k[0]*N + k[1])*4 + k[2])

    def run(noise_amp, size_pen, wexp, seed):
        rng = random.Random(seed)
        dotted = [[False]*N for _ in range(N)]
        dots = []
        for x, y in init_pts:
            dotted[x][y] = True
            dots.append((x, y))
        used = set()
        heap = []
        pending = {}
        out = []
        counter = 0
        ticks = 0
        gain = 0.0

        def wpri(x, y):
            return (w[x][y] / wmax) ** wexp * wmax

        def build(sx, sy, tx, ty, ex, ey, fx, fy, newx, newy):
            nonlocal counter
            if newx == ex and newy == ey:
                order = (ex, ey, sx, sy, fx, fy, tx, ty)
            else:
                order = (fx, fy, sx, sy, ex, ey, tx, ty)
            segs = []; mids = []
            side_segs(order[0], order[1], order[2], order[3], segs, mids)
            side_segs(order[2], order[3], order[4], order[5], segs, mids)
            side_segs(order[4], order[5], order[6], order[7], segs, mids)
            side_segs(order[6], order[7], order[0], order[1], segs, mids)
            pri = wpri(newx, newy) - size_pen * len(segs) + rng.uniform(0, noise_amp)
            counter += 1
            heapq.heappush(heap, (-pri, counter, (order, segs, mids, newx, newy)))

        def completions(sx, sy, tx, ty, res):
            dx = tx - sx; dy = ty - sy
            if dx != 0 and dy != 0:
                res.append((sx, ty, tx, sy))
            if (dx + dy) % 2 == 0:
                p = (dx + dy) // 2
                q = (dx - dy) // 2
                ex = sx + p; ey = sy + p
                fx = sx + q; fy = sy - q
                if 0 <= ex < N and 0 <= ey < N and 0 <= fx < N and 0 <= fy < N:
                    res.append((ex, ey, fx, fy))

        def pair_gen(sx, sy, tx, ty):
            res = []
            completions(sx, sy, tx, ty, res)
            for ex, ey, fx, fy in res:
                de = dotted[ex][ey]; df = dotted[fx][fy]
                if de and not df:
                    build(sx, sy, tx, ty, ex, ey, fx, fy, fx, fy)
                elif df and not de:
                    build(sx, sy, tx, ty, ex, ey, fx, fy, ex, ey)
                elif not de and not df:
                    s = sx*N + sy; t = tx*N + ty
                    ei = ex*N + ey; fi = fx*N + fy
                    pending.setdefault(ei, []).append((s, t, fi))
                    pending.setdefault(fi, []).append((s, t, ei))

        for i in range(M):
            x1, y1 = dots[i]
            for j in range(i+1, M):
                pair_gen(x1, y1, dots[j][0], dots[j][1])

        while heap:
            ticks += 1
            if (ticks & 255) == 0 and time.time() - t0 > TL:
                return None, -1.0
            negp, _, move = heapq.heappop(heap)
            order, segs, mids, nx, ny = move
            if dotted[nx][ny]:
                continue
            bad = False
            for m in mids:
                if dotted[m // N][m % N]:
                    bad = True; break
            if not bad:
                for sg in segs:
                    if sg in used:
                        bad = True; break
            if bad:
                continue
            dotted[nx][ny] = True
            for sg in segs:
                used.add(sg)
            gain += w[nx][ny]
            out.append(order)
            pi = nx*N + ny
            for (s, t, oi) in pending.pop(pi, ()):
                ox, oy = oi // N, oi % N
                if not dotted[ox][oy]:
                    build(s // N, s % N, t // N, t % N, nx, ny, ox, oy, ox, oy)
            for (qx, qy) in dots:
                pair_gen(nx, ny, qx, qy)
            dots.append((nx, ny))
        return out, gain

    best_out = []
    best_gain = -1.0
    configs = [
        (0.0, 0.0, 1.0), (30.0, 0.0, 1.0), (100.0, 0.0, 1.0),
        (300.0, 0.0, 1.0), (0.0, 1.0, 1.0), (30.0, 1.0, 1.0),
        (100.0, 3.0, 1.0), (300.0, 1.0, 1.0), (60.0, 0.5, 1.0),
        (200.0, 2.0, 1.0), (0.0, -1.0, 1.0), (30.0, -2.0, 1.0),
        (100.0, -1.0, 1.0), (0.0, 0.0, 1.3), (30.0, 0.0, 1.3),
        (0.0, 0.0, 0.7), (30.0, 0.0, 0.7), (60.0, -0.5, 1.3),
        (0.0, 8.0, 1.0), (30.0, 8.0, 1.0), (0.0, 20.0, 1.0),
        (30.0, -8.0, 1.0), (0.0, -15.0, 1.0), (60.0, 5.0, 0.9),
    ]
    ci = 0
    seed = 999
    while time.time() - t0 < TL:
        if ci < len(configs):
            noise_amp, size_pen, wexp = configs[ci]
        else:
            r = random.random()
            noise_amp = random.uniform(0, wmax) if r < 0.7 else random.uniform(0, 2*wmax)
            size_pen = random.uniform(-15.0, 20.0)
            wexp = random.choice((0.5, 0.7, 0.9, 1.0, 1.0, 1.0, 1.2, 1.5))
        ci += 1
        seed += 1
        out, gain = run(noise_amp, size_pen, wexp, seed)
        if out is None:
            break
        if gain > best_gain:
            best_gain = gain
            best_out = out

    res = [str(len(best_out))]
    for o in best_out:
        res.append(' '.join(map(str, o)))
    sys.stdout.write('\n'.join(res) + '\n')

main()
