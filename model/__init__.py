"""Model package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from model.demand import DemandParameters
from model.demand import expected_demand
from model.demand import optimal_static_price
from model.reference import update_exponential_reference
