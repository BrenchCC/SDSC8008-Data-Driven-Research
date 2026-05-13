"""Estimator package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from estimators.least_squares import OnlineLeastSquares
from estimators.least_squares import least_squares_estimate
from estimators.least_squares import estimated_optimal_price
