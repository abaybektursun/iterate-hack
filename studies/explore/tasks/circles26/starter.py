import json

# 5 x 5 grid of equal circles, plus one small circle in a gap: a valid but weak packing.
r = 0.1
circles = [[0.1 + 0.2 * i, 0.1 + 0.2 * j, r] for i in range(5) for j in range(5)]
gap = (2 ** 0.5 - 1) * r  # largest circle that fits between four touching circles
circles.append([0.2, 0.2, gap * 0.999])
print(json.dumps({"circles": circles}))
