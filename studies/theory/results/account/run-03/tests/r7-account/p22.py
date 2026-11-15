"""p22: fit, share of math500-s2800-T06 gap problems in loop (ordered rules R1..R5). refuted_by: none (a fit)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-s2800-T06", "loop", refuted=lambda m: False)
