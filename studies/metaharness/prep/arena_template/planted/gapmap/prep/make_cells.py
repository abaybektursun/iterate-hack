"""Write the cells of one batch from queue.json: one cell per split, plus the extra cells, with the default settings.

  python3 studies/gapmap/prep/make_cells.py <batch>      writes studies/gapmap/cells/<batch>.json

A batch is one metric. Edit a cell in the written file to give it its own settings (interval level, table format, digits).
"""
import json
import sys
from pathlib import Path

study = Path(__file__).resolve().parent.parent
queue = json.loads((study / "queue.json").read_text())
batch = sys.argv[1]
assert batch in queue["batches"], f"batch must be one of {queue['batches']}"
cells = [{"id": split, "kind": "split", "metric": batch, "split": split, **queue["defaults"]} for split in queue["splits"]]
cells += [{"seed": queue["defaults"]["seed"], **extra} for extra in queue["extras"]]
(study / "cells").mkdir(exist_ok=True)
(study / "cells" / f"{batch}.json").write_text(json.dumps(cells, indent=1) + "\n")
print(f"{len(cells)} cells: " + ", ".join(c["id"] for c in cells))
