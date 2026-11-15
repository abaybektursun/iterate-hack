import json, time, numpy as np
from scipy.optimize import minimize, linprog

N = 26
T0 = time.time()
BUDGET = 55.0
rng = np.random.default_rng(2026)

pairs = np.array([(i, j) for i in range(N) for j in range(i + 1, N)])
PI, PJ = pairs[:, 0], pairs[:, 1]

def cons_fun(v):
    x, y, r = v[:N], v[N:2*N], v[2*N:]
    dx = x[PI] - x[PJ]
    dy = y[PI] - y[PJ]
    d = np.sqrt(dx * dx + dy * dy) - r[PI] - r[PJ]
    return np.concatenate([r, x - r, 1 - x - r, y - r, 1 - y - r, d])

def cons_jac(v):
    x, y, r = v[:N], v[N:2*N], v[2*N:]
    m = 5 * N + len(PI)
    J = np.zeros((m, 3 * N))
    J[0:N, 2*N:3*N] = np.eye(N)
    J[N:2*N, 0:N] = np.eye(N)
    J[N:2*N, 2*N:3*N] = -np.eye(N)
    J[2*N:3*N, 0:N] = -np.eye(N)
    J[2*N:3*N, 2*N:3*N] = -np.eye(N)
    J[3*N:4*N, N:2*N] = np.eye(N)
    J[3*N:4*N, 2*N:3*N] = -np.eye(N)
    J[4*N:5*N, N:2*N] = -np.eye(N)
    J[4*N:5*N, 2*N:3*N] = -np.eye(N)
    row = 5 * N
    dx = x[PI] - x[PJ]
    dy = y[PI] - y[PJ]
    dist = np.maximum(np.sqrt(dx * dx + dy * dy), 1e-12)
    for k in range(len(PI)):
        i, j = PI[k], PJ[k]
        J[row + k, i] = dx[k] / dist[k]
        J[row + k, j] = -dx[k] / dist[k]
        J[row + k, N + i] = dy[k] / dist[k]
        J[row + k, N + j] = -dy[k] / dist[k]
        J[row + k, 2 * N + i] = -1.0
        J[row + k, 2 * N + j] = -1.0
    return J

con = {'type': 'ineq', 'fun': cons_fun, 'jac': cons_jac}

def obj(v):
    return -v[2*N:].sum()

def obj_jac(v):
    g = np.zeros(3 * N)
    g[2*N:] = -1.0
    return g

def lp_radii(x, y):
    dx = x[PI] - x[PJ]
    dy = y[PI] - y[PJ]
    dist = np.sqrt(dx * dx + dy * dy)
    A = np.zeros((len(PI), N))
    A[np.arange(len(PI)), PI] = 1.0
    A[np.arange(len(PI)), PJ] = 1.0
    bounds = np.stack([np.zeros(N),
                       np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y))], axis=1)
    res = linprog(-np.ones(N), A_ub=A, b_ub=dist, bounds=bounds, method='highs')
    if res.success:
        return res.x
    return np.minimum(bounds[:, 1], 0.02)

def slsqp(v0, maxiter=500):
    return minimize(obj, v0, jac=obj_jac, constraints=[con],
                    method='SLSQP', options={'maxiter': maxiter, 'ftol': 1e-13})

MARGIN = 5e-7

def feasible(v):
    return cons_fun(v).min() > -1e-9

def repair(x, y, r):
    for _ in range(80):
        v = np.concatenate([x, y, r])
        c = cons_fun(v)
        if c.min() > MARGIN:
            break
        viol = np.where(c[5*N:] <= MARGIN)[0]
        for k in viol:
            i, j = PI[k], PJ[k]
            dist = np.hypot(x[i]-x[j], y[i]-y[j])
            need = (r[i] + r[j] + MARGIN) - dist
            if need > 0:
                si = r[i] / max(r[i] + r[j], 1e-12)
                r[i] -= need * si
                r[j] -= need * (1 - si)
        wall = np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y))
        r = np.minimum(r, wall - MARGIN)
        r = np.maximum(r, 1e-9)
    return r

best_v, best_s = None, -np.inf

def try_update(v):
    global best_v, best_s
    x, y, r = v[:N].copy(), v[N:2*N].copy(), v[2*N:].copy()
    r = repair(x, y, r)
    vv = np.concatenate([x, y, r])
    if feasible(vv):
        s = r.sum()
        if s > best_s:
            best_s, best_v = s, vv

def hex_init():
    pts = []
    rr = 0.09
    j = 0
    while len(pts) < N:
        off = rr if j % 2 else 0.0
        cols = 6 if j % 2 else 5
        for i in range(cols):
            pts.append([rr + off + 2 * rr * i * 1.02, rr + 2 * rr * j * 0.9])
        j += 1
    pts = np.array(pts[:N])
    pts[:, 0] = np.clip(pts[:, 0], rr, 1 - rr)
    pts[:, 1] = np.clip(pts[:, 1], rr, 1 - rr)
    return np.concatenate([pts[:, 0], pts[:, 1], np.full(N, rr * 0.9)])

def rand_init():
    pts = rng.random((N, 2)) * 0.84 + 0.08
    return np.concatenate([pts[:, 0], pts[:, 1], np.full(N, 0.04)])

# Phase 1: cold restarts (hex + random)
for k in range(4):
    if time.time() - T0 > BUDGET * 0.35:
        break
    try:
        v0 = hex_init() if k == 0 else rand_init()
        try_update(slsqp(v0).x)
    except Exception:
        pass

# Phase 2: basin hopping — kick a random subset of circles, LP-resolve radii, SLSQP
scale = 0.02
fails = 0
while time.time() - T0 < BUDGET:
    if best_v is None:
        break
    v = best_v.copy()
    mode = rng.random()
    if mode < 0.55:
        # small subset kick
        kk = rng.integers(1, 6)
        idx = rng.choice(N, size=kk, replace=False)
        v[idx] += rng.normal(0, scale, kk)
        v[N + idx] += rng.normal(0, scale, kk)
    elif mode < 0.85:
        # global tiny jitter
        v[:2*N] += rng.normal(0, scale * 0.4, 2 * N)
    else:
        # relocate smallest circles to random free-ish spots
        kk = rng.integers(1, 3)
        idx = np.argsort(best_v[2*N:])[:kk]
        v[idx] = rng.uniform(0.1, 0.9, kk)
        v[N + idx] = rng.uniform(0.1, 0.9, kk)
    v[:N] = np.clip(v[:N], 0.02, 0.98)
    v[N:2*N] = np.clip(v[N:2*N], 0.02, 0.98)
    r = lp_radii(v[:N], v[N:2*N])
    v[2*N:] = np.maximum(r * 0.95, 1e-4)
    try:
        res = slsqp(v)
        prev = best_s
        try_update(res.x)
        if best_s > prev:
            fails = 0
            scale = max(scale * 0.7, 0.003)
            r2 = lp_radii(res.x[:N], res.x[N:2*N])
            v2 = np.concatenate([res.x[:N], res.x[N:2*N], np.maximum(r2 * 0.98, 1e-4)])
            try_update(slsqp(v2, maxiter=300).x)
        else:
            fails += 1
            if fails > 8:
                scale = min(scale * 1.6, 0.08)
                fails = 0
    except Exception:
        pass

if best_v is None:
    r = 0.1
    c = [[0.1 + 0.2 * i, 0.1 + 0.2 * j, r] for i in range(5) for j in range(5)]
    c.append([0.3, 0.3, 0.04])
    print(json.dumps({"circles": c}))
else:
    x, y = best_v[:N].copy(), best_v[N:2*N].copy()
    r = repair(x, y, best_v[2*N:].copy())
    x = np.clip(x, r + MARGIN, 1 - r - MARGIN)
    y = np.clip(y, r + MARGIN, 1 - r - MARGIN)
    r = repair(x, y, r)
    circles = [[float(x[i]), float(y[i]), float(r[i])] for i in range(N)]
    print(json.dumps({"circles": circles}))
