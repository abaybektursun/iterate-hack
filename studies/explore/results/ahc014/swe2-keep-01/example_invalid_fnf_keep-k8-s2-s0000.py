import sys, time

def main():
    t0 = time.time()
    data = sys.stdin.read().split()
    it = iter(data)
    N = int(next(it)); M = int(next(it))
    dot = [[False]*N for _ in range(N)]
    for _ in range(M):
        x = int(next(it)); y = int(next(it))
        dot[x][y] = True

    DIRS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    didx = {d:i for i,d in enumerate(DIRS)}

    # nxt[d][x][y] = packed id of first dot strictly in direction d, or -1
    nxt = [[[ -1]*N for _ in range(N)] for _ in range(8)]
    for di,(dx,dy) in enumerate(DIRS):
        arr = nxt[di]
        for sx in range(N):
            for sy in range(N):
                px, py = sx-dx, sy-dy
                if 0 <= px < N and 0 <= py < N:
                    continue
                last = -1
                x, y = sx, sy
                while 0 <= x < N and 0 <= y < N:
                    arr[x][y] = last
                    if dot[x][y]:
                        last = x*N+y
                    x += dx; y += dy

    used = set()  # normalized unit-edge keys: min(id1,id2)*4096+max(id1,id2)

    def update_rays(qx, qy):
        for di,(dx,dy) in enumerate(DIRS):
            arr = nxt[di]
            x, y = qx-dx, qy-dy
            while 0 <= x < N and 0 <= y < N and not dot[x][y]:
                arr[x][y] = qx*N+qy
                x -= dx; y -= dy

    def side_edges_ok(x1,y1,x2,y2):
        dx = (x2>x1)-(x2<x1); dy = (y2>y1)-(y2<y1)
        x, y = x1, y1
        while (x,y) != (x2,y2):
            nx, ny = x+dx, y+dy
            a = x*N+y; b = nx*N+ny
            k = a*4096+b if a<b else b*4096+a
            if k in used:
                return False
            x, y = nx, ny
        return True

    def add_side(x1,y1,x2,y2):
        dx = (x2>x1)-(x2<x1); dy = (y2>y1)-(y2<y1)
        x, y = x1, y1
        while (x,y) != (x2,y2):
            nx, ny = x+dx, y+dy
            a = x*N+y; b = nx*N+ny
            used.add(a*4096+b if a<b else b*4096+a)
            x, y = nx, ny

    # configs: pairs of perpendicular direction indices forming a corner
    CONFIGS = []
    for sx in (1,-1):
        for sy in (1,-1):
            CONFIGS.append((didx[(sx,0)], didx[(0,sy)]))
    for a,b in ((1,1),(1,-1),(-1,-1),(-1,1)):
        CONFIGS.append((didx[(a,b)], didx[(b,-a)]))

    cx = (N-1)/2.0
    weight = [[ (x-cx)**2 + (y-cx)**2 + 1 for y in range(N)] for x in range(N)]
    order = sorted((x,y) for x in range(N) for y in range(N) if not dot[x][y],
                   key=lambda p: -weight[p[0]][p[1]])

    ops = []
    TL = 2.6
    improved = True
    cnt = 0
    while improved and time.time()-t0 < TL:
        improved = False
        for px,py in order:
            cnt += 1
            if cnt & 255 == 0 and time.time()-t0 > TL:
                break
            if dot[px][py]:
                continue
            best = None  # (perim, c1,c2,c4)
            for d1,d2 in CONFIGS:
                d1x,d1y = DIRS[d1]; d2x,d2y = DIRS[d2]
                i1 = nxt[d1][px][py]
                if i1 < 0: continue
                i2 = nxt[d2][px][py]
                if i2 < 0: continue
                c1x,c1y = i1//N, i1%N
                c2x,c2y = i2//N, i2%N
                c4x = c1x + (c2x-px); c4y = c1y + (c2y-py)
                if not (0 <= c4x < N and 0 <= c4y < N) or not dot[c4x][c4y]:
                    continue
                if nxt[d2][c1x][c1y] != c4x*N+c4y: continue
                if nxt[d1][c2x][c2y] != c4x*N+c4y: continue
                # check edges
                if not (side_edges_ok(px,py,c1x,c1y) and
                        side_edges_ok(c1x,c1y,c4x,c4y) and
                        side_edges_ok(c4x,c4y,c2x,c2y) and
                        side_edges_ok(c2x,c2y,px,py)):
                    continue
                per = abs(c1x-px)+abs(c1y-py)+abs(c2x-px)+abs(c2y-py)
                if best is None or per < best[0]:
                    best = (per,(c1x,c1y),(c4x,c4y),(c2x,c2y))
            if best is None:
                continue
            _,(c1x,c1y),(c4x,c4y),(c2x,c2y) = best
            add_side(px,py,c1x,c1y); add_side(c1x,c1y,c4x,c4y)
            add_side(c4x,c4y,c2x,c2y); add_side(c2x,c2y,px,py)
            dot[px][py] = True
            update_rays(px,py)
            ops.append((px,py,c1x,c1y,c4x,c4y,c2x,c2y))
            improved = True
        if time.time()-t0 > TL:
            break

    out = [str(len(ops))]
    out += [' '.join(map(str,o)) for o in ops]
    sys.stdout.write('\n'.join(out)+'\n')

main()
