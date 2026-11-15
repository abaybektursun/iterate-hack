import json
import math
import random
import time

random.seed(3)
start = time.time()

N = 26

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def score(c):
    return sum(r for _, _, r in c)

def feasible(c):
    for x, y, r in c:
        if r <= 0:
            return False
        if x - r < -1e-10 or x + r > 1 + 1e-10 or y - r < -1e-10 or y + r > 1 + 1e-10:
            return False
    for i in range(N):
        x1, y1, r1 = c[i]
        for j in range(i + 1, N):
            x2, y2, r2 = c[j]
            dx = x1 - x2
            dy = y1 - y2
            if dx * dx + dy * dy < (r1 + r2) * (r1 + r2) - 1e-12:
                return False
    return True

def max_r_for(i, c):
    x, y, _ = c[i]
    lim = min(x, 1 - x, y, 1 - y)
    for j in range(N):
        if j == i:
            continue
        x2, y2, r2 = c[j]
        d = math.hypot(x - x2, y - y2)
        lim = min(lim, d - r2)
    return max(0.0, lim)

def relax(c, rounds=10):
    for _ in range(rounds):
        order = list(range(N))
        random.shuffle(order)
        improved = False
        for i in order:
            mr = max_r_for(i, c)
            if mr > c[i][2] + 1e-13:
                c[i][2] = mr
                improved = True
        if not improved:
            break
    return c

def shrink_to_feasible(c):
    d = [x[:] for x in c]
    for _ in range(40):
        if feasible(d):
            return d
        for i in range(N):
            d[i][2] *= 0.997
    return d

def template(kind):
    if kind == 0:
        pts = [
            (0.07,0.07),(0.23,0.07),(0.39,0.07),(0.55,0.07),(0.71,0.07),(0.87,0.07),
            (0.12,0.21),(0.30,0.21),(0.48,0.21),(0.66,0.21),(0.84,0.21),
            (0.07,0.37),(0.25,0.37),(0.43,0.37),(0.61,0.37),(0.79,0.37),
            (0.12,0.53),(0.30,0.53),(0.48,0.53),(0.66,0.53),(0.84,0.53),
            (0.07,0.69),(0.25,0.69),(0.43,0.69),(0.61,0.69),(0.79,0.69),
        ]
    elif kind == 1:
        pts = [
            (0.08,0.08),(0.24,0.08),(0.40,0.08),(0.56,0.08),(0.72,0.08),(0.88,0.08),
            (0.16,0.22),(0.34,0.22),(0.52,0.22),(0.70,0.22),(0.88,0.22),
            (0.08,0.38),(0.26,0.38),(0.44,0.38),(0.62,0.38),(0.80,0.38),
            (0.16,0.54),(0.34,0.54),(0.52,0.54),(0.70,0.54),(0.88,0.54),
            (0.08,0.70),(0.26,0.70),(0.44,0.70),(0.62,0.70),(0.80,0.70),
        ]
    else:
        pts = [
            (0.10,0.10),(0.28,0.10),(0.46,0.10),(0.64,0.10),(0.82,0.10),(0.94,0.10),
            (0.12,0.25),(0.30,0.25),(0.48,0.25),(0.66,0.25),(0.84,0.25),
            (0.10,0.40),(0.28,0.40),(0.46,0.40),(0.64,0.40),(0.82,0.40),
            (0.12,0.55),(0.30,0.55),(0.48,0.55),(0.66,0.55),(0.84,0.55),
            (0.10,0.70),(0.28,0.70),(0.46,0.70),(0.64,0.70),(0.82,0.70),
        ]
    c = [[x, y, 0.03] for x, y in pts[:N]]
    return relax(c, rounds=25)

def perturb(c, scale_xy, scale_r):
    d = [x[:] for x in c]
    i = random.randrange(N)
    mode = random.random()
    if mode < 0.75:
        d[i][0] = clamp(d[i][0] + random.uniform(-scale_xy, scale_xy), d[i][2], 1 - d[i][2])
        d[i][1] = clamp(d[i][1] + random.uniform(-scale_xy, scale_xy), d[i][2], 1 - d[i][2])
    elif mode < 0.9:
        d[i][2] = max(1e-9, d[i][2] + random.uniform(-scale_r, scale_r))
    else:
        j = random.randrange(N)
        if j != i:
            dx = d[i][0] - d[j][0]
            dy = d[i][1] - d[j][1]
            n = math.hypot(dx, dy) + 1e-12
            push = random.uniform(-scale_xy, scale_xy)
            d[i][0] = clamp(d[i][0] + push * dx / n, d[i][2], 1 - d[i][2])
            d[i][1] = clamp(d[i][1] + push * dy / n, d[i][2], 1 - d[i][2])
            d[j][0] = clamp(d[j][0] - push * dx / n, d[j][2], 1 - d[j][2])
            d[j][1] = clamp(d[j][1] - push * dy / n, d[j][2], 1 - d[j][2])
    d[i][2] = min(d[i][2], max_r_for(i, d))
    if not feasible(d):
        d = shrink_to_feasible(d)
        if not feasible(d):
            return None
    return relax(d, rounds=5)

def tighten(c):
    d = [x[:] for x in c]
    for _ in range(8):
        changed = False
        for i in range(N):
            mr = max_r_for(i, d)
            if mr > d[i][2] + 1e-13:
                d[i][2] = mr
                changed = True
        if not changed:
            break
    return d

def polish(c):
    d = [x[:] for x in c]
    dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    for step in [0.0035, 0.0025, 0.0015, 0.001]:
        for _ in range(3):
            order = list(range(N))
            random.shuffle(order)
            moved = False
            for i in order:
                x, y, r = d[i]
                best = d[i][:]
                best_r = r
                cand = [(x, y)]
                for dx, dy in dirs:
                    xx = clamp(x + step * dx, r, 1 - r)
                    yy = clamp(y + step * dy, r, 1 - r)
                    cand.append((xx, yy))
                for xx, yy in cand:
                    tmp = [z[:] for z in d]
                    tmp[i][0], tmp[i][1] = xx, yy
                    mr = max_r_for(i, tmp)
                    if mr > best_r + 1e-12:
                        best = [xx, yy, mr]
                        best_r = mr
                if best_r > r + 1e-12:
                    d[i] = best
                    moved = True
            d = relax(d, rounds=4)
            d = tighten(d)
            if not moved:
                break
    return d

best = None
best_score = -1.0

# Diverse starts
for kind in range(3):
    c = template(kind)
    c = tighten(c)
    s = score(c)
    if s > best_score and feasible(c):
        best = [x[:] for x in c]
        best_score = s

# Jittered copies of best template
base = template(0)
for shift in [0.0, 0.004, -0.004, 0.007, -0.007, 0.011]:
    c = [x[:] for x in base]
    for i in range(N):
        x, y, r = c[i]
        x = clamp(x + (shift if i % 2 == 0 else -shift), r, 1 - r)
        y = clamp(y + (shift if i % 3 == 0 else -shift), r, 1 - r)
        c[i][0], c[i][1] = x, y
    c = relax(c, rounds=12)
    c = tighten(c)
    s = score(c)
    if s > best_score and feasible(c):
        best = [x[:] for x in c]
        best_score = s

# Main search loop
iters = 80000
for t in range(iters):
    if time.time() - start > 58:
        break
    frac = t / iters
    scale_xy = 0.018 * (1.0 - frac) + 0.001
    scale_r = 0.006 * (1.0 - frac) + 0.0005
    cand = perturb(best, scale_xy, scale_r)
    if cand is None:
        continue
    cand = tighten(cand)
    s = score(cand)
    if s > best_score + 1e-12:
        best, best_score = cand, s
    else:
        # Mild annealing acceptance
        if random.random() < 0.02 * (1.0 - frac):
            best, best_score = cand, s

# Final polishing and tightening
best = polish(best)
best = tighten(best)

# Safety shrink if numerical issues appear
if not feasible(best):
    best = shrink_to_feasible(best)

for i in range(N):
    best[i][2] = max(1e-9, best[i][2] - 1e-12)

if not feasible(best):
    best = shrink_to_feasible(best)

print(json.dumps({"circles": best}))
