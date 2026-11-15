"""p39: share of hard328-theta05-T1 gap problems in reliability (ordered rules R1..R5). refuted_by: share below 0.17 or above
0.44."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("hard328-theta05-T1", "reliability", refuted=lambda m: m < 0.17 or m > 0.44)
