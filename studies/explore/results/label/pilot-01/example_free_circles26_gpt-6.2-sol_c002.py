import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
START = time.monotonic()

import json
import numpy as np
from scipy.optimize import minimize

N = 26
I, J = np.triu_indices(N, 1)
K = np.arange(N)
P = np.arange(len(I))
BND = np.array([(0., 1.), (0., 1.), (.00001, .35)] * N)
OBJ = np.tile([0., 0., -1.], N)
WALL = np.zeros((4 * N, 3 * N))
for k in range(4):
    WALL[k*N+K, 3*K+k//2] = 1 if k % 2 == 0 else -1
    WALL[k*N+K, 3*K+2] = -1
COLS = np.array([3*I, 3*I+1, 3*I+2, 3*J, 3*J+1, 3*J+2])
ONES = np.ones(len(I))
rng = np.random.default_rng(749832)
DEADLINE = START + 57.7


def geometry(c):
    x, y, r = c.T
    dx, dy = x[I]-x[J], y[I]-y[J]
    d = np.hypot(dx, dy)
    return x, y, r, dx, dy, d


def soft(z, weight, reg, bias, floor, steps):
    def fg(z):
        x, y, r, dx, dy, d = geometry(z.reshape(N, 3))
        a = np.maximum(0., r-x)
        b = np.maximum(0., r+x-1.)
        c = np.maximum(0., r-y)
        e = np.maximum(0., r+y-1.)
        h = np.maximum(0., r[I]+r[J]-d)
        coeff = h / np.maximum(d, 1e-14)
        u, v = coeff*dx, coeff*dy
        bc = np.bincount
        g = np.empty((N, 3))
        g[:, 0] = b-a-bc(I, u, N)+bc(J, u, N)
        g[:, 1] = e-c-bc(I, v, N)+bc(J, v, N)
        g[:, 2] = a+b+c+e+bc(I, h, N)+bc(J, h, N)
        g *= 2*weight
        rr = r-.1
        g[:, 2] += 2*reg*rr-bias
        f = weight*(a@a+b@b+c@c+e@e+h@h) + reg*(rr@rr)-bias@r
        return f, g.ravel()

    bounds = BND.copy()
    bounds[2::3, 0] = floor
    res = minimize(fg, z.ravel(), method="L-BFGS-B", jac=True,
                   bounds=bounds, options={"maxiter": steps, "maxcor": 12,
                                           "ftol": 2e-10, "gtol": 1e-6})
    return res.x.reshape(N, 3)


def exact(c, full=False):
    _, _, r, _, _, d = geometry(c)
    mask = np.ones(len(I), dtype=bool) if full else d-r[I]-r[J] < .115
    ii, jj = I[mask], J[mask]
    cols = COLS[:, mask]
    m = len(ii)
    rows = np.arange(m)+4*N
    matrix = np.zeros((4*N+m, 3*N))
    matrix[:4*N] = WALL
    ones = ONES[:m]
    cache_z = None

    def evaluate(z):
        nonlocal cache_z, vals, derivs
        if cache_z is not None and np.array_equal(z, cache_z):
            return
        cache_z = z.copy()
        x, y, r = z.reshape(N, 3).T
        dx, dy = x[ii]-x[jj], y[ii]-y[jj]
        d = np.hypot(dx, dy)
        vals = np.concatenate((x-r, 1-x-r, y-r, 1-y-r, d-r[ii]-r[jj]))
        d = np.maximum(d, 1e-15)
        u, v = dx/d, dy/d
        derivs = (u, v, -ones, -u, -v, -ones)

    vals = derivs = None

    def cf(z):
        evaluate(z)
        return vals

    def cj(z):
        evaluate(z)
        matrix[rows, cols] = derivs
        return matrix

    res = minimize(lambda z: OBJ @ z, c.ravel(), jac=lambda z: OBJ,
                   bounds=BND, method="SLSQP",
                   constraints=[{"type": "ineq", "fun": cf, "jac": cj}],
                   options={"maxiter": 62, "ftol": 2e-11})
    return res.x.reshape(N, 3)


def safe(c):
    c = c.copy()
    x, y, r, _, _, d = geometry(c)
    if not np.all(np.isfinite(c)) or np.min(r) <= 0:
        return None
    factor = min(1., np.min(np.minimum.reduce([x, 1-x, y, 1-y])/r),
                 np.min(d/(r[I]+r[J])))
    if factor < .90:
        return None
    r *= factor*(1-4e-10)
    return c


def rows_seed(counts, stagger):
    m = len(counts)
    pts = []
    ys = np.linspace(.095, .905, m)
    for j, k in enumerate(counts):
        if stagger:
            h = .81/(max(counts)-1)
            span = h*(k-1)
            off = (.81-span)*(.08 if j % 2 else .92)
            xs = .095+off+np.arange(k)*h
        else:
            xs = np.linspace(.095, .905, k)
        pts.extend((x, ys[j], .095) for x in xs)
    return np.array(pts)


def structured():
    groups = [
        [5, 5, 6, 5, 5], [6, 5, 4, 5, 6], [6, 4, 6, 4, 6],
        [5, 6, 4, 6, 5], [6, 4, 5, 5, 6], [6, 5, 5, 5, 5],
        [5, 4, 5, 4, 4, 4], [5, 4, 4, 4, 4, 5], [4, 5, 4, 5, 4, 4],
        [4, 5, 4, 4, 5, 4], [5, 4, 4, 5, 4, 4], [4, 4, 5, 4, 4, 5],
        [6, 6, 7, 7], [7, 6, 6, 7]
    ]
    out = []
    for stagger in (False, True):
        for g in groups:
            out.append(rows_seed(g, stagger))

    # Perimeter chains with independently packed cores.
    for m in (4, 5, 6):
        xy = np.linspace(.099, .901, m)
        outer = ([(t, xy[0]) for t in xy] +
                 [(xy[-1], t) for t in xy[1:]] +
                 [(t, xy[-1]) for t in xy[-2::-1]] +
                 [(xy[0], t) for t in xy[-2:0:-1]])
        left = N-len(outer)
        for ring in (False, True):
            if ring:
                a = 2*np.pi*np.arange(left-1)/(left-1) + .19
                p = np.column_stack((.5+.253*np.cos(a), .5+.253*np.sin(a)))
                p = np.vstack((p, [.5, .5]))
            else:
                g = np.linspace(.29, .71, 4)
                p = np.array([(x, y) for x in g for y in g])
                rank = np.sum((p-.5)**2, axis=1)+rng.uniform(0, .009, len(p))
                p = p[np.argsort(rank)[:left]]
                if left > len(p):
                    continue
            out.append(np.column_stack((np.vstack((outer, p)),
                                        np.full(N, .085))))
    return out


def insert(c, removed):
    out = c.copy()
    keep = np.ones(N, dtype=bool)
    keep[removed] = False
    for i in removed:
        pts = np.vstack((rng.uniform(.025, .975, (400, 2)),
                         rng.uniform(.18, .82, (100, 2))))
        dx = pts[:, None, :] - out[keep, :2]
        nearest = np.sqrt(np.sum(dx*dx, axis=2)) - out[keep, 2]
        room = np.minimum(np.min(nearest, axis=1),
                          np.min(np.minimum(pts, 1-pts), axis=1))
        ix = np.argmax(room+rng.uniform(0, .018, len(pts)))
        out[i, :2] = pts[ix]
        out[i, 2] = np.clip(room[ix], .045, .13)
        keep[i] = True
    return out


def mutate(c, large):
    z = c.copy()
    p = rng.random()
    if p < .20:
        # Replace one or two weak circles, favoring well-separated vacancies.
        keys = z[:, 2] + rng.uniform(0, .095, N)
        count = 2 if large and rng.random() < .6 else 1
        z = insert(z, np.argsort(keys)[:count])
        z[:, :2] += rng.normal(0, .007, (N, 2))
    elif p < .50:
        i = rng.integers(N)
        delta = z[:, :2]-z[i, :2]
        order = np.argsort(np.sum(delta*delta, axis=1))
        k = rng.integers(2, 10 if large else 6)
        ids = order[:k]
        s = rng.uniform(.027, .085) if large else rng.uniform(.015, .046)
        z[ids, :2] += rng.normal(0, s, (k, 2))
        z[ids, 2] += rng.normal(0, .016, k)
    elif p < .67:
        i = rng.integers(N)
        delta = z[:, :2]-z[i, :2]
        d2 = np.sum(delta*delta, axis=1)
        f = np.exp(-d2/rng.uniform(.035, .14))
        s = rng.uniform(.12, .44) * (1.4 if large else 1.)
        rot = np.column_stack((-delta[:, 1], delta[:, 0]))
        z[:, :2] += f[:, None]*(rng.choice([-1., 1.])*s*rot +
                                rng.normal(0, .023, 2))
        z[:, :2] += rng.normal(0, .009, (N, 2))
    else:
        s = rng.uniform(.022, .061) if large else rng.uniform(.009, .037)
        z[:, :2] += rng.normal(0, s, (N, 2))
        z[:, 2] += rng.normal(0, .014, N)
    return z


def random_seed():
    # Jittered rotated triangular lattice clipped to the square.
    if rng.random() < .66:
        q = np.array([(i+.5*(j % 2), j*np.sqrt(.75))
                      for i in range(-8, 9) for j in range(-8, 9)])
        a = rng.uniform(0, np.pi/3)
        rot = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
        xy = (q @ rot)*rng.uniform(.173, .199) + .5 + rng.uniform(-.09, .09, 2)
        priority = np.max(np.abs(xy-.5), axis=1)+rng.uniform(0, .025, len(xy))
        xy = xy[np.argsort(priority)[:N]]
        xy = np.clip(xy, .085, .915) + rng.normal(0, .021, (N, 2))
    else:
        counts = np.full(5, 5)
        counts[rng.integers(5)] += 1
        for _ in range(rng.integers(4)):
            a, b = rng.integers(5, size=2)
            if counts[a] > 3 and counts[b] < 7:
                counts[a] -= 1
                counts[b] += 1
        xy = rows_seed(counts, rng.random() < .6)[:, :2]
        xy += rng.normal(0, .057, (N, 2))
    return np.column_stack((xy, np.full(N, .091)))


def main():
    archive = []
    fallback = rows_seed([5, 5, 6, 5, 5], False)
    fallback[:, 2] = .07
    best = fallback
    best_score = best[:, 2].sum()
    ones = np.ones(N)

    def register(c):
        nonlocal best, best_score
        c = safe(c)
        if c is None:
            return None
        sc = c[:, 2].sum()
        sig = np.sort(c[:, 2])
        if sc > best_score:
            best, best_score = c, sc
        for oldscore, oldsig, oldc in archive:
            if abs(oldscore-sc) < .00012 and np.linalg.norm(oldsig-sig) < .0018:
                return (sc, c)
        archive.append((sc, sig, c))
        archive.sort(key=lambda a: -a[0])
        del archive[36:]
        return (sc, c)

    def solve(z, weight, reg, bias, floor, steps):
        z = soft(z, weight, reg, bias, floor, steps)
        c = exact(z)
        _, _, r, _, _, d = geometry(c)
        if np.min(d-r[I]-r[J]) < -3e-6 and time.monotonic() < DEADLINE-.24:
            c = exact(c, True)
        return register(c)

    lib = structured()
    cur = None
    for t, seed in enumerate(lib):
        if time.monotonic() > min(DEADLINE-1., START+14.):
            break
        seed = seed + rng.normal(0, .006 if t < 15 else .014, seed.shape)
        item = solve(seed, 66., 1.5, ones, .037, 130)
        if item is not None and (cur is None or item[0] > cur[0]):
            cur = item

    step = 0
    while time.monotonic() < DEADLINE-.22:
        phase = step % 43
        if archive and (phase == 0 or cur is None):
            lim = min(len(archive), 22)
            rank = min(lim-1, int(rng.exponential(4.7)))
            cur = archive[rank][0], archive[rank][2]

        fresh = cur is None or rng.random() < (.24 if step < 90 else .125)
        large = phase < 13 or rng.random() < .13
        if fresh:
            z = random_seed()
        else:
            parent = cur[1]
            if rng.random() < .19 and archive:
                rank = min(len(archive)-1, int(rng.exponential(4.5)))
                parent = archive[rank][2]
            z = mutate(parent, large)

        w = rng.choice([27., 45., 70., 110., 170.])
        reg = rng.choice([0., .6, 2., 4.5, 8.],
                         p=[.25, .25, .23, .20, .07])
        floor = rng.choice([.012, .043, .062], p=[.30, .48, .22])
        bias = ones if rng.random() < .57 else 1+rng.normal(0, .075, N)
        item = solve(z, w, reg, bias, floor, 115 if fresh or large else 85)
        if item is not None:
            temp = .0055*(.14**(phase/42.))
            if cur is None or item[0] >= cur[0] or (
                item[0] > cur[0]-.029 and
                rng.random() < np.exp((item[0]-cur[0])/temp)
            ):
                cur = item
        step += 1

    print(json.dumps({"circles": best.tolist()}, separators=(",", ":")))


if __name__ == "__main__":
    main()
