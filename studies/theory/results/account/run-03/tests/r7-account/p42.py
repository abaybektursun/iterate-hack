"""p42: hard328-theta05-T1 gap count minus base-only count (B = e72c, theta0.5 cue = 34ad, stored score_v3). refuted_by: net
below 21 or above 30."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("hard328-theta05-T1", refuted=lambda m: m < 21 or m > 30)
