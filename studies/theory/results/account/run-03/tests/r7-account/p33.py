"""p33: share of math500-code-T1 gap problems in deliberation (ordered rules R1..R5). refuted_by: share below 0.30 or above 0.56."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-code-T1", "deliberation", refuted=lambda m: m < 0.30 or m > 0.56)
