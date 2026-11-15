import json, time
import numpy as np
from scipy.optimize import minimize

N = 26
DEADLINE = time.time() + 55.0
rng = np.random.default_rng(12345)

I, J = np.triu_indices(N, 1)

def constraints(z):
    x = z[:N]; y = z[N:2*N]; r = z[2*N:]
    dx = x[I] - x[J]; dy = y[I] - y[J]
    d = np.sqrt(dx*dx + dy*dy) - r[I] - r[J]
    return np.concatenate([x - r, 1 - x - r, y - r, 1 - y - r, d, r])

def objective(z):
    return -z[2*N:].sum()

def feasible_radii(x, y, scale=0.95):
    r = np.minimum.reduce([x, 1 - x, y, 1 - y])
    dx = x[I] - x[J]; dy = y[I] - y[J]
    d = np.sqrt(dx*dx + dy*dy) / 2.0
    for k, (i, j) in enumerate(zip(I, J)):
        r[i] = min(r[i], d[k]); r[j] = min(r[j], d[k])
    return np.maximum(r * scale, 1e-4)

def hex_init(rows, cols, jitter, rng):
    pts = []
    for j in range(rows):
        for i in range(cols):
            pts.append((i + 0.5 * (j % 2), j * 0.8660254))
    pts = np.array(pts[:N], dtype=float)
    pts += rng.normal(0, jitter, pts.shape)
    pts -= pts.min(0)
    span = pts.max(0); span[span < 1e-9] = 1.0
    pts /= span
    m = 0.06
    x = m + pts[:, 0] * (1 - 2*m)
    y = m + pts[:, 1] * (1 - 2*m)
    return x, y

def random_init(rng):
    # jittered 6x5 grid subset
    gx, gy = np.meshgrid(np.arange(6), np.arange(5))
    pts = np.column_stack([gx.ravel(), gy.ravel()]).astype(float)
    pts += rng.uniform(-0.3, 0.3, pts.shape)
    idx = rng.choice(len(pts), N, replace=False)
    pts = pts[idx]
    pts -= pts.min(0)
    span = pts.max(0); span[span < 1e-9] = 1.0
    pts /= span
    m = 0.06
    return m + pts[:,0]*(1-2*m), m + pts[:,1]*(1-2*m)

inits = []
for rows, cols in [(5,6),(6,5),(5,5),(4,7),(7,4),(6,6)]:
    for jit in (0.0, 0.08, 0.2):
        inits.append((rows, cols, jit))
for _ in range(8):
    inits.append(None)

bounds = [(0,1)]*N + [(0,1)]*N + [(1e-5, 0.5)]*N
cons = [{'type': 'ineq', 'fun': constraints}]

best_r = -1.0; best = None
k = 0
while time.time() < DEADLINE - 2.0:
    spec = inits[k % len(inits)]; k += 1
    if spec is None:
        x, y = random_init(rng)
    else:
        x, y = hex_init(*spec, rng)
    r = feasible_radii(x, y)
    z0 = np.concatenate([x, y, r])
    try:
        res = minimize(objective, z0, method='SLSQP', bounds=bounds,
                       constraints=cons,
                       options={'maxiter': 400, 'ftol': 1e-10})
        z = res.x
        val = -res.fun
        if val > best_r and constraints(z).min() > -1e-6:
            best_r = val; best = z.copy()
    except Exception:
        pass
    if time.time() > DEADLINE - 2.0:
        break

if best is None:
    # fallback: 5x5 grid + one small circle
    r = 0.09
    circles = [[0.1 + 0.2*i, 0.1 + 0.2*j, r] for i in range(5) for j in range(5)]
    circles.append([0.5, 0.5, 0.04])
else:
    x = best[:N]; y = best[N:2*N]; r = best[2*N:].copy()
    # shrink radii a hair to guarantee feasibility within tolerance
    for _ in range(200):
        dx = x[I] - x[J]; dy = y[I] - y[J]
        dist = np.sqrt(dx*dx + dy*dy)
        viol = (r[I] + r[J]) - dist
        m = viol.max() if len(viol) else 0
        wall = np.maximum.reduce([r - x, r - (1-x), r - y, r - (1-y)]).max()
        need = max(m, wall, 0.0)
        if need <= 0:
            break
        r -= (need + 1e-9) * 1.0000001
        r = np.maximum(r, 1e-6)
    circles = [[float(x[i]), float(y[i]), float(r[i])] for i in range(N)]

print(json.dumps({"circles": circles}))
