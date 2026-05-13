
"""Strategy package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from ire.strategies.slow_moving import run_slow_moving
from ire.strategies.robust_calibration import run_robust_calibration
from ire.strategies.deterministic_testing import run_deterministic_testing
