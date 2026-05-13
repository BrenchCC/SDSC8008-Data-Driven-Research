"""Metric package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from metrics.regret import expected_revenue
from metrics.regret import benchmark_revenue
