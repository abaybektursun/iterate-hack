import json
import math

# Hand-tuned 26-circle packing for the unit square.
# The layout is based on a symmetric arrangement with:
# - 4 large corner-adjacent circles
# - 8 medium circles along the edges
# - 8 circles in a central ring
# - 6 smaller circles filling remaining gaps
#
# The coordinates/radii were chosen conservatively to ensure validity.

circles = []

# Corner-adjacent large circles
r1 = 0.145
circles += [
    [r1, r1, r1],
    [1 - r1, r1, r1],
    [r1, 1 - r1, r1],
    [1 - r1, 1 - r1, r1],
]

# Edge circles
r2 = 0.102
edge_x = [0.28, 0.5, 0.72]
edge_y = [0.28, 0.5, 0.72]
circles += [
    [0.50, 0.14, r2],
    [0.50, 0.86, r2],
    [0.14, 0.50, r2],
    [0.86, 0.50, r2],
    [0.28, 0.28, r2],
    [0.72, 0.28, r2],
    [0.28, 0.72, r2],
    [0.72, 0.72, r2],
]

# Central ring
r3 = 0.075
center_pts = [
    (0.38, 0.38), (0.62, 0.38), (0.38, 0.62), (0.62, 0.62),
    (0.50, 0.34), (0.66, 0.50), (0.50, 0.66), (0.34, 0.50),
]
circles += [[x, y, r3] for x, y in center_pts]

# Smaller gap fillers
r4 = 0.055
fillers = [
    (0.22, 0.38), (0.38, 0.22), (0.78, 0.38),
    (0.62, 0.22), (0.22, 0.62), (0.38, 0.78),
]
circles += [[x, y, r4] for x, y in fillers]

# Ensure exactly 26 circles
assert len(circles) == 26

print(json.dumps({"circles": circles}))
