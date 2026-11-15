"""p35: math500-code-T1 gap count minus base-only count (B = per_problem t1, RL = Code-RL cue 162452-0203 score_v3).
refuted_by: net below 35 or above 44."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("math500-code-T1", refuted=lambda m: m < 35 or m > 44)
