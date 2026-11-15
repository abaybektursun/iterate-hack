"""p2: share of math500-null-T1 gap problems in budget (ordered rules R1..R5). refuted_by: share below 0.12 or above 0.36."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-null-T1", "budget", refuted=lambda m: m < 0.12 or m > 0.36)
