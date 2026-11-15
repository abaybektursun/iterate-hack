"""p14: math500-rl-T1 gap count minus base-only count from per_problem.json (t1 = B, t2 = RL). refuted_by: net below 50 or above
54."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("math500-rl-T1", refuted=lambda m: m < 50 or m > 54)
