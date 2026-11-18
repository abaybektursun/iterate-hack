import json
import math
import random
import time
import numpy as np
from scipy.optimize import minimize

N = 26
random.seed(11)
np.random.seed(11)

EPS = 1e-12

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def total_r(c):
    return float(np.sum(c[:, 2]))

def valid(c):
    for i in range(N):
        x, y, r = c[i]
        if r <= 0 or x - r < -1e-9 or x + r > 1 + 1e-9 or y - r < -1e-9 or y + r > 1 + 1e-9:
            return False
        for j in range(i + 1, N):
            dx = x - c[j, 0]
            dy = y - c[j, 1]
            if dx * dx + dy * dy < (r + c[j, 2] - 1e-9) ** 2:
                return False
    return True

def project(c):
    c = c.copy()
    for i in range(N):
        c[i, 2] = max(EPS, c[i, 2])
        c[i, 0] = clamp(c[i, 0], c[i, 2], 1 - c[i, 2])
        c[i, 1] = clamp(c[i, 1], c[i, 2], 1 - c[i, 2])
    return c

def max_r_at(c, i, x, y):
    lim = min(x, 1 - x, y, 1 - y)
    for j in range(N):
        if j == i:
            continue
        d = math.hypot(x - c[j, 0], y - c[j, 1]) - c[j, 2]
        if d < lim:
            lim = d
    return max(lim, EPS)

def repair(c, rounds=8):
    c = c.copy()
    for _ in range(rounds):
        for i in range(N):
            x, y, _ = c[i]
            c[i, 2] = min(c[i, 2], x, 1 - x, y, 1 - y)
            c[i, 2] = max(c[i, 2], EPS)

        for i in range(N):
            for j in range(i + 1, N):
                dx = c[i, 0] - c[j, 0]
                dy = c[i, 1] - c[j, 1]
                d = math.hypot(dx, dy)
                s = c[i, 2] + c[j, 2]
                if d < s - 1e-14:
                    if d < 1e-15:
                        ang = 2.0 * math.pi * ((17 * i + 31 * j + 7) % 997) / 997.0
                        ux, uy = math.cos(ang), math.sin(ang)
                        c[i, 0] = clamp(c[i, 0] + 1e-4 * ux, c[i, 2], 1 - c[i, 2])
                        c[i, 1] = clamp(c[i, 1] + 1e-4 * uy, c[i, 2], 1 - c[i, 2])
                        c[j, 0] = clamp(c[j, 0] - 1e-4 * ux, c[j, 2], 1 - c[j, 2])
                        c[j, 1] = clamp(c[j, 1] - 1e-4 * uy, c[j, 2], 1 - c[j, 2])
                        dx = c[i, 0] - c[j, 0]
                        dy = c[i, 1] - c[j, 1]
                        d = math.hypot(dx, dy)
                    excess = s - d + 1e-12
                    si = min(c[i, 0] - c[i, 2], 1 - (c[i, 0] + c[i, 2]), c[i, 1] - c[i, 2], 1 - (c[i, 1] + c[i, 2]))
                    sj = min(c[j, 0] - c[j, 2], 1 - (c[j, 0] + c[j, 2]), c[j, 1] - c[j, 2], 1 - (c[j, 1] + c[j, 2]))
                    ai = 0.5 if abs(si - sj) < 1e-12 else (0.42 if si > sj else 0.58)
                    aj = 1.0 - ai
                    c[i, 2] = max(EPS, c[i, 2] - ai * excess)
                    c[j, 2] = max(EPS, c[j, 2] - aj * excess)
        c = project(c)
    return c

def init_template(kind=0):
    pts = []
    if kind == 0:
        pts = [
            (0.09, 0.09), (0.50, 0.09), (0.91, 0.09),
            (0.09, 0.50), (0.50, 0.50), (0.91, 0.50),
            (0.09, 0.91), (0.50, 0.91), (0.91, 0.91),
            (0.24, 0.24), (0.76, 0.24), (0.24, 0.76), (0.76, 0.76),
            (0.34, 0.50), (0.66, 0.50), (0.50, 0.34), (0.50, 0.66),
            (0.18, 0.66), (0.34, 0.84), (0.66, 0.84), (0.84, 0.66),
            (0.84, 0.34), (0.66, 0.16), (0.34, 0.16), (0.16, 0.34),
            (0.16, 0.84)
        ]
    elif kind == 1:
        pts.extend([(0.08, 0.08), (0.92, 0.08), (0.08, 0.92), (0.92, 0.92)])
        for t in range(8):
            a = 2 * math.pi * t / 8.0 + 0.12
            pts.append((0.5 + 0.23 * math.cos(a), 0.5 + 0.23 * math.sin(a)))
        for t in range(4):
            a = 2 * math.pi * t / 4.0 + 0.34
            pts.append((0.5 + 0.11 * math.cos(a), 0.5 + 0.11 * math.sin(a)))
        pts += [(0.5, 0.5), (0.25, 0.5), (0.75, 0.5), (0.5, 0.25), (0.5, 0.75)]
        pts += [(0.18, 0.32), (0.32, 0.18), (0.68, 0.18), (0.82, 0.32), (0.82, 0.68),
                (0.68, 0.82), (0.32, 0.82), (0.18, 0.68)]
    elif kind == 2:
        xs = [0.12, 0.5, 0.88]
        ys = [0.12, 0.5, 0.88]
        for x in xs:
            for y in ys:
                pts.append((x, y))
        pts += [(0.24, 0.24), (0.76, 0.24), (0.24, 0.76), (0.76, 0.76),
                (0.34, 0.50), (0.66, 0.50), (0.50, 0.34), (0.50, 0.66),
                (0.18, 0.66), (0.66, 0.18), (0.82, 0.34), (0.34, 0.82),
                (0.18, 0.18), (0.82, 0.82)]
    else:
        pts += [(0.09, 0.5), (0.91, 0.5), (0.5, 0.09), (0.5, 0.91)]
        for t in range(10):
            a = 2 * math.pi * t / 10.0 + 0.07
            pts.append((0.5 + 0.22 * math.cos(a), 0.5 + 0.22 * math.sin(a)))
        pts += [(0.20, 0.20), (0.80, 0.20), (0.20, 0.80), (0.80, 0.80),
                (0.35, 0.35), (0.65, 0.35), (0.35, 0.65), (0.65, 0.65),
                (0.5, 0.5), (0.5, 0.28), (0.28, 0.5), (0.72, 0.5), (0.5, 0.72)]
    c = np.array([[x, y, 0.01] for x, y in pts[:N]], dtype=float)
    return repair(c, rounds=3)

def local_greedy(c, sweeps=3):
    c = c.copy()
    for _ in range(sweeps):
        for i in range(N):
            x0, y0, _ = c[i]
            best = c[i].copy()
            best_r = max_r_at(c, i, x0, y0)
            for rad in (0.0, 0.006, 0.012, 0.02, 0.03, 0.04):
                for ang in range(20):
                    a = 2 * math.pi * ang / 20.0
                    x = clamp(x0 + rad * math.cos(a), 0.0, 1.0)
                    y = clamp(y0 + rad * math.sin(a), 0.0, 1.0)
                    r = max_r_at(c, i, x, y)
                    if r > best_r + 1e-15:
                        best_r = r
                        best = np.array([x, y, 0.995 * r], dtype=float)
            c[i] = best
        c = repair(c, rounds=2)
    return c

def soft_obj(x):
    c = x.reshape(N, 3)
    r = np.maximum(c[:, 2], EPS)
    xx = c[:, 0]
    yy = c[:, 1]
    ov = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            dx = xx[i] - xx[j]
            dy = yy[i] - yy[j]
            d = math.hypot(dx, dy)
            s = r[i] + r[j]
            if d < s:
                ov += (s - d) ** 2
    bd = np.sum(np.maximum(0.0, r - xx) ** 2 + np.maximum(0.0, xx + r - 1.0) ** 2 +
                np.maximum(0.0, r - yy) ** 2 + np.maximum(0.0, yy + r - 1.0) ** 2)
    return -float(np.sum(r)) + 250.0 * ov + 250.0 * float(bd)

def relax(c, iters=120):
    x0 = c.reshape(-1).copy()
    bounds = [(0.0, 1.0), (0.0, 1.0), (EPS, 0.5)] * N
    res = minimize(soft_obj, x0, method="L-BFGS-B", bounds=bounds,
                   options={"maxiter": iters, "ftol": 1e-15, "maxcor": 20})
    c = res.x.reshape(N, 3)
    c = project(c)
    c = repair(c, rounds=6)
    return c

def coordinate_ascent(c, passes=2):
    c = c.copy()
    for _ in range(passes):
        improved = False
        for i in range(N):
            x0, y0, _ = c[i]
            base = total_r(c)
            best = c[i].copy()
            best_score = base
            for rad in (0.0, 0.004, 0.008, 0.012, 0.018, 0.025):
                for ang in range(24):
                    a = 2 * math.pi * ang / 24.0
                    x = clamp(x0 + rad * math.cos(a), 0.0, 1.0)
                    y = clamp(y0 + rad * math.sin(a), 0.0, 1.0)
                    r = max_r_at(c, i, x, y)
                    if r <= EPS:
                        continue
                    trial = c.copy()
                    trial[i] = [x, y, 0.998 * r]
                    trial = repair(trial, rounds=1)
                    if valid(trial):
                        sc = total_r(trial)
                        if sc > best_score + 1e-15:
                            best_score = sc
                            best = trial[i].copy()
                            improved = True
            c[i] = best
        c = repair(c, rounds=2)
        if not improved:
            break
    return c

def anneal(best, deadline):
    cur = best.copy()
    cur_s = total_r(cur)
    best = cur.copy()
    best_s = cur_s
    temp = 0.03
    step = 0.03
    it = 0
    while time.time() < deadline:
        it += 1
        cand = cur.copy()
        if random.random() < 0.7:
            i = random.randrange(N)
            cand[i, 0] = clamp(cand[i, 0] + random.gauss(0, step), 0.0, 1.0)
            cand[i, 1] = clamp(cand[i, 1] + random.gauss(0, step), 0.0, 1.0)
            cand[i, 2] = max(EPS, cand[i, 2] * math.exp(random.gauss(0, 0.02)))
        else:
            i = random.randrange(N)
            j = random.randrange(N)
            for k in {i, j}:
                cand[k, 0] = clamp(cand[k, 0] + random.gauss(0, step * 1.3), 0.0, 1.0)
                cand[k, 1] = clamp(cand[k, 1] + random.gauss(0, step * 1.3), 0.0, 1.0)
                cand[k, 2] = max(EPS, cand[k, 2] * math.exp(random.gauss(0, 0.03)))
        cand = project(cand)
        cand = repair(cand, rounds=3)
        if it % 3 == 0:
            cand = local_greedy(cand, sweeps=1)
        if it % 5 == 0:
            cand = coordinate_ascent(cand, passes=1)
        if valid(cand):
            s = total_r(cand)
            d = s - cur_s
            if d > 0 or random.random() < math.exp(d / max(temp, 1e-12)):
                cur = cand
                cur_s = s
            if s > best_s:
                best = cand.copy()
                best_s = s
        temp *= 0.9988
        step *= 0.9993
        if step < 0.0015:
            step = 0.0015
    return best

def final_polish(c):
    c = repair(c, rounds=8)
    c = local_greedy(c, sweeps=4)
    c = coordinate_ascent(c, passes=4)
    c = relax(c, iters=90)
    c = local_greedy(c, sweeps=4)
    c = coordinate_ascent(c, passes=4)
    c = repair(c, rounds=12)
    if valid(c):
        for i in range(N):
            c[i, 2] = min(c[i, 2], c[i, 0], 1 - c[i, 0], c[i, 1], 1 - c[i, 1])
        c = repair(c, rounds=2)
    return c

def main():
    start = time.time()
    deadline = start + 58.5

    candidates = []
    for kind in range(4):
        c = init_template(kind)
        c = relax(c, iters=90)
        c = local_greedy(c, sweeps=3)
        c = coordinate_ascent(c, passes=2)
        c = relax(c, iters=80)
        c = coordinate_ascent(c, passes=2)
        c = repair(c, rounds=6)
        if valid(c):
            candidates.append(c)

    if not candidates:
        candidates = [repair(init_template(0), rounds=10)]

    best = max(candidates, key=total_r)
    best = anneal(best, deadline - 3.0)
    best = final_polish(best)

    if not valid(best):
        best = final_polish(init_template(0))
        if not valid(best):
            best = repair(init_template(0), rounds=20)

    print(json.dumps({"circles": best.tolist()}))

if __name__ == "__main__":
    main()
