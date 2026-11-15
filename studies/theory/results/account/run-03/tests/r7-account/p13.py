"""p13: fit, share of math500-rl-T1 gap problems no rule takes (ordered rules R1..R5). refuted_by: none (a fit)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-rl-T1", "unassigned", refuted=lambda m: False)
