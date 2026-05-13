"""Estimator package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from ire.estimators.least_squares import OnlineLeastSquares
from ire.estimators.least_squares import least_squares_estimate
from ire.estimators.least_squares import estimated_optimal_price
