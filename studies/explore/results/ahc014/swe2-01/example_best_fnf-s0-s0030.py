import sys
import time
import random

def main():
    t0 = time.time()
    TL = 2.80
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    M = int(data[idx]); idx += 1
    init_dots = []
    for _ in range(M):
        x = int(data[idx]); y = int(data[idx+1]); idx += 2
        init_dots.append((x, y))

    c = (N - 1) / 2.0
    W = [[0.0]*N for _ in range(N)]
    for x in range(N):
        wx = (x - c)*(x - c)
        for y in range(N):
            W[x][y] = wx + (y - c)*(y - c) + 1

    RAYS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    PAIRS = []
    for u in [(1,0),(-1,0),(1,1),(-1,-1)]:
        vs = [(0,1),(0,-1)] if u[1] == 0 else [(1,-1),(-1,1)]
        for v in vs:
            PAIRS.append((u, v))

    # Precompute for each direction the list of lines (each a list of cells in +d order)
    LINES = {}
    for (dx, dy) in RAYS:
        lines = []
        for sx in range(N):
            for sy in range(N):
                px = sx - dx; py = sy - dy
                if 0 <= px < N and 0 <= py < N:
                    continue
                line = []
                cx, cy = sx, sy
                while 0 <= cx < N and 0 <= cy < N:
                    line.append((cx, cy))
                    cx += dx; cy += dy
                lines.append(line)
        LINES[(dx, dy)] = lines

    dot0 = [[False]*N for _ in range(N)]
    for (x, y) in init_dots:
        dot0[x][y] = True

    dot = [row[:] for row in dot0]
    used = bytearray(N*N*4)
    moves = []
    move_keys = []
    score = 0.0

    def side_keys(x1, y1, x2, y2):
        dx = x2 - x1; dy = y2 - y1
        ax = abs(dx); ay = abs(dy)
        steps = ax if ax > ay else ay
        ux = dx // steps; uy = dy // steps
        if ux == 0: did = 1
        elif uy == 0: did = 0
        elif ux == uy: did = 2
        else: did = 3
        keys = []
        x, y = x1, y1
        for i in range(steps):
            nx = x + ux; ny = y + uy
            sx = x if x < nx else nx
            sy = y if y < ny else ny
            keys.append(((sx*N + sy) << 2) | did)
            x = nx; y = ny
            if i < steps - 1 and dot[x][y]:
                return None
        for k in keys:
            if used[k]:
                return None
        return keys

    def rebuild_tables():
        nxt = {}
        for (dx, dy) in RAYS:
            tab = [[None]*N for _ in range(N)]
            for line in LINES[(dx, dy)]:
                last = None
                for (lx, ly) in line:
                    tab[lx][ly] = last
                    if dot[lx][ly]:
                        last = (lx, ly)
            nxt[(dx, dy)] = tab
        return nxt

    def gen_candidates(nxt, alpha):
        cands = []
        ap = cands.append
        for x in range(N):
            row = dot[x]
            for y in range(N):
                if not row[y]:
                    continue
                for (u, v) in PAIRS:
                    p2 = nxt[u][x][y]
                    if p2 is None:
                        continue
                    p4 = nxt[v][x][y]
                    if p4 is None:
                        continue
                    p1x = p2[0] + p4[0] - x
                    p1y = p2[1] + p4[1] - y
                    if not (0 <= p1x < N and 0 <= p1y < N) or dot[p1x][p1y]:
                        continue
                    per = abs(p2[0]-x) + abs(p2[1]-y) + abs(p4[0]-x) + abs(p4[1]-y)
                    w = W[p1x][p1y]
                    ap((-(w - alpha*per), p1x, p1y, p2[0], p2[1], x, y, p4[0], p4[1]))
        return cands

    def apply_move(m):
        nonlocal score
        x1,y1,x2,y2,x3,y3,x4,y4 = m
        if dot[x1][y1]:
            return False
        if not (dot[x2][y2] and dot[x3][y3] and dot[x4][y4]):
            return False
        k1 = side_keys(x1,y1,x2,y2)
        if k1 is None: return False
        k2 = side_keys(x2,y2,x3,y3)
        if k2 is None: return False
        k3 = side_keys(x3,y3,x4,y4)
        if k3 is None: return False
        k4 = side_keys(x4,y4,x1,y1)
        if k4 is None: return False
        kk = k1+k2+k3+k4
        for k in kk:
            used[k] = 1
        dot[x1][y1] = True
        moves.append(m)
        move_keys.append(kk)
        score += W[x1][y1]
        return True

    def undo_move():
        nonlocal score
        m = moves.pop()
        kk = move_keys.pop()
        dot[m[0]][m[1]] = False
        for k in kk:
            used[k] = 0
        score -= W[m[0]][m[1]]

    def reapply(kept):
        while moves:
            undo_move()
        for m in kept:
            apply_move(m)

    def greedy_fill(noise, alpha, deadline, batch):
        while time.time() < deadline:
            nxt = rebuild_tables()
            cands = gen_candidates(nxt, alpha)
            if not cands:
                break
            cands.sort()
            applied = 0
            n = len(cands)
            i = 0
            while i < n and applied < batch and time.time() < deadline:
                if noise > 0:
                    j = min(n - 1, i + int(random.expovariate(1.0/max(1.0, noise*8))))
                    cand = cands[j]
                    cands[j] = cands[i]
                else:
                    cand = cands[i]
                i += 1
                (_, x1,y1,x2,y2,x3,y3,x4,y4) = cand
                if apply_move((x1,y1,x2,y2,x3,y3,x4,y4)):
                    applied += 1
            if applied == 0:
                break

    random.seed(20261114)

    best_score = -1.0
    best_moves = []

    # Initial greedy with a few alphas, keep best
    deadline0 = t0 + 0.6
    for a in (0.4, 0.0, 0.8):
        if time.time() > deadline0:
            break
        while moves:
            undo_move()
        greedy_fill(0.0, a, deadline0, batch=10**9)
        if score > best_score:
            best_score = score
            best_moves = list(moves)

    reapply(best_moves)

    stall = 0
    end = t0 + TL - 0.05
    while time.time() < end:
        if stall >= 12:
            reapply(best_moves)
            stall = 0
        r_ = random.random()
        n = len(moves)
        if r_ < 0.30 and n > 5:
            cut = random.randint(max(0, n-80), n-1)
            while len(moves) > cut:
                undo_move()
        elif r_ < 0.72 and n:
            cx = random.randrange(N); cy = random.randrange(N)
            r = random.randint(2, N//3)
            idxs = set(i for i, m in enumerate(moves)
                       if abs(m[0]-cx) <= r and abs(m[1]-cy) <= r)
            if idxs:
                reapply([moves[i] for i in range(n) if i not in idxs])
        elif n:
            idxs = set(random.sample(range(n), max(1, int(n*random.uniform(0.05, 0.35)))))
            reapply([moves[i] for i in range(n) if i not in idxs])
        greedy_fill(random.uniform(0.0, 0.8),
                    random.uniform(0.0, 1.0),
                    end,
                    batch=random.choice([60, 150, 10**9]))
        if score > best_score:
            best_score = score
            best_moves = list(moves)
            stall = 0
        else:
            stall += 1

    out = [str(len(best_moves))]
    for m in best_moves:
        out.append(' '.join(map(str, m)))
    sys.stdout.write('\n'.join(out) + '\n')

main()
