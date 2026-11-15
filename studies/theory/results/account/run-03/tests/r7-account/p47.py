"""p47: share of math500-s0400-T06 gap problems in deliberation (ordered rules R1..R5). refuted_by: share below 0.04 or above
0.22."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-s0400-T06", "deliberation", refuted=lambda m: m < 0.04 or m > 0.22)
