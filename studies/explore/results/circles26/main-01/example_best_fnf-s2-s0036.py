import json
import math
import random

random.seed(1)

N = 26

def valid(cs):
    for i, (x, y, r) in enumerate(cs):
        if r <= 0 or x - r < -1e-10 or x + r > 1 + 1e-10 or y - r < -1e-10 or y + r > 1 + 1e-10:
            return False
        for j in range(i + 1, len(cs)):
            x2, y2, r2 = cs[j]
            if (x - x2) ** 2 + (y - y2) ** 2 < (r + r2 - 1e-10) ** 2:
                return False
    return True

def score(cs):
    return sum(r for _, _, r in cs)

# Start from a known valid packing.
circles = [[0.1 + 0.2 * i, 0.1 + 0.2 * j, 0.1] for i in range(5) for j in range(5)]
circles.append([0.2, 0.2, 0.041])  # small gap circle

def max_r_for(i, cs):
    x, y, _ = cs[i]
    r = min(x, 1 - x, y, 1 - y)
    for j, (x2, y2, r2) in enumerate(cs):
        if i == j:
            continue
        d = math.hypot(x - x2, y - y2)
        r = min(r, d - r2)
    return max(r, 1e-12)

# Initial tighten
for i in range(N):
    circles[i][2] = min(circles[i][2], max_r_for(i, circles) * 0.999999)

best = [c[:] for c in circles]
best_score = score(best)

# Strict hill-climbing: move centers a tiny bit, then re-tighten only the moved circle.
steps = [0.02, 0.012, 0.007, 0.004, 0.002]
for step in steps:
    for _ in range(12000):
        i = random.randrange(N)
        cand = [c[:] for c in best]
        x, y, r = cand[i]

        # Try a tiny random move.
        ang = random.random() * 2 * math.pi
        dist = random.random() * step
        nx = min(1 - 1e-12, max(1e-12, x + dist * math.cos(ang)))
        ny = min(1 - 1e-12, max(1e-12, y + dist * math.sin(ang)))
        cand[i][0] = nx
        cand[i][1] = ny

        # Re-tighten only this circle; if this increases score while keeping validity, accept.
        nr = max_r_for(i, cand) * 0.999999
        cand[i][2] = nr

        if valid(cand) and score(cand) > best_score + 1e-15:
            best = cand
            best_score = score(cand)

# Try local deterministic coordinate nudges on circles with the most slack.
for _ in range(2000):
    slack = []
    for i, (x, y, r) in enumerate(best):
        mr = max_r_for(i, best)
        slack.append((mr - r, i))
    slack.sort(reverse=True)

    improved = False
    for _, i in slack[:8]:
        x, y, r = best[i]
        for dx, dy in [(0.003,0), (-0.003,0), (0,0.003), (0,-0.003),
                       (0.002,0.002), (0.002,-0.002), (-0.002,0.002), (-0.002,-0.002)]:
            cand = [c[:] for c in best]
            cand[i][0] = min(1 - 1e-12, max(1e-12, x + dx))
            cand[i][1] = min(1 - 1e-12, max(1e-12, y + dy))
            cand[i][2] = max_r_for(i, cand) * 0.999999
            if valid(cand):
                sc = score(cand)
                if sc > best_score + 1e-15:
                    best = cand
                    best_score = sc
                    improved = True
                    break
        if improved:
            break
    if not improved:
        break

# Final safety shrink pass.
for i in range(N):
    best[i][2] = min(best[i][2], max_r_for(i, best) * 0.999999)

if not valid(best):
    # Absolute fallback: original valid grid.
    best = [[0.1 + 0.2 * i, 0.1 + 0.2 * j, 0.1] for i in range(5) for j in range(5)]
    best.append([0.2, 0.2, (math.sqrt(2) - 1) * 0.1 * 0.999])

print(json.dumps({"circles": best}))
