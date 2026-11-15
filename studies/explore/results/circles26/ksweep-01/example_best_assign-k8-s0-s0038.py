import json
import math
import random
import time

random.seed(29)

N = 26

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def dist2(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy

def score(circles):
    return sum(r for _, _, r in circles)

def feasible(circles):
    for i, (x, y, r) in enumerate(circles):
        if not (r > 0 and x - r >= -1e-9 and x + r <= 1 + 1e-9 and y - r >= -1e-9 and y + r <= 1 + 1e-9):
            return False
        for j in range(i):
            x2, y2, r2 = circles[j]
            if dist2((x, y), (x2, y2)) < (r + r2 - 1e-9) ** 2:
                return False
    return True

def max_radius_for(i, circles, x=None, y=None):
    if x is None:
        x, y, _ = circles[i]
    r = min(x, 1 - x, y, 1 - y)
    for j, (x2, y2, r2) in enumerate(circles):
        if j == i:
            continue
        d = math.hypot(x - x2, y - y2) - r2
        if d < r:
            r = d
    return max(r, 0.0)

def tighten(circles):
    for i in range(len(circles)):
        x, y, _ = circles[i]
        circles[i][2] = max_radius_for(i, circles, x, y) * 0.999999999

def local_opt(circles, iters=1, movable=None, steps=(0.0006, 0.0012, 0.0025, 0.005, 0.009, 0.014, 0.022)):
    idxs = range(len(circles)) if movable is None else movable
    for _ in range(iters):
        for i in idxs:
            x0, y0, _ = circles[i]
            best_x, best_y = x0, y0
            best_r = max_radius_for(i, circles, x0, y0)
            for step in steps:
                for dx, dy in ((1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)):
                    nrm = math.hypot(dx, dy)
                    x = clamp(x0 + step * dx / nrm, 0.0, 1.0)
                    y = clamp(y0 + step * dy / nrm, 0.0, 1.0)
                    r = max_radius_for(i, circles, x, y)
                    if r > best_r + 1e-15:
                        best_x, best_y, best_r = x, y, r
            circles[i][0], circles[i][1], circles[i][2] = best_x, best_y, best_r * 0.999999999
        tighten(circles)

def probe(circles, grid):
    pts = []
    for i in range(grid + 1):
        x = i / grid
        for j in range(grid + 1):
            y = j / grid
            r = min(x, 1 - x, y, 1 - y)
            for cx, cy, cr in circles:
                d = math.hypot(x - cx, y - cy) - cr
                if d < r:
                    r = d
            pts.append((r, x, y))
    pts.sort(reverse=True)
    return pts

def gap_points(circles, topk=18):
    pts = []
    for grid in (12, 16, 22, 28):
        pts.extend(probe(circles, grid)[:topk])
    pts.sort(reverse=True)
    out = []
    for r, x, y in pts:
        if r <= 1e-6:
            continue
        if all((x - ux) ** 2 + (y - uy) ** 2 >= 0.0045 for _, ux, uy in out):
            out.append((r, x, y))
        if len(out) >= topk:
            break
    return [(x, y) for _, x, y in out]

def expand_new(circles, idx, rounds=8):
    for _ in range(rounds):
        x, y, _ = circles[idx]
        best = (x, y, max_radius_for(idx, circles, x, y))
        br = best[2]
        for step in (0.0004, 0.0008, 0.0016, 0.0032, 0.006, 0.010, 0.016, 0.024):
            for dx, dy in ((1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)):
                nrm = math.hypot(dx, dy)
                xx = clamp(x + step * dx / nrm, 0.0, 1.0)
                yy = clamp(y + step * dy / nrm, 0.0, 1.0)
                rr = max_radius_for(idx, circles, xx, yy)
                if rr > br + 1e-15:
                    best = (xx, yy, rr)
                    br = rr
        circles[idx][0], circles[idx][1], circles[idx][2] = best[0], best[1], best[2] * 0.999999999

def build(seeds):
    circles = [[x, y, 1e-3] for x, y in seeds[:N]]
    local_opt(circles, iters=9)
    tighten(circles)
    while len(circles) < N:
        pts = gap_points(circles, topk=14)
        if not pts:
            pts = [(0.5, 0.5)]
        x, y = pts[0]
        circles.append([x, y, 1e-3])
        expand_new(circles, len(circles) - 1, rounds=8)
        local_opt(circles, iters=2)
        tighten(circles)
    return circles[:N]

def rebuild_weakest(circles, count=4):
    c = [row[:] for row in circles]
    weak = sorted(range(len(c)), key=lambda i: c[i][2])[:count]
    survivors = [c[i][:] for i in range(len(c)) if i not in weak]
    while len(survivors) < N - count:
        pts = gap_points(survivors, topk=10)
        if not pts:
            break
        x, y = pts[0]
        survivors.append([x, y, 1e-3])
        expand_new(survivors, len(survivors) - 1, rounds=6)
        local_opt(survivors, iters=1)
        tighten(survivors)
    while len(survivors) < N:
        x, y = random.choice([(0.1,0.1),(0.5,0.1),(0.9,0.1),(0.1,0.5),(0.9,0.5),(0.1,0.9),(0.5,0.9),(0.9,0.9),(0.25,0.25),(0.75,0.25),(0.25,0.75),(0.75,0.75)])
        survivors.append([x, y, 1e-3])
        expand_new(survivors, len(survivors) - 1, rounds=6)
        local_opt(survivors, iters=1)
        tighten(survivors)
    return survivors[:N]

def mutate(circles, scale, k):
    c = [row[:] for row in circles]
    for i in random.sample(range(len(c)), k):
        c[i][0] = clamp(c[i][0] + random.gauss(0, scale), 0.0, 1.0)
        c[i][1] = clamp(c[i][1] + random.gauss(0, scale), 0.0, 1.0)
    return c

def repair(circles):
    tighten(circles)
    for i in range(len(circles)):
        circles[i][0] = clamp(circles[i][0], 0.0, 1.0)
        circles[i][1] = clamp(circles[i][1], 0.0, 1.0)
        circles[i][2] = max_radius_for(i, circles, circles[i][0], circles[i][1]) * 0.999999999
    tighten(circles)

def main():
    deadline = time.time() + 57.0

    seed_sets = [
        [(0.18,0.18),(0.50,0.18),(0.82,0.18),(0.18,0.50),(0.50,0.50),(0.82,0.50),(0.18,0.82),(0.50,0.82),(0.82,0.82),
         (0.34,0.34),(0.66,0.34),(0.34,0.66),(0.66,0.66),(0.50,0.34),(0.34,0.50),(0.66,0.50),(0.50,0.66),
         (0.14,0.30),(0.30,0.14),(0.70,0.14),(0.86,0.30),(0.86,0.70),(0.70,0.86),(0.30,0.86),(0.14,0.70),(0.50,0.78)],
        [(0.16,0.16),(0.50,0.16),(0.84,0.16),(0.16,0.50),(0.50,0.50),(0.84,0.50),(0.16,0.84),(0.50,0.84),(0.84,0.84),
         (0.27,0.27),(0.73,0.27),(0.27,0.73),(0.73,0.73),(0.50,0.27),(0.27,0.50),(0.73,0.50),(0.50,0.73),
         (0.10,0.34),(0.34,0.10),(0.66,0.10),(0.90,0.34),(0.90,0.66),(0.66,0.90),(0.34,0.90),(0.10,0.66),(0.50,0.64)],
        [(0.20,0.20),(0.50,0.20),(0.80,0.20),(0.20,0.50),(0.50,0.50),(0.80,0.50),(0.20,0.80),(0.50,0.80),(0.80,0.80),
         (0.30,0.30),(0.70,0.30),(0.30,0.70),(0.70,0.70),(0.50,0.30),(0.30,0.50),(0.70,0.50),(0.50,0.70),
         (0.12,0.12),(0.88,0.12),(0.12,0.88),(0.88,0.88),(0.12,0.50),(0.88,0.50),(0.50,0.12),(0.50,0.88),(0.36,0.64)],
        [(0.14,0.14),(0.50,0.14),(0.86,0.14),(0.14,0.50),(0.50,0.50),(0.86,0.50),(0.14,0.86),(0.50,0.86),(0.86,0.86),
         (0.24,0.24),(0.76,0.24),(0.24,0.76),(0.76,0.76),(0.50,0.24),(0.24,0.50),(0.76,0.50),(0.50,0.76),
         (0.08,0.36),(0.36,0.08),(0.64,0.08),(0.92,0.36),(0.92,0.64),(0.64,0.92),(0.36,0.92),(0.08,0.64),(0.50,0.62)],
        [(0.22,0.22),(0.50,0.22),(0.78,0.22),(0.22,0.50),(0.50,0.50),(0.78,0.50),(0.22,0.78),(0.50,0.78),(0.78,0.78),
         (0.33,0.33),(0.67,0.33),(0.33,0.67),(0.67,0.67),(0.50,0.33),(0.33,0.50),(0.67,0.50),(0.50,0.67),
         (0.11,0.11),(0.89,0.11),(0.11,0.89),(0.89,0.89),(0.11,0.50),(0.89,0.50),(0.50,0.11),(0.50,0.89),(0.39,0.61)],
    ]

    best = None
    best_s = -1.0
    for seeds in seed_sets:
        c = build(seeds)
        repair(c)
        local_opt(c, iters=4)
        repair(c)
        s = score(c)
        if s > best_s:
            best, best_s = c, s

    cur = [row[:] for row in best]
    cur_s = best_s

    # merge/rebuild stage
    for _ in range(10):
        if time.time() > deadline - 2.0:
            break
        cand = rebuild_weakest(cur, count=4 if random.random() < 0.7 else 5)
        local_opt(cand, iters=2)
        repair(cand)
        s = score(cand)
        if s > best_s + 1e-15:
            best, best_s = [row[:] for row in cand], s
            cur, cur_s = [row[:] for row in cand], s
        elif s > cur_s + 1e-15 or random.random() < 0.25:
            cur, cur_s = cand, s

    phases = [(0.015, 1, 120), (0.009, 2, 160), (0.005, 3, 220), (0.0025, 4, 260), (0.0012, 5, 280)]
    while time.time() < deadline - 0.8:
        for scale, k, trials in phases:
            for _ in range(trials):
                if time.time() > deadline - 0.8:
                    break
                cand = mutate(cur, scale, k)
                idxs = sorted(range(len(cand)), key=lambda i: cand[i][2], reverse=True)
                local_opt(cand, iters=1, movable=idxs[:max(9, len(cand)//2)])
                local_opt(cand, iters=1)
                repair(cand)
                if not feasible(cand):
                    continue
                s = score(cand)
                temp = max(1e-6, 0.003 + scale * 2.7)
                if s > cur_s + 1e-15 or random.random() < math.exp((s - cur_s) / temp):
                    cur, cur_s = cand, s
                    if s > best_s + 1e-15:
                        best, best_s = [row[:] for row in cand], s
            if time.time() > deadline - 0.8:
                break

        idxs = sorted(range(len(best)), key=lambda i: best[i][2], reverse=True)
        local_opt(best, iters=2, movable=idxs[:12])
        local_opt(best, iters=1)
        repair(best)
        s = score(best)
        if s > best_s + 1e-15:
            best_s = s

        cand = rebuild_weakest(best, count=3)
        local_opt(cand, iters=2)
        repair(cand)
        if feasible(cand) and score(cand) > best_s + 1e-15:
            best, best_s = cand, score(cand)

    repair(best)
    if not feasible(best):
        best = build(seed_sets[0])
        repair(best)

    print(json.dumps({"circles": best}))

if __name__ == "__main__":
    main()
