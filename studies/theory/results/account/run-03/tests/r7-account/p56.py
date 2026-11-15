"""p56: math500-s0100-T06 gap count minus base-only count (B = base F_math500 sample 0, RL = s0100 P_math500 sample 0, both v3
regrade). refuted_by: net below -12 or above 32."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("math500-s0100-T06", refuted=lambda m: m < -12 or m > 32)
