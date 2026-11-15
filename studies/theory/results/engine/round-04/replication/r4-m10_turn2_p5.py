"""r4-m10 rival turn 2, test 5, recomputed from the recipe alone: test 4 at RL step 400."""
import json

import importlib
run = importlib.import_module("r4-m10_turn2_p4").run

print(json.dumps(run("r3_s0400_s0100-01_out_s0400_P_math500.jsonl")))
