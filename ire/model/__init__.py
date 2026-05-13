"""Model package for dynamic pricing replication."""

import os
import sys

sys.path.append(os.getcwd())

from ire.model.demand import DemandParameters
from ire.model.demand import expected_demand
from ire.model.demand import optimal_static_price
from ire.model.reference import update_exponential_reference
