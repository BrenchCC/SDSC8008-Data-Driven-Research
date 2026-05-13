"""Demand model for the dynamic pricing replication."""

import logging
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


@dataclass(frozen = True)
class DemandParameters:
    """Container for model parameters.

    Parameters:
        alpha: Base demand intercept.
        beta: Positive price-sensitivity coefficient in alpha - beta * price.
        eta_plus: Gain-side reference effect coefficient.
        eta_minus: Loss-side reference effect coefficient.
        sigma: Standard deviation of additive demand shock.
        zeta: Exponential smoothing coefficient for reference price.
        price_lower: Lower admissible price.
        price_upper: Upper admissible price.
    """

    alpha: float = 1.1
    beta: float = 0.5
    eta_plus: float = 0.1
    eta_minus: float = 0.3
    sigma: float = 0.1
    zeta: float = 0.1
    price_lower: float = 0.5
    price_upper: float = 1.5


def expected_demand(
    price: ArrayLike,
    reference_price: ArrayLike,
    params: DemandParameters
) -> np.ndarray:
    """Compute expected demand under asymmetric reference effects.

    Parameters:
        price: Current posted price.
        reference_price: Current consumer reference price.
        params: Demand and reference-effect parameters.
    """

    price_array = np.asarray(price, dtype = np.float64)
    reference_array = np.asarray(reference_price, dtype = np.float64)
    gain_gap = np.maximum(0.0, reference_array - price_array)
    loss_gap = np.maximum(0.0, price_array - reference_array)
    demand = (
        params.alpha
        - params.beta * price_array
        + params.eta_plus * gain_gap
        - params.eta_minus * loss_gap
    )
    return np.asarray(demand, dtype = np.float64)


def realized_demand(
    price: ArrayLike,
    reference_price: ArrayLike,
    shock: ArrayLike,
    params: DemandParameters
) -> np.ndarray:
    """Compute realized demand by adding the demand shock.

    Parameters:
        price: Current posted price.
        reference_price: Current consumer reference price.
        shock: Additive mean-zero demand shock.
        params: Demand and reference-effect parameters.
    """

    shock_array = np.asarray(shock, dtype = np.float64)
    return expected_demand(price, reference_price, params) + shock_array


def optimal_static_price(params: DemandParameters) -> float:
    """Compute the full-information fixed price alpha / (2 beta).

    Parameters:
        params: Demand and reference-effect parameters.
    """

    price = params.alpha / (2.0 * params.beta)
    return float(np.clip(price, params.price_lower, params.price_upper))


def clip_price(price: ArrayLike, params: DemandParameters) -> np.ndarray:
    """Clip a price to the admissible price interval.

    Parameters:
        price: Candidate price value.
        params: Demand and reference-effect parameters.
    """

    price_array = np.asarray(price, dtype = np.float64)
    clipped = np.clip(price_array, params.price_lower, params.price_upper)
    return np.asarray(clipped, dtype = np.float64)
