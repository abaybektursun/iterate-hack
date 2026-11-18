import json
import math
import random
import sys

random.seed(0)

N = 26
EPS = 1e-12

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def dist2(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy

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
        circles[i][2] = max_radius_for(i, circles, x, y) * 0.999999

def init_packing():
    # Start from a mixed structured layout: outer ring + interior points.
    pts = []
    # Corners-ish and edge-related points
    base = [
        (0.12, 0.12), (0.50, 0.12), (0.88, 0.12),
        (0.12, 0.50), (0.50, 0.50), (0.88, 0.50),
        (0.12, 0.88), (0.50, 0.88), (0.88, 0.88),
    ]
    pts.extend(base)
    # Add a denser middle band
    pts.extend([
        (0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72),
        (0.35, 0.50), (0.65, 0.50), (0.50, 0.35), (0.50, 0.65),
        (0.20, 0.66), (0.34, 0.84), (0.66, 0.84), (0.84, 0.66),
        (0.84, 0.34), (0.66, 0.16), (0.34, 0.16), (0.16, 0.34),
        (0.16, 0.84),
    ])
    circles = [[x, y, 0.01] for x, y in pts[:N]]
    tighten(circles)
    return circles

def random_mutation(circles, step_xy, step_r):
    c = [row[:] for row in circles]
    op = random.random()
    if op < 0.65:
        i = random.randrange(N)
        c[i][0] = clamp(c[i][0] + random.gauss(0, step_xy), 0.0, 1.0)
        c[i][1] = clamp(c[i][1] + random.gauss(0, step_xy), 0.0, 1.0)
        c[i][2] = max(1e-6, c[i][2] * math.exp(random.gauss(0, step_r)))
    elif op < 0.90:
        # Move a small cluster
        i = random.randrange(N)
        j = random.randrange(N)
        for k in {i, j}:
            c[k][0] = clamp(c[k][0] + random.gauss(0, step_xy * 1.5), 0.0, 1.0)
            c[k][1] = clamp(c[k][1] + random.gauss(0, step_xy * 1.5), 0.0, 1.0)
            c[k][2] = max(1e-6, c[k][2] * math.exp(random.gauss(0, step_r * 1.3)))
    else:
        # Swap-like relocation toward a random promising grid point
        i = random.randrange(N)
        gx = (random.randint(0, 10) + 0.5) / 11.0
        gy = (random.randint(0, 10) + 0.5) / 11.0
        c[i][0] = clamp(0.65 * c[i][0] + 0.35 * gx + random.gauss(0, step_xy * 0.5), 0.0, 1.0)
        c[i][1] = clamp(0.65 * c[i][1] + 0.35 * gy + random.gauss(0, step_xy * 0.5), 0.0, 1.0)
        c[i][2] = max(1e-6, c[i][2] * math.exp(random.gauss(0, step_r * 0.8)))
    return c

def repair(circles):
    # Iteratively tighten; if invalid due to overlaps, shrink the circles involved.
    for _ in range(3):
        for i in range(N):
            x, y, _ = circles[i]
            circles[i][2] = min(circles[i][2], x, 1 - x, y, 1 - y)
        for i in range(N):
            xi, yi, ri = circles[i]
            for j in range(i + 1, N):
                xj, yj, rj = circles[j]
                d = math.hypot(xi - xj, yi - yj)
                if d < ri + rj:
                    if d < 1e-15:
                        # Nudge identical centers apart
                        ang = random.random() * 2 * math.pi
                        xi += 1e-4 * math.cos(ang)
                        yi += 1e-4 * math.sin(ang)
                        xj -= 1e-4 * math.cos(ang)
                        yj -= 1e-4 * math.sin(ang)
                        xi = clamp(xi, 0.0, 1.0)
                        yi = clamp(yi, 0.0, 1.0)
                        xj = clamp(xj, 0.0, 1.0)
                        yj = clamp(yj, 0.0, 1.0)
                        circles[i][0], circles[i][1] = xi, yi
                        circles[j][0], circles[j][1] = xj, yj
                        d = math.hypot(xi - xj, yi - yj)
                    shrink = (ri + rj - d) * 0.500001
                    circles[i][2] = max(1e-6, ri - shrink)
                    circles[j][2] = max(1e-6, rj - shrink)
    tighten(circles)

def score(circles):
    return sum(r for _, _, r in circles)

def local_opt(circles):
    # Greedy coordinate/radius ascent: each circle moved to nearby best point among samples.
    for _ in range(2):
        for i in range(N):
            best = circles[i][:]
            best_r = max_radius_for(i, circles, best[0], best[1])
            best_score = best_r
            x0, y0, _ = circles[i]
            for ang in range(16):
                a = 2 * math.pi * ang / 16.0
                for rad in (0.0, 0.01, 0.02, 0.03, 0.05):
                    x = clamp(x0 + rad * math.cos(a), 0.0, 1.0)
                    y = clamp(y0 + rad * math.sin(a), 0.0, 1.0)
                    r = max_radius_for(i, circles, x, y)
                    if r > best_score + 1e-15:
                        best_score = r
                        best = [x, y, r]
            circles[i] = best
        tighten(circles)

def main():
    circles = init_packing()
    best = [c[:] for c in circles]
    tighten(best)
    best_s = score(best)

    # Annealing with multiple phases.
    T0 = 0.02
    T1 = 1e-5
    iters = 3500
    for t in range(iters):
        frac = t / max(1, iters - 1)
        T = T0 * ((T1 / T0) ** frac)
        step_xy = 0.08 * (1 - frac) + 0.004
        step_r = 0.25 * (1 - frac) + 0.03

        cand = random_mutation(best, step_xy, step_r)
        repair(cand)
        local_opt(cand)
        if not feasible(cand):
            continue
        s = score(cand)
        ds = s - best_s
        if ds > 0 or random.random() < math.exp(ds / max(T, 1e-12)):
            best = cand
            best_s = s

    # Final polish on current best.
    for _ in range(4):
        local_opt(best)
        repair(best)
        if feasible(best):
            s = score(best)
            if s > best_s:
                best_s = s

    # Safety fallback: ensure valid and exactly 26 circles.
    if not feasible(best):
        best = init_packing()
        repair(best)
        local_opt(best)

    print(json.dumps({"circles": best}))

if __name__ == "__main__":
    main()
