import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import json
import time
import numpy as np
from scipy.optimize import minimize

N = 26
START = time.monotonic()
DEADLINE = START + 57.0
rng = np.random.default_rng(12345)
I, J = np.triu_indices(N, 1)
M = len(I)
K = 4 * N + M
rows = np.arange(M) + 4 * N
grad = np.zeros(3 * N)
grad[2::3] = -1.0
bounds = [(0.00001, 0.99999), (0.00001, 0.99999),
          (0.00001, 0.49)] * N

base_jac = np.zeros((K, 3 * N))
for i in range(N):
    q = 4 * i
    base_jac[q, 3*i] = 1
    base_jac[q+1, 3*i] = -1
    base_jac[q+2, 3*i+1] = 1
    base_jac[q+3, 3*i+1] = -1
    base_jac[q:q+4, 3*i+2] = -1
base_jac[rows, 3*I+2] = -1
base_jac[rows, 3*J+2] = -1

def constraints(z):
    c = z.reshape(N, 3)
    p, r = c[:, :2], c[:, 2]
    d = p[I] - p[J]
    wall = np.column_stack((p[:, 0]-r, 1-p[:, 0]-r,
                            p[:, 1]-r, 1-p[:, 1]-r))
    return np.concatenate((wall.ravel(),
                           np.sqrt(np.sum(d*d, axis=1)) - r[I] - r[J]))

def jacobian(z):
    c = z.reshape(N, 3)
    d = c[I, :2] - c[J, :2]
    d /= np.maximum(np.linalg.norm(d, axis=1), 1e-15)[:, None]
    a = base_jac.copy()
    a[rows, 3*I] = d[:, 0]
    a[rows, 3*I+1] = d[:, 1]
    a[rows, 3*J] = -d[:, 0]
    a[rows, 3*J+1] = -d[:, 1]
    return a

class OutOfTime(Exception):
    pass

def callback(z):
    if time.monotonic() > DEADLINE:
        raise OutOfTime()

def safe(c):
    c = np.asarray(c).copy()
    c[:, :2] = np.clip(c[:, :2], 1e-7, 1-1e-7)
    c[:, 2] = np.maximum(c[:, 2], 1e-10)
    r = c[:, 2]
    wall = np.minimum(c[:, :2], 1-c[:, :2]).min(axis=1)
    fac = min(1.0, float(np.min(wall/r)))
    d = np.linalg.norm(c[I, :2]-c[J, :2], axis=1)
    fac = min(fac, float(np.min(d/(r[I]+r[J]))))
    c[:, 2] *= max(0.0, fac) * (1-2e-10)
    return c

def optimize(c, iterations=110):
    res = minimize(lambda z: -np.sum(z[2::3]), c.ravel(),
                   jac=lambda z: grad, method="SLSQP", bounds=bounds,
                   constraints={"type": "ineq", "fun": constraints,
                                "jac": jacobian},
                   callback=callback,
                   options={"maxiter": iterations, "ftol": 2e-10,
                            "disp": False})
    return safe(res.x.reshape(N, 3))

def row_seed(counts, jitter=0.0):
    pts = []
    ys = np.linspace(.095, .905, len(counts))
    for k, y in zip(counts, ys):
        xs = np.linspace(.095, .905, k)
        for x in xs:
            pts.append([x, y, .085])
    c = np.array(pts)
    c[:, :2] += rng.normal(0, jitter, (N, 2))
    return c

def grid_extra():
    c = [[x, y, .095] for y in np.linspace(.1,.9,5)
         for x in np.linspace(.1,.9,5)]
    c.append([.2,.2,.035])
    return np.array(c)

def border_seed():
    p = []
    for x in np.linspace(.09,.91,5):
        p.extend([[x,.09,.085],[x,.91,.085]])
    for y in [.295,.5,.705]:
        p.extend([[.09,y,.085],[.91,y,.085]])
    for y in [.3,.5,.7]:
        for x in [.3,.5,.7]:
            p.append([x,y,.085])
    p.append([.4,.4,.035])
    return np.array(p)

# A radius-preserving soft relaxation helps reorganize contacts before
# the exact constrained optimization.
def soften(c, weight=150.0, iterations=65):
    def fun(z):
        a = z.reshape(N,3)
        p, r = a[:,:2], a[:,2]
        d = p[I]-p[J]
        lengths = np.maximum(np.linalg.norm(d,axis=1),1e-12)
        ov = np.maximum(r[I]+r[J]-lengths,0)
        b = np.column_stack((r-p[:,0], r+p[:,0]-1,
                             r-p[:,1], r+p[:,1]-1))
        b = np.maximum(b,0)
        val = -r.sum() + weight*(np.sum(ov*ov)+np.sum(b*b))
        g = np.zeros((N,3))
        g[:,2] = -1 + 2*weight*b.sum(axis=1)
        g[:,0] = 2*weight*(-b[:,0]+b[:,1])
        g[:,1] = 2*weight*(-b[:,2]+b[:,3])
        v = 2*weight*ov
        f = v[:,None]*d/lengths[:,None]
        np.add.at(g[:,:2], I, -f)
        np.add.at(g[:,:2], J, f)
        np.add.at(g[:,2], I, v)
        np.add.at(g[:,2], J, v)
        return val,g.ravel()
    result = minimize(fun,c.ravel(),jac=True,method="L-BFGS-B",
                      bounds=bounds,
                      options={"maxiter":iterations,"ftol":1e-10,
                               "maxcor":12})
    return result.x.reshape(N,3)

best = safe(grid_extra())
best_score = best[:,2].sum()
pool = []
current = best.copy()
current_score = best_score

def remember(c):
    global best, best_score
    score = c[:,2].sum()
    if np.min(c[:,2]) <= 0:
        return score
    if score > best_score:
        best, best_score = c.copy(), score
    if not pool or all(abs(score-s) > 1e-6 for s,_ in pool):
        pool.append((score,c.copy()))
        pool.sort(key=lambda t:-t[0])
        del pool[10:]
    return score

seeds = [
    row_seed([5,5,6,5,5],.003),
    grid_extra(),
    border_seed(),
    row_seed([5,6,5,5,5],.005),
    row_seed([4,5,4,5,4,4],.004),
    row_seed([6,5,5,5,5],.006),
]
try:
    for c in seeds:
        if time.monotonic() > START+15:
            break
        c = optimize(c, 150)
        remember(c)
    current = best.copy()
    current_score = best_score
    iteration = 0
    while time.monotonic() < DEADLINE-.4:
        iteration += 1
        if rng.random() < .30:
            current = pool[int(rng.integers(min(5,len(pool))))][1].copy()
            current_score = current[:,2].sum()
        c = current.copy()
        mode = rng.random()
        if mode < .30:
            # Delete a disk and insert it into a different large cavity.
            idx = int(rng.integers(N))
            other = np.delete(c,idx,axis=0)
            pts = rng.uniform(.025,.975,(650,2))
            clearance = np.minimum(pts,1-pts).min(axis=1)
            gaps = np.linalg.norm(pts[:,None,:]-other[None,:,:2],
                                  axis=2)-other[None,:,2]
            clearance = np.minimum(clearance,gaps.min(axis=1))
            order = np.argsort(clearance)[-12:]
            k = int(rng.choice(order))
            c[idx,:2] = pts[k]
            c[idx,2] = max(.015,clearance[k])
        else:
            scale = float(rng.choice([.012,.025,.045,.075,.11]))
            count = int(rng.integers(3,N+1))
            ids = rng.choice(N,count,replace=False)
            c[ids,:2] += rng.normal(0,scale,(count,2))
            c[:, :2] = np.clip(c[:,:2],.015,.985)
            if mode > .78:
                c[:,2] *= rng.uniform(.85,1.15,N)
                c = soften(c,weight=float(rng.choice([70,140,240])),
                           iterations=75)
        candidate = optimize(c,110)
        sc = remember(candidate)
        temperature = .0035 * (1-(time.monotonic()-START)/60) + .0003
        if sc > current_score or rng.random() < np.exp(
                max(-700,(sc-current_score)/temperature)):
            current, current_score = candidate, sc
        if iteration % 9 == 0:
            current, current_score = best.copy(), best_score
except OutOfTime:
    pass

best = safe(best)
print(json.dumps({"circles": best.tolist()}, separators=(",",":")))
