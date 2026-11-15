"""p48: share of math500-s0400-T06 gap problems no rule takes (ordered rules R1..R5). refuted_by: share above 0.02."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-s0400-T06", "unassigned", refuted=lambda m: m > 0.02)
