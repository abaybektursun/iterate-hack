Circle packing, n = 26. Place 26 non-overlapping circles inside the unit square [0, 1] x [0, 1] so that the sum of
their radii is as large as possible.

Your program is run as `python solution.py` with a 60 s wall-clock limit, one CPU core, and Python 3 with numpy
and scipy available (no network). It must print, as its last line of standard output, one JSON object:
{"circles": [[x, y, r], ... 26 entries]}.

Validity: every r > 0; every circle lies inside the square (x - r >= 0, x + r <= 1, same for y); no two circles
overlap (distance between centres >= r_i + r_j). A tolerance of 1e-9 is allowed. An invalid output scores nothing.
Score: the sum of the 26 radii (higher is better). The best published values are about 2.635-2.636.
