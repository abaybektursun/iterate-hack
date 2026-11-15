"""p46: share of math500-s0400-T06 gap problems in reliability (ordered rules R1..R5). refuted_by: share below 0.06 or above
0.25."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-s0400-T06", "reliability", refuted=lambda m: m < 0.06 or m > 0.25)
