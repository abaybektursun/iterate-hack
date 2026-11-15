"""p4: share of math500-null-T1 gap problems in reliability (ordered rules R1..R5). refuted_by: share below 0.22 or above 0.50."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("math500-null-T1", "reliability", refuted=lambda m: m < 0.22 or m > 0.50)
