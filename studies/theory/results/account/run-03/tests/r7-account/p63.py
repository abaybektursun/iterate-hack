"""p63: math500-fr-T06 gap count minus base-only count (B = base F_math500 sample 0, RL = fr P_math500 sample 0, both v3
regrade). refuted_by: net below -5 or above 55."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("math500-fr-T06", refuted=lambda m: m < -5 or m > 55)
