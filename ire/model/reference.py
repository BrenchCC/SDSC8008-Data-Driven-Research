"""Reference price process for the dynamic pricing replication."""

import logging

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


def update_exponential_reference(
    reference_price: ArrayLike,
    price: ArrayLike,
    zeta: float
) -> np.ndarray:
    """Update reference price using exponential smoothing.

    Parameters:
        reference_price: Previous reference price.
        price: Current posted price.
        zeta: Smoothing coefficient in [0, 1).
    """

    reference_array = np.asarray(reference_price, dtype = np.float64)
    price_array = np.asarray(price, dtype = np.float64)
    updated = zeta * reference_array + (1.0 - zeta) * price_array
    return np.asarray(updated, dtype = np.float64)
