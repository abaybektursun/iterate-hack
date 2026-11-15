"""p7: math500-null-T1 gap problems minus base-only problems (both counts printed on the info line). refuted_by: net below -9 or
above 3."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r7_common import net_main

net_main("math500-null-T1", refuted=lambda m: m < -9 or m > 3)
