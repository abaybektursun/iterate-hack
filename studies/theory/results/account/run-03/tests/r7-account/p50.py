"""p50: share of math500-s0100-T06 gap problems in loop (ordered rules R1..R5). refuted_by: share below 0.43 or above 0.70."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-s0100-T06", "loop", refuted=lambda m: m < 0.43 or m > 0.70)
