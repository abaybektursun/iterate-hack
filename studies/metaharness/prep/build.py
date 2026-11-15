"""Build one arena (lib/arena.py).

  MH_HOME=<dir> python3 -m studies.metaharness.prep.build <arena id> <skill|plain> <planted|clean> <port> <base commit>
"""
import json
import sys

from studies.metaharness.lib import arena as A

arena_id, arm, variant, port, base = sys.argv[1:6]
print(json.dumps(A.build(arena_id, arm, variant, int(port), base)))
