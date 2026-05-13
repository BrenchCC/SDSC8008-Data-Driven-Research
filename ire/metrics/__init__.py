"""Metric package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from ire.metrics.regret import expected_revenue
from ire.metrics.regret import benchmark_revenue
