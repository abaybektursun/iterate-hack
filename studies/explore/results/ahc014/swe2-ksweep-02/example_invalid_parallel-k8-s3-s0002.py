import sys
import time

def main():
    t0 = time.time()
    LIMIT = 2.85
    data = sys.stdin.buffer.read().split()
    N = int(data[0]); M = int(data[1])
    dot = [[False]*N for _ in range(N)]
    for i in range(M):
        dot[int(data[2+2*i])][int(data[3+2*i])] = True
    c = (N-1)/2.0
    w = [[(x-c)*(x-c)+(y-c)*(y-c)+1 for y in range(N)] for x in range(N)]
    used = [[0]*N for _ in range(N)]  # bitmask over 4 canonical dirs: E,NE,N,NW

    D = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
    POSIDX = {(1,0):0,(1,1):1,(0,1):2,(-1,1):3}
    NEGIDX = {(-1,0):0,(-1,-1):1,(0,-1):2,(1,-1):3}

    ops = []

    def try_place(px, py):
        # enumerate 8 unordered perpendicular direction pairs {e1, e2=rot90(e1)}
        for i in range(8):
            e1x, e1y = D[i]
            e2x, e2y = D[(i+2) % 8]
            # first dot along e1 from p1
            x, y = px+e1x, py+e1y
            p2 = None
            while 0 <= x < N and 0 <= y < N:
                if dot[x][y]:
                    p2 = (x, y); break
                x += e1x; y += e1y
            if p2 is None: continue
            x, y = px+e2x, py+e2y
            p4 = None
            while 0 <= x < N and 0 <= y < N:
                if dot[x][y]:
                    p4 = (x, y); break
                x += e2x; y += e2y
            if p4 is None: continue
            a = (p2[0]-px)*e1x + (p2[1]-py)*e1y
            b = (p4[0]-px)*e2x + (p4[1]-py)*e2y
            p3x = px + a*e1x + b*e2x
            p3y = py + a*e1y + b*e2y
            if not (0 <= p3x < N and 0 <= p3y < N): continue
            if not dot[p3x][p3y]: continue

            # sides: (start, dir, len, check_dots)
            # p1->p2 and p1->p4 have no intermediate dots by first-dot property
            ok = True
            edge_list = []
            for (sx, sy, dx, dy, L, chk) in (
                (px, py, e1x, e1y, a, False),
                (px, py, e2x, e2y, b, False),
                (p2[0], p2[1], e2x, e2y, b, True),
                (p4[0], p4[1], e1x, e1y, a, True),
            ):
                pos = (dx, dy) in POSIDX
                idx = POSIDX[(dx, dy)] if pos else NEGIDX[(dx, dy)]
                cx, cy = sx, sy
                for k in range(L):
                    if pos:
                        ex, ey = cx, cy
                    else:
                        ex, ey = cx+dx, cy+dy
                    if used[ex][ey] >> idx & 1:
                        ok = False; break
                    edge_list.append((ex, ey, idx))
                    cx += dx; cy += dy
                    if chk and k < L-1 and dot[cx][cy]:
                        ok = False; break
                if not ok: break
            if not ok: continue

            for (ex, ey, idx) in edge_list:
                used[ex][ey] |= (1 << idx)
            dot[px][py] = True
            ops.append((px, py, p2[0], p2[1], p3x, p3y, p4[0], p4[1]))
            return True
        return False

    empt = sorted(
        [(x, y) for x in range(N) for y in range(N) if not dot[x][y]],
        key=lambda p: -w[p[0]][p[1]]
    )
    while time.time() - t0 < LIMIT:
        progress = False
        for (x, y) in empt:
            if dot[x][y]:
                continue
            if try_place(x, y):
                progress = True
            if time.time() - t0 >= LIMIT:
                break
        if not progress:
            break

    out = [str(len(ops))]
    out += [" ".join(map(str, op)) for op in ops]
    sys.stdout.write("\n".join(out) + "\n")

main()
