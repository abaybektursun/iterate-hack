import json
import math
import random
import time
import numpy as np
from scipy.optimize import minimize, least_squares

N = 26
random.seed(7)
np.random.seed(7)

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def total_r(c):
    return float(np.sum(c[:, 2]))

def valid(c):
    for i in range(N):
        x, y, r = c[i]
        if r <= 0 or x - r < -1e-10 or x + r > 1 + 1e-10 or y - r < -1e-10 or y + r > 1 + 1e-10:
            return False
        for j in range(i + 1, N):
            dx = x - c[j, 0]
            dy = y - c[j, 1]
            if dx * dx + dy * dy < (r + c[j, 2] - 1e-10) ** 2:
                return False
    return True

def project(c):
    c = c.copy()
    for i in range(N):
        c[i, 2] = max(1e-12, c[i, 2])
        c[i, 0] = clamp(c[i, 0], c[i, 2], 1 - c[i, 2])
        c[i, 1] = clamp(c[i, 1], c[i, 2], 1 - c[i, 2])
    return c

def repair(c, rounds=8):
    c = c.copy()
    for _ in range(rounds):
        for i in range(N):
            x, y, r = c[i]
            lim = min(x, 1 - x, y, 1 - y)
            if r > lim:
                c[i, 2] = max(1e-12, lim)

        for i in range(N):
            for j in range(i + 1, N):
                dx = c[i, 0] - c[j, 0]
                dy = c[i, 1] - c[j, 1]
                d = math.hypot(dx, dy)
                s = c[i, 2] + c[j, 2]
                if d < s - 1e-14:
                    if d < 1e-15:
                        ang = 2.0 * math.pi * ((29 * i + 37 * j + 11) % 1009) / 1009.0
                        ux, uy = math.cos(ang), math.sin(ang)
                        c[i, 0] = clamp(c[i, 0] + 1e-4 * ux, c[i, 2], 1 - c[i, 2])
                        c[i, 1] = clamp(c[i, 1] + 1e-4 * uy, c[i, 2], 1 - c[i, 2])
                        dx = c[i, 0] - c[j, 0]
                        dy = c[i, 1] - c[j, 1]
                        d = math.hypot(dx, dy)
                    excess = s - d + 1e-12
                    slack_i = min(c[i, 0] - c[i, 2], 1 - (c[i, 0] + c[i, 2]), c[i, 1] - c[i, 2], 1 - (c[i, 1] + c[i, 2]))
                    slack_j = min(c[j, 0] - c[j, 2], 1 - (c[j, 0] + c[j, 2]), c[j, 1] - c[j, 2], 1 - (c[j, 1] + c[j, 2]))
                    if slack_i >= slack_j:
                        c[i, 2] = max(1e-12, c[i, 2] - 0.58 * excess)
                        c[j, 2] = max(1e-12, c[j, 2] - 0.42 * excess)
                    else:
                        c[i, 2] = max(1e-12, c[i, 2] - 0.42 * excess)
                        c[j, 2] = max(1e-12, c[j, 2] - 0.58 * excess)
        c = project(c)
    return c

def template_from_spec(spec):
    pts = []
    # spec: list of (kind, params)
    for kind, par in spec:
        if kind == "corners":
            s = par.get("r", 0.07)
            pts += [[s, s, s], [1 - s, s, s], [s, 1 - s, s], [1 - s, 1 - s, s]]
        elif kind == "edges":
            k = par.get("k", 6)
            r = par.get("r", 0.055)
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
            for t in range(m):
                a = 2 * math.pi * t / m + par.get("phi", 0.0)
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
    c = np.array(pts[:N], dtype=float)
    if len(c) < N:
        extra = N - len(c)
        for i in range(extra):
            a = 2 * math.pi * i / max(1, extra)
            c = np.vstack([c, [0.5 + 0.18 * math.cos(a), 0.5 + 0.18 * math.sin(a), 0.04]])
    return project(c[:N])

def lowdim_fit(c):
    # fit only global scale and a few affine nudges to make the template feasible
    base = c.copy()

    def pack_to_c(z):
        s, dx, dy, phi = z
        out = base.copy()
        cx, cy = 0.5, 0.5
        for i in range(N):
            x, y, r = base[i]
            x -= cx
            y -= cy
            xr = x * math.cos(phi) - y * math.sin(phi)
            yr = x * math.sin(phi) + y * math.cos(phi)
            out[i, 0] = cx + s * xr + dx
            out[i, 1] = cy + s * yr + dy
            out[i, 2] = max(1e-12, s * base[i, 2])
        return project(out)

    def obj(z):
        c2 = pack_to_c(z)
        pen = 0.0
        for i in range(N):
            x, y, r = c2[i]
            pen += max(0.0, r - x) ** 2 + max(0.0, x + r - 1) ** 2 + max(0.0, r - y) ** 2 + max(0.0, y + r - 1) ** 2
        for i in range(N):
            for j in range(i + 1, N):
                dx = c2[i, 0] - c2[j, 0]
                dy = c2[i, 1] - c2[j, 1]
                d = math.hypot(dx, dy)
                s = c2[i, 2] + c2[j, 2]
                if d < s:
                    pen += (s - d) ** 2
        return -total_r(c2) + 200.0 * pen

    z0 = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
    res = minimize(obj, z0, method="Nelder-Mead", options={"maxiter": 250, "xatol": 1e-5, "fatol": 1e-8})
    return repair(pack_to_c(res.x), rounds=4)

def objective(x, w_ov, w_bd, w_neg):
    c = x.reshape(N, 3)
    r = np.maximum(c[:, 2], 1e-12)
    xx = c[:, 0]
    yy = c[:, 1]
    bd = np.maximum(0.0, r - xx) ** 2 + np.maximum(0.0, xx + r - 1.0) ** 2 + np.maximum(0.0, r - yy) ** 2 + np.maximum(0.0, yy + r - 1.0) ** 2
    ov = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            dx = xx[i] - xx[j]
            dy = yy[i] - yy[j]
            d = math.hypot(dx, dy)
            s = r[i] + r[j]
            if d < s:
                ov += (s - d) ** 2
    neg = -float(np.sum(r))
    radneg = float(np.sum(np.maximum(0.0, -c[:, 2]) ** 2))
    return neg + w_bd * float(np.sum(bd)) + w_ov * ov + w_neg * radneg

def scipy_relax(c, iters=80, w_ov=200.0, w_bd=200.0):
    x0 = c.reshape(-1).copy()
    bounds = []
    for _ in range(N):
        bounds += [(0.0, 1.0), (0.0, 1.0), (1e-12, 0.5)]
    res = minimize(objective, x0, args=(w_ov, w_bd, 1.0), method="L-BFGS-B", bounds=bounds, options={"maxiter": iters, "ftol": 1e-14, "maxcor": 20})
    c = res.x.reshape(N, 3)
    c = project(c)
    c = repair(c, rounds=5)
    return c

def max_r_at(c, i, x, y):
    lim = min(x, 1 - x, y, 1 - y)
    for j in range(N):
        if j == i:
            continue
        lim = min(lim, math.hypot(x - c[j, 0], y - c[j, 1]) - c[j, 2])
    return lim

def greedy_polish(c):
    c = c.copy()
    for _ in range(3):
        for i in range(N):
            x, y, r = c[i]
            base = total_r(c)
            best = c[i].copy()
            for dx in (-0.02, -0.01, 0.0, 0.01, 0.02):
                for dy in (-0.02, -0.01, 0.0, 0.01, 0.02):
                    nx = clamp(x + dx, 0.0, 1.0)
                    ny = clamp(y + dy, 0.0, 1.0)
                    nr = max_r_at(c, i, nx, ny)
                    if nr <= 1e-12:
                        continue
                    trial = c.copy()
                    trial[i] = [nx, ny, 0.995 * nr]
                    trial = repair(trial, rounds=2)
                    if valid(trial):
                        sc = total_r(trial)
                        if sc > base + 1e-15:
                            base = sc
                            best = trial[i].copy()
            c[i] = best
        c = repair(c, rounds=2)
    return c

def final_slsqp(c):
    x0 = c.reshape(-1).copy()
    cons = []
    for i in range(N):
        idx = 3 * i
        cons.append({"type": "ineq", "fun": lambda x, idx=idx: x[idx + 0] - x[idx + 2]})
        cons.append({"type": "ineq", "fun": lambda x, idx=idx: 1.0 - x[idx + 0] - x[idx + 2]})
        cons.append({"type": "ineq", "fun": lambda x, idx=idx: x[idx + 1] - x[idx + 2]})
        cons.append({"type": "ineq", "fun": lambda x, idx=idx: 1.0 - x[idx + 1] - x[idx + 2]})
    for i in range(N):
        for j in range(i + 1, N):
            ii = 3 * i
            jj = 3 * j
            cons.append({"type": "ineq", "fun": lambda x, ii=ii, jj=jj: (x[ii] - x[jj]) ** 2 + (x[ii + 1] - x[jj + 1]) ** 2 - (x[ii + 2] + x[jj + 2]) ** 2})
    bounds = [(0.0, 1.0), (0.0, 1.0), (1e-12, 0.5)] * N
    res = minimize(lambda x: -float(np.sum(x.reshape(N, 3)[:, 2])), x0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 450, "ftol": 1e-12, "disp": False})
    c = res.x.reshape(N, 3)
    c = project(c)
    c = repair(c, rounds=10)
    return c

def structured_library():
    lib = []

    # boundary-heavy
    lib.append([
        ("corners", {"r": 0.068}),
        ("edges", {"k": 5, "r": 0.053, "off": 0.12}),
        ("center", {"r": 0.056}),
        ("grid", {"xs": [0.29, 0.5, 0.71], "ys": [0.30, 0.70], "r": 0.042}),
    ])

    # two rings
    lib.append([
        ("corners", {"r": 0.066}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.24, "m": 8, "r": 0.048, "phi": 0.0}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.11, "m": 4, "r": 0.062, "phi": 0.4}),
        ("strip", {"y": 0.5, "k": 6, "r": 0.034}),
    ])

    # 3x3 core + border
    lib.append([
        ("corners", {"r": 0.065}),
        ("edges", {"k": 4, "r": 0.052, "off": 0.16}),
        ("grid", {"xs": [0.28, 0.5, 0.72], "ys": [0.28, 0.5, 0.72], "r": 0.043}),
        ("center", {"r": 0.055}),
    ])

    # asymmetric ring for escaping symmetric local minima
    lib.append([
        ("corners", {"r": 0.066}),
        ("ring", {"c": (0.48, 0.52), "rad": 0.255, "m": 9, "r": 0.044, "phi": 0.16}),
        ("grid", {"xs": [0.24, 0.5, 0.76], "ys": [0.24, 0.76], "r": 0.041}),
        ("center", {"r": 0.052}),
    ])

    # dense edges with interior pentagon
    lib.append([
        ("corners", {"r": 0.064}),
        ("edges", {"k": 6, "r": 0.048, "off": 0.10}),
        ("ring", {"c": (0.5, 0.5), "rad": 0.16, "m": 5, "r": 0.06, "phi": 0.3}),
        ("center", {"r": 0.05}),
    ])

    return lib

def run():
    start = time.time()
    best = None
    best_score = -1.0

    for spec in structured_library():
        if time.time() - start > 48.0:
            break
        c = template_from_spec(spec)
        c = lowdim_fit(c)
        c = scipy_relax(c, iters=90, w_ov=180.0, w_bd=180.0)
        c = greedy_polish(c)
        c = scipy_relax(c, iters=70, w_ov=260.0, w_bd=240.0)
        c = greedy_polish(c)
        c = repair(c, rounds=6)
        if valid(c):
            sc = total_r(c)
            if sc > best_score:
                best = c.copy()
                best_score = sc

    # Local perturbation around best template
    cur = best.copy()
    temp = 0.02
    step = 0.03
    while time.time() - start < 55.0:
        if random.random() < 0.65:
            cand = scipy_relax(cur, iters=45, w_ov=300.0, w_bd=280.0)
        else:
            cand = cur.copy()
            i = random.randrange(N)
            cand[i, 0] += random.gauss(0, step)
            cand[i, 1] += random.gauss(0, step)
            cand[i, 2] *= math.exp(random.gauss(0, 0.012))
            cand = project(cand)
            cand = repair(cand, rounds=4)

        cand = greedy_polish(cand)
        cand = repair(cand, rounds=4)

        if valid(cand):
            sc = total_r(cand)
            delta = sc - best_score
            if delta > 0 or random.random() < math.exp(delta / max(1e-9, temp)):
                cur = cand.copy()
            if sc > best_score:
                best = cand.copy()
                best_score = sc

        temp *= 0.998
        step *= 0.999
        step = max(step, 0.0015)

    best = final_slsqp(best)
    best = greedy_polish(best)
    best = repair(best, rounds=12)

    if not valid(best):
        best = template_from_spec(structured_library()[0])
        best = repair(best, rounds=18)

    return best

circles = run()
print(json.dumps({"circles": circles.tolist()}))
