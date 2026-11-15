"""p41: share of hard328-theta05-T1 gap problems no rule takes (ordered rules R1..R5). refuted_by: share above 0.03."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import share_main

share_main("hard328-theta05-T1", "unassigned", refuted=lambda m: m > 0.03)
