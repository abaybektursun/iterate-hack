"""p61: share of math500-fr-T06 gap problems in deliberation (ordered rules R1..R5). refuted_by: share below 0.05 or above 0.25."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-fr-T06", "deliberation", refuted=lambda m: m < 0.05 or m > 0.25)
