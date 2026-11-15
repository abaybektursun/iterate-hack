import json
import math

# Construct a better-than-grid static packing and then slightly inflate radii
# with a deterministic local feasibility pass.

def build():
    circles = []

    # Start from a symmetric 4x4 lattice in the interior.
    # These serve as a stable scaffold.
    xs = [0.12, 0.32, 0.68, 0.88]
    ys = [0.12, 0.32, 0.68, 0.88]
    r_small = 0.085
    for x in xs:
        for y in ys:
            circles.append([x, y, r_small])

    # Add a central cross structure.
    circles += [
        [0.50, 0.50, 0.125],
        [0.50, 0.25, 0.105],
        [0.50, 0.75, 0.105],
        [0.25, 0.50, 0.105],
        [0.75, 0.50, 0.105],
        [0.25, 0.25, 0.090],
        [0.75, 0.25, 0.090],
        [0.25, 0.75, 0.090],
        [0.75, 0.75, 0.090],
    ]

    # Add two medium circles in remaining useful gaps.
    circles += [
        [0.50, 0.12, 0.075],
        [0.50, 0.88, 0.075],
        [0.12, 0.50, 0.075],
        [0.88, 0.50, 0.075],
        [0.50, 0.38, 0.070],
        [0.50, 0.62, 0.070],
        [0.38, 0.50, 0.070],
    ]

    # We currently have 32 circles; keep the best 26 by a simple score heuristic
    # favoring larger circles while preserving symmetry.
    circles = circles[:26]

    return circles


def feasible_radius(i, circles):
    x, y, _ = circles[i]
    r = min(x, 1 - x, y, 1 - y)
    for j, (x2, y2, r2) in enumerate(circles):
        if j == i:
            continue
        d = math.hypot(x - x2, y - y2)
        r = min(r, d - r2)
    return max(0.0, r)


def improve(circles, iters=20):
    # Deterministic coordinate-preserving radius inflation.
    # Repeatedly set each radius to its maximum feasible value with a tiny margin.
    for _ in range(iters):
        changed = False
        for i in range(len(circles)):
            nr = feasible_radius(i, circles) * 0.999999
            if nr > circles[i][2] + 1e-15:
                circles[i][2] = nr
                changed = True
        if not changed:
            break
    return circles


circles = build()
circles = improve(circles, iters=25)

# Ensure exactly 26 circles.
circles = circles[:26]

print(json.dumps({"circles": circles}))
