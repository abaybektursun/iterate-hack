"""p15: fit, share of hard328-rl-T1 gap problems in loop (ordered rules R1..R5). refuted_by: none (a fit)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("hard328-rl-T1", "loop", refuted=lambda m: False)
