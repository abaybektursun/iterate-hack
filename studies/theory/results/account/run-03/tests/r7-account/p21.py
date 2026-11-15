"""p21: hard328-rl-T1 gap count minus base-only count (B = e72c, RL = 86ef, stored score_v3). refuted_by: net below 39 or above 43."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("hard328-rl-T1", refuted=lambda m: m < 39 or m > 43)
