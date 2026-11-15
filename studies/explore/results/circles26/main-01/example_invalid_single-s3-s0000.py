import json
import math

circles = []

# Four corner circles
r_corner = 0.1464
circles += [
    [r_corner, r_corner, r_corner],
    [1 - r_corner, r_corner, r_corner],
    [r_corner, 1 - r_corner, r_corner],
    [1 - r_corner, 1 - r_corner, r_corner],
]

# Four side circles
r_side = 0.1185
circles += [
    [0.5, r_side, r_side],
    [0.5, 1 - r_side, r_side],
    [r_side, 0.5, r_side],
    [1 - r_side, 0.5, r_side],
]

# Central 3x3 pattern of moderately large circles
r_mid = 0.0825
coords = [0.32, 0.5, 0.68]
for x in coords:
    for y in coords:
        circles.append([x, y, r_mid])

# Small circles in remaining gaps
small = [
    (0.18, 0.32), (0.18, 0.68), (0.32, 0.18), (0.32, 0.82),
    (0.68, 0.18), (0.68, 0.82), (0.82, 0.32), (0.82, 0.68),
]
r_small = 0.0495
for x, y in small:
    circles.append([x, y, r_small])

# One center filler
circles.append([0.5, 0.5, 0.041])

# Ensure exactly 26 circles
assert len(circles) == 26

print(json.dumps({"circles": circles}))
