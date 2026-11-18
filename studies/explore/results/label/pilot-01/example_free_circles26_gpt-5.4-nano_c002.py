import json, math, random, time
import numpy as np
from scipy.optimize import minimize

# ------------------- Config -------------------
N = 26
TIME_LIMIT = 58.5  # seconds (keep headroom)
SEED = 7
random.seed(SEED)
np.random.seed(SEED)

# ------------------- Utilities -------------------
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def total_r(c):
    return float(np.sum(c[:, 2]))

def valid(c):
    # c: (N,3)
    for i in range(N):
        x, y, r = c[i]
        if not (r > 0 and x - r >= -1e-10 and x + r <= 1 + 1e-10 and y - r >= -1e-10 and y + r <= 1 + 1e-10):
            return False
        for j in range(i + 1, N):
            dx = x - c[j, 0]
            dy = y - c[j, 1]
            if dx * dx + dy * dy < (r + c[j, 2] - 1e-10) ** 2:
                return False
    return True

def project(c):
    c = c.copy()
    c[:, 2] = np.maximum(c[:, 2], 1e-12)
    for i in range(N):
        r = c[i, 2]
        c[i, 0] = clamp(c[i, 0], r, 1 - r)
        c[i, 1] = clamp(c[i, 1], r, 1 - r)
    return c

# Compute max feasible radius at (x,y) given other circles
def max_r_at(c, i, x, y):
    lim = min(x, 1 - x, y, 1 - y)
    for j in range(N):
        if j == i:
            continue
        dj = math.hypot(x - c[j, 0], y - c[j, 1]) - c[j, 2]
        if dj < lim:
            lim = dj
    return lim

# ------------------- Repair/Overlap Fix -------------------
def repair(c, rounds=6):
    c = c.copy()
    for _ in range(rounds):
        # boundary radii cap
        for i in range(N):
            x, y, r = c[i]
            lim = min(x, 1 - x, y, 1 - y)
            if r > lim:
                c[i, 2] = max(1e-12, lim)

        # resolve overlaps by shrinking radii (keep centers fixed)
        for i in range(N):
            xi, yi, ri = c[i]
            for j in range(i + 1, N):
                xj, yj, rj = c[j]
                dx = xi - xj
                dy = yi - yj
                d = math.hypot(dx, dy)
                s = ri + rj
                if d < s - 1e-14:
                    excess = s - d + 1e-12
                    # allocate shrink proportional to available slack to boundaries
                    slack_i = min(xi - ri, 1 - (xi + ri), yi - ri, 1 - (yi + ri))
                    slack_j = min(xj - rj, 1 - (xj + rj), yj - rj, 1 - (yj + rj))
                    if slack_i + slack_j <= 0:
                        # fallback: split 0.5-0.5
                        shrink_i = 0.5 * excess
                        shrink_j = 0.5 * excess
                    else:
                        w_i = max(0.0, slack_i) / (max(0.0, slack_i) + max(0.0, slack_j) + 1e-18)
                        shrink_i = w_i * excess
                        shrink_j = (1 - w_i) * excess
                    c[i, 2] = max(1e-12, ri - shrink_i)
                    c[j, 2] = max(1e-12, rj - shrink_j)
        c = project(c)
    return c

# ------------------- Template Library -------------------
def template_from_spec(spec):
    pts = []

    for kind, par in spec:
        if kind == "corners":
            s = par.get("r", 0.068)
            pts += [[s, s, s], [1 - s, s, s], [s, 1 - s, s], [1 - s, 1 - s, s]]
        elif kind == "edges":
            k = par.get("k", 6)
            r = par.get("r", 0.053)
            off = par.get("off", 0.06)
            xs = np.linspace(off, 1 - off, k)
            ys = np.linspace(off, 1 - off, k)
            for x in xs:
                pts.append([x, r, r])
                pts.append([x, 1 - r, r])
            for y in ys[1:-1]:
                pts.append([r, y, r])
                pts.append([1 - r, y, r])
        elif kind == "ring":
            cx, cy = par.get("c", (0.5, 0.5))
            rad = par.get("rad", 0.24)
            m = par.get("m", 8)
            rr = par.get("r", 0.05)
            phi = par.get("phi", 0.0)
            for t in range(m):
                a = 2 * math.pi * t / m + phi
                pts.append([cx + rad * math.cos(a), cy + rad * math.sin(a), rr])
        elif kind == "center":
            pts.append([0.5, 0.5, par.get("r", 0.06)])
        elif kind == "grid":
            xs = par.get("xs", [0.28, 0.5, 0.72])
            ys = par.get("ys", [0.28, 0.5, 0.72])
            rr = par.get("r", 0.045)
            for x in xs:
                for y in ys:
                    pts.append([x, y, rr])
        elif kind == "strip":
            y = par.get("y", 0.5)
            k = par.get("k", 5)
            rr = par.get("r", 0.05)
            xs = np.linspace(0.12, 0.88, k)
            for x in xs:
                pts.append([x, y, rr])

    c = np.array(pts, dtype=float)
    if len(c) < N:
        extra = N - len(c)
        for i in range(extra):
            a = 2 * math.pi * i / max(1, extra)
            c = np.vstack([c, [0.5 + 0.18 * math.cos(a), 0.5 + 0.18 * math.sin(a), 0.04]])
    c = project(c[:N])
    return c

def structured_library():
    lib = []
    lib.append([  # boundary-heavy + inner grid
        ("corners", {"r": 0.068}),
        ("edges", {"k": 5, "r": 0.053, "off": 0.12}),
        ("center", {"r": 0.056}),
        ("grid", {"xs": [0.29, 0.5, 0.71], "ys": [0.30, 0.70], "r": 0.042}),
    ])
    lib.append([  # two rings + strip
        ("corners", {"r": 0.066}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.245, "m": 8, "r": 0.048, "phi": 0.02}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.12, "m": 4, "r": 0.06, "phi": 0.55}),
        ("strip", {"y": 0.5, "k": 6, "r": 0.034}),
    ])
    lib.append([  # 3x3 core + border
        ("corners", {"r": 0.065}),
        ("edges", {"k": 4, "r": 0.052, "off": 0.16}),
        ("grid", {"xs": [0.28, 0.5, 0.72], "ys": [0.28, 0.5, 0.72], "r": 0.043}),
        ("center", {"r": 0.055}),
    ])
    lib.append([  # asymmetric ring
        ("corners", {"r": 0.066}),
        ("ring", {"c": (0.48, 0.52), "rad": 0.258, "m": 9, "r": 0.044, "phi": 0.18}),
        ("grid", {"xs": [0.24, 0.5, 0.76], "ys": [0.24, 0.76], "r": 0.041}),
        ("center", {"r": 0.052}),
    ])
    lib.append([  # dense edges
        ("corners", {"r": 0.064}),
        ("edges", {"k": 6, "r": 0.048, "off": 0.10}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.165, "m": 5, "r": 0.06, "phi": 0.28}),
        ("center", {"r": 0.050}),
    ])
    return lib

# ------------------- Penalty Objective -------------------
def penalty_objective(x, w_ov, w_bd, w_minr):
    c = x.reshape(N, 3)
    r = np.maximum(c[:, 2], 1e-12)
    xx = c[:, 0]
    yy = c[:, 1]

    # boundary penalty
    bd = (
        np.maximum(0.0, r - xx) ** 2
        + np.maximum(0.0, xx + r - 1.0) ** 2
        + np.maximum(0.0, r - yy) ** 2
        + np.maximum(0.0, yy + r - 1.0) ** 2
    )

    # overlaps penalty (symmetric)
    ov = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            dx = xx[i] - xx[j]
            dy = yy[i] - yy[j]
            d = math.hypot(dx, dy)
            s = r[i] + r[j]
            if d < s:
                ov += (s - d) ** 2

    # keep radii not too small by slight regularization
    minr_pen = float(np.sum(np.maximum(0.0, 1e-12 - c[:, 2]) ** 2))
    return -float(np.sum(r)) + w_bd * float(np.sum(bd)) + w_ov * ov + w_minr * minr_pen

def relax_with_lbfgsb(c0, w_ov=250.0, w_bd=250.0, iters=120):
    x0 = c0.reshape(-1).copy()
    bounds = []
    for _ in range(N):
        bounds += [(0.0, 1.0), (0.0, 1.0), (1e-12, 0.5)]
    res = minimize(
        lambda z: penalty_objective(z, w_ov, w_bd, 1.0),
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": iters, "ftol": 1e-14, "maxcor": 20},
    )
    c = res.x.reshape(N, 3)
    c = project(c)
    c = repair(c, rounds=6)
    return c

# ------------------- Greedy Polish -------------------
def greedy_polish(c, sweeps=4):
    c = c.copy()
    for _ in range(sweeps):
        order = list(range(N))
        random.shuffle(order)
        for i in order:
            x, y, r = c[i]
            base = total_r(c)
            best = c[i].copy()
            best_score = base

            # try moving to a small set of candidate positions
            radii_steps = [0.0, 0.01, 0.02, 0.03, 0.045, 0.06]
            angles = 16
            for rad in radii_steps:
                for k in range(angles):
                    a = 2 * math.pi * k / angles
                    nx = clamp(x + rad * math.cos(a), 0.0, 1.0)
                    ny = clamp(y + rad * math.sin(a), 0.0, 1.0)
                    nr = max_r_at(c, i, nx, ny)
                    if nr <= 1e-12:
                        continue
                    trial = c.copy()
                    trial[i] = [nx, ny, 0.9998 * nr]
                    trial = repair(trial, rounds=2)
                    if valid(trial):
                        sc = total_r(trial)
                        if sc > best_score + 1e-15:
                            best_score = sc
                            best = trial[i].copy()
            c[i] = best
        c = repair(c, rounds=3)
    return c

# ------------------- Main Search -------------------
def main():
    start = time.time()
    best = None
    best_s = -1e18

    # Build candidate from multiple templates
    for spec in structured_library():
        if time.time() - start > TIME_LIMIT:
            break
        c = template_from_spec(spec)

        # quick staged relaxations
        stages = [
            (180.0, 180.0, 90),
            (280.0, 240.0, 90),
        ]
        for w_ov, w_bd, iters in stages:
            if time.time() - start > TIME_LIMIT:
                break
            c = relax_with_lbfgsb(c, w_ov=w_ov, w_bd=w_bd, iters=iters)
            if valid(c):
                s = total_r(c)
                if s > best_s:
                    best, best_s = c.copy(), s

        if time.time() - start > TIME_LIMIT:
            break

        c = greedy_polish(c, sweeps=3)
        if valid(c):
            s = total_r(c)
            if s > best_s:
                best, best_s = c.copy(), s

    if best is None:
        best = template_from_spec(structured_library()[0])
        best = repair(best, rounds=10)
        best_s = total_r(best)

    # Local stochastic improvement around best
    cur = best.copy()
    temp = 0.02
    step_xy = 0.02
    step_r = 0.03

    while time.time() - start < TIME_LIMIT:
        cand = cur.copy()

        # perturb
        if random.random() < 0.65:
            i = random.randrange(N)
            cand[i, 0] = clamp(cand[i, 0] + random.gauss(0, step_xy), 0.0, 1.0)
            cand[i, 1] = clamp(cand[i, 1] + random.gauss(0, step_xy), 0.0, 1.0)
            # update radius to max feasible at new center (then tiny shrink)
            nr = max_r_at(cand, i, cand[i, 0], cand[i, 1])
            cand[i, 2] = max(1e-12, 0.9996 * nr)
        else:
            # scale all radii slightly and reproject/repair
            scale = math.exp(random.gauss(0, step_r))
            cand[:, 2] = np.maximum(1e-12, cand[:, 2] * scale)
            cand = project(cand)

        cand = repair(cand, rounds=4)
        cand = greedy_polish(cand, sweeps=1)

        if valid(cand):
            sc = total_r(cand)
            ds = sc - best_s
            if ds > 1e-12 or random.random() < math.exp(ds / max(1e-9, temp)):
                cur = cand.copy()
                if sc > best_s:
                    best, best_s = cand.copy(), sc

        # cool
        temp *= 0.995
        step_xy = max(0.007, step_xy * 0.995)
        step_r = max(0.01, step_r * 0.995)

    # Final polishing: one more relax + greedy
    if time.time() - start < TIME_LIMIT - 1.0:
        best = relax_with_lbfgsb(best, w_ov=320.0, w_bd=280.0, iters=110)
        best = greedy_polish(best, sweeps=3)
        best = repair(best, rounds=10)

    if not valid(best):
        # last resort: clamp radii to max feasible at current centers
        for i in range(N):
            x, y = best[i, 0], best[i, 1]
            nr = max_r_at(best, i, x, y)
            best[i, 2] = max(1e-12, 0.999 * nr)
        best = project(best)
        best = repair(best, rounds=12)

    if not valid(best):
        # absolute last fallback: output projected template
        best = project(template_from_spec(structured_library()[0]))
        best = repair(best, rounds=20)

    print(json.dumps({"circles": best.tolist()}))

if __name__ == "__main__":
    main()
