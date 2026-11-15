"""Speed of numpy's bit generators on the resampler's multinomial draw (500 problems, 500 categories).

Called by cell.py for a cell of kind bench. Reports draws per second for PCG64, MT19937, Philox and SFC64.
"""
import time

import numpy as np

GENERATORS = {"PCG64": np.random.PCG64, "MT19937": np.random.MT19937, "Philox": np.random.Philox, "SFC64": np.random.SFC64}


def run(cell):
    n = 500
    table = []
    for name, bit_generator in GENERATORS.items():
        rng = np.random.Generator(bit_generator(cell.get("seed", 0)))
        draws, began = 0, time.time()
        while time.time() - began < cell["seconds_per_generator"]:
            rng.multinomial(n, np.full(n, 1 / n), size=5000)
            draws += 5000
        table.append({"group": name, "draws_per_second": round(draws / (time.time() - began))})
        print(f"[bench] {name}: {table[-1]['draws_per_second']} draws per second", flush=True)
    return {"table": table, "seconds": {"bench": cell["seconds_per_generator"] * len(GENERATORS)}}
