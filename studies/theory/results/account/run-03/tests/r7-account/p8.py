"""p8: fit, share of math500-rl-T1 gap problems in loop (recipe defines only R1: B cap hit and rule A). refuted_by: none (a fit)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-rl-T1", "loop", refuted=lambda m: False, loop_only=True)
