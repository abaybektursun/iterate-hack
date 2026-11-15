import json
import math
import numpy as np
from scipy.optimize import minimize

N = 26
DIM = 3 * N

def unpack(v):
    return v.reshape(N, 3)

def objective(v):
    return -float(np.sum(v[2::3]))

def grad_objective(v):
    g = np.zeros_like(v)
    g[2::3] = -1.0
    return g

def make_constraints():
    cons = []
    eye = np.eye(DIM)

    for i in range(N):
        k = 3 * i
        cons.append({"type": "ineq", "fun": lambda v, k=k: v[k] - v[k + 2],
                     "jac": lambda v, k=k: eye[k] - eye[k + 2]})
        cons.append({"type": "ineq", "fun": lambda v, k=k: 1.0 - v[k] - v[k + 2],
                     "jac": lambda v, k=k: -eye[k] - eye[k + 2]})
        cons.append({"type": "ineq", "fun": lambda v, k=k: v[k + 1] - v[k + 2],
                     "jac": lambda v, k=k: eye[k + 1] - eye[k + 2]})
        cons.append({"type": "ineq", "fun": lambda v, k=k: 1.0 - v[k + 1] - v[k + 2],
                     "jac": lambda v, k=k: -eye[k + 1] - eye[k + 2]})

    for i in range(N):
        ki = 3 * i
        for j in range(i + 1, N):
            kj = 3 * j

            def fun(v, ki=ki, kj=kj):
                dx = v[ki] - v[kj]
                dy = v[ki + 1] - v[kj + 1]
                rr = v[ki + 2] + v[kj + 2]
                return dx * dx + dy * dy - rr * rr

            def jac(v, ki=ki, kj=kj):
                dx = v[ki] - v[kj]
                dy = v[ki + 1] - v[kj + 1]
                rr = v[ki + 2] + v[kj + 2]
                g = np.zeros(DIM)
                g[ki] = 2.0 * dx
                g[kj] = -2.0 * dx
                g[ki + 1] = 2.0 * dy
                g[kj + 1] = -2.0 * dy
                g[ki + 2] = -2.0 * rr
                g[kj + 2] = -2.0 * rr
                return g

            cons.append({"type": "ineq", "fun": fun, "jac": jac})
    return cons

CONS = make_constraints()

def base_layout():
    # Strong geometric seed: staggered dense rows with slight asymmetry.
    pts = []
    rows = [
        (0.095, 5, 0.02),
        (0.255, 6, 0.00),
        (0.415, 5, 0.03),
        (0.585, 5, 0.00),
        (0.755, 5, 0.02),
    ]
    for y, c, shift in rows:
        xs = np.linspace(0.11, 0.89, c)
        if c == 6:
            xs = np.linspace(0.08, 0.92, c)
        xs = xs + shift
        for x in xs:
            pts.append([x, y])
    pts = np.array(pts[:N], dtype=float)

    # Hand-tuned micro-shift to break symmetry.
    tweak = np.array([
        [-0.012, 0.006], [0.006, -0.004], [0.000, 0.003], [0.004, -0.006], [0.010, 0.004],
        [-0.006, 0.000], [0.005, 0.004], [-0.004, -0.004], [0.006, 0.002], [-0.005, -0.005],
        [0.002, 0.005], [-0.008, -0.003], [0.004, 0.002], [-0.003, -0.004], [0.007, 0.004],
        [-0.005, 0.003], [0.003, -0.005], [-0.002, 0.004], [0.005, -0.003], [-0.006, 0.002],
        [0.004, 0.005], [-0.004, -0.002], [0.006, 0.003], [-0.003, -0.004], [0.003, 0.002],
        [-0.005, -0.003]
    ], dtype=float)
    pts += tweak[:N]
    pts = np.clip(pts, 0.02, 0.98)
    return pts

def estimate_radii_from_points(pts):
    r = np.full(N, 0.03, dtype=float)
    for i in range(N):
        x, y = pts[i]
        r[i] = max(1e-3, min(x, 1 - x, y, 1 - y) * 0.65)
    return r

def pack(pts, r):
    v = np.empty(DIM, dtype=float)
    v[0::3] = pts[:, 0]
    v[1::3] = pts[:, 1]
    v[2::3] = r
    return v

def feasible_repair(v, passes=60):
    v = v.copy()
    for _ in range(passes):
        changed = False

        # boundary repair
        for i in range(N):
            k = 3 * i
            x, y, r = v[k:k+3]
            maxr = min(x, 1 - x, y, 1 - y)
            if r > maxr:
                v[k + 2] = max(1e-10, 0.99 * maxr)
                changed = True

        # pairwise overlap repair: shrink larger-radius circle a bit
        for i in range(N):
            ki = 3 * i
            xi, yi, ri = v[ki:ki+3]
            for j in range(i + 1, N):
                kj = 3 * j
                xj, yj, rj = v[kj:kj+3]
                dx = xi - xj
                dy = yi - yj
                d = math.hypot(dx, dy)
                s = ri + rj
                if d < s:
                    if d < 1e-15:
                        # nudge apart deterministically
                        ang = (i * 37 + j * 91) * 0.1234567
                        nx, ny = math.cos(ang), math.sin(ang)
                        shift = 0.5 * (s + 1e-12)
                        v[ki] = min(1 - v[ki + 2], max(v[ki + 2], xi + 0.5 * shift * nx))
                        v[ki + 1] = min(1 - v[ki + 2], max(v[ki + 2], yi + 0.5 * shift * ny))
                        v[kj] = min(1 - v[kj + 2], max(v[kj + 2], xj - 0.5 * shift * nx))
                        v[kj + 1] = min(1 - v[kj + 2], max(v[kj + 2], yj - 0.5 * shift * ny))
                        xi, yi = v[ki], v[ki + 1]
                        xj, yj = v[kj], v[kj + 1]
                        d = math.hypot(xi - xj, yi - yj)
                    target = max(d * 0.999999, 1e-12)
                    scale = target / (s + 1e-15)
                    if scale < 1.0:
                        if ri >= rj:
                            v[ki + 2] *= scale
                        else:
                            v[kj + 2] *= scale
                        changed = True

        if not changed:
            break
    v[2::3] = np.maximum(v[2::3], 1e-12)
    return v

def local_opt(v, maxiter=700, ftol=1e-12):
    v = feasible_repair(v)
    res = minimize(
        objective, v, method="SLSQP", jac=grad_objective,
        constraints=CONS,
        options={"ftol": ftol, "maxiter": maxiter, "disp": False}
    )
    x = res.x if res.success else v
    return feasible_repair(x)

def score(v):
    return float(np.sum(v[2::3]))

def geom_signature(v):
    pts = v.reshape(N, 3)[:, :2]
    # coarse signature for diversity
    return tuple(np.round(pts.flatten() * 20).astype(int).tolist())

def overlap_penalty(v):
    p = 0.0
    for i in range(N):
        xi, yi, ri = v[3*i:3*i+3]
        for j in range(i + 1, N):
            xj, yj, rj = v[3*j:3*j+3]
            d = math.hypot(xi - xj, yi - yj)
            gap = d - (ri + rj)
            if gap < 0:
                p += (-gap) ** 2
    return p

def splice(p1, p2, rng):
    a = p1.reshape(N, 3).copy()
    b = p2.reshape(N, 3).copy()
    cutx = rng.uniform(0.3, 0.7)
    cuty = rng.uniform(0.3, 0.7)
    mode = rng.integers(4)
    child = a.copy()

    if mode == 0:
        mask = a[:, 0] + a[:, 2] + 1e-12 > cutx
    elif mode == 1:
        mask = a[:, 1] + a[:, 2] + 1e-12 > cuty
    elif mode == 2:
        mask = (a[:, 0] > cutx) ^ (a[:, 1] > cuty)
    else:
        mask = (a[:, 0] + a[:, 1]) > (cutx + cuty)

    child[mask] = b[mask]

    # mix a few circles based on nearest positions
    idx = rng.choice(N, size=6, replace=False)
    child[idx, :2] = 0.65 * a[idx, :2] + 0.35 * b[idx, :2]
    child[idx, 2] = np.minimum(a[idx, 2], b[idx, 2])

    child[:, :2] += rng.normal(scale=0.012, size=(N, 2))
    child[:, :2] = np.clip(child[:, :2], 0.01, 0.99)
    child[:, 2] = np.maximum(child[:, 2] * rng.uniform(0.85, 1.05, size=N), 1e-4)
    return child.reshape(-1)

def diversify_and_select(pop, k):
    # Greedy selection by score with diversity tie-break.
    selected = []
    sigs = set()
    pool = sorted(pop, key=lambda v: (-score(v), overlap_penalty(v)))
    for v in pool:
        sig = geom_signature(v)
        if sig in sigs:
            continue
        selected.append(v)
        sigs.add(sig)
        if len(selected) >= k:
            break
    if len(selected) < k:
        for v in pool:
            if len(selected) >= k:
                break
            if all(np.linalg.norm(v[0::3] - u[0::3]) > 0.01 for u in selected):
                selected.append(v)
    return selected[:k]

def make_initial_population():
    rng = np.random.default_rng(1234)
    base = base_layout()
    pts = base.copy()
    r = estimate_radii_from_points(pts)
    v0 = pack(pts, r)
    pop = []

    # Multiple structured seeds around the base.
    for t in range(12):
        vv = v0.copy()
        vv[0::3] += rng.normal(scale=0.02, size=N)
        vv[1::3] += rng.normal(scale=0.02, size=N)
        vv[0::3] = np.clip(vv[0::3], 0.02, 0.98)
        vv[1::3] = np.clip(vv[1::3], 0.02, 0.98)
        vv[2::3] *= rng.uniform(0.85, 1.08, size=N)
        pop.append(local_opt(vv, maxiter=550, ftol=1e-11))

    # Jittered grid-ish starts.
    for seed in [1, 7, 17, 29, 41]:
        rng2 = np.random.default_rng(seed)
        pts2 = base_layout()
        pts2 += rng2.normal(scale=0.03, size=pts2.shape)
        pts2 = np.clip(pts2, 0.02, 0.98)
        v2 = pack(pts2, np.full(N, 0.025))
        pop.append(local_opt(v2, maxiter=500, ftol=1e-11))

    return pop

def evolve(pop, rounds=10, offspring_per_round=14):
    rng = np.random.default_rng(999)
    archive = list(pop)

    for _ in range(rounds):
        parents = sorted(archive, key=score, reverse=True)
        elite = parents[:8]
        children = []

        for _ in range(offspring_per_round):
            p1 = elite[rng.integers(len(elite))]
            p2 = archive[rng.integers(len(archive))]
            child = splice(p1, p2, rng)
            child = feasible_repair(child)

            # small deterministic positional massage toward empty space
            for __ in range(2):
                pts = child.reshape(N, 3)
                for i in range(N):
                    x, y, r = pts[i]
                    fx = min(x - r, (1 - x) - r)
                    fy = min(y - r, (1 - y) - r)
                    if fx < 0.02:
                        pts[i, 0] = min(1 - r, max(r, x + 0.01 * (0.5 - x)))
                    if fy < 0.02:
                        pts[i, 1] = min(1 - r, max(r, y + 0.01 * (0.5 - y)))
                child = pts.reshape(-1)
                child = feasible_repair(child)

            child = local_opt(child, maxiter=450, ftol=1e-11)
            children.append(child)

        archive = diversify_and_select(archive + children, 18)

        # occasional stronger re-optimization of top few
        refined = []
        for v in sorted(archive, key=score, reverse=True)[:6]:
            refined.append(local_opt(v, maxiter=900, ftol=1e-13))
        archive = diversify_and_select(archive + refined, 18)

    return archive

def final_polish(v):
    # Multi-pass polish with tiny perturbations to escape shallow basins.
    rng = np.random.default_rng(2024)
    best = v.copy()
    best_s = score(best)
    for _ in range(12):
        cand = best.copy()
        cand[0::3] += rng.normal(scale=0.003, size=N)
        cand[1::3] += rng.normal(scale=0.003, size=N)
        cand[0::3] = np.clip(cand[0::3], 0.01, 0.99)
        cand[1::3] = np.clip(cand[1::3], 0.01, 0.99)
        cand = feasible_repair(cand)
        cand = local_opt(cand, maxiter=1200, ftol=1e-14)
        s = score(cand)
        if s > best_s:
            best, best_s = cand, s
    return best

population = make_initial_population()
population = evolve(population, rounds=11, offspring_per_round=16)

best = max(population, key=score)
best = final_polish(best)

circles = unpack(best).tolist()

# final numerical safety clamp
for i in range(N):
    x, y, r = circles[i]
    r = max(1e-12, min(r, x, 1 - x, y, 1 - y))
    circles[i] = [float(x), float(y), float(r)]

print(json.dumps({"circles": circles}))
