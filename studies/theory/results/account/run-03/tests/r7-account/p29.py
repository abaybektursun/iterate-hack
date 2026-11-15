"""p29: share of math500-code-T1 gap problems in loop (recipe defines only R1: B cap hit and rule A).
refuted_by (by construction): rule A cannot take a problem -> coded as refuted if the share is above 0."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-code-T1", "loop", refuted=lambda m: m > 0, loop_only=True)
