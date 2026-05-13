"""Revenue and regret calculations for replication experiments."""

import os
import sys
import logging

import numpy as np

sys.path.append(os.getcwd())

from ire.model.demand import DemandParameters, expected_demand

logger = logging.getLogger(__name__)


def expected_revenue(
    price: float,
    reference_price: float,
    params: DemandParameters
) -> float:
    """Compute expected single-period revenue.

    Parameters:
        price: Posted price.
        reference_price: Current reference price.
        params: Demand and reference-effect parameters.
    """

    demand = expected_demand(price, reference_price, params)
    return float(price * demand)


def benchmark_revenue(
    period: int,
    initial_reference_price: float,
    p_star: float,
    params: DemandParameters
) -> float:
    """Compute the fixed-price clairvoyant benchmark used for PSB comparison.

    Parameters:
        period: One-indexed time period.
        initial_reference_price: Initial reference price for the simulation path.
        p_star: Full-information static optimal price.
        params: Demand and reference-effect parameters.
    """

    zeta_power = np.float64(params.zeta) ** np.float64(period - 1)
    reference_gap = initial_reference_price - p_star
    demand = (
        params.alpha
        - params.beta * p_star
        + params.eta_plus * max(0.0, reference_gap) * zeta_power
        - params.eta_minus * max(0.0, -reference_gap) * zeta_power
    )
    return float(p_star * demand)
