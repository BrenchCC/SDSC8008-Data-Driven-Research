"""Least-squares estimators for the replication policies."""

import logging
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


@dataclass
class OnlineLeastSquares:
    """Cumulative sufficient statistics for y = alpha - beta * price.

    Parameters:
        count: Number of observations.
        sum_x: Sum of transformed regressor x = -price.
        sum_y: Sum of observed demands.
        sum_xx: Sum of x squared.
        sum_xy: Sum of x times observed demand.
    """

    count: int = 0
    sum_x: float = 0.0
    sum_y: float = 0.0
    sum_xx: float = 0.0
    sum_xy: float = 0.0

    def update(self, price: float, demand: float) -> None:
        """Add one price-demand observation.

        Parameters:
            price: Posted price for the observation.
            demand: Realized demand for the observation.
        """

        x_value = -float(price)
        y_value = float(demand)
        self.count += 1
        self.sum_x += x_value
        self.sum_y += y_value
        self.sum_xx += x_value * x_value
        self.sum_xy += x_value * y_value

    def estimate(self) -> tuple[float, float]:
        """Estimate alpha and positive beta from cumulative statistics.

        Parameters:
            None: This method uses the instance's cumulative statistics.
        """

        if self.count < 2:
            raise ValueError("At least two observations are required for least squares.")

        matrix = np.array(
            [
                [float(self.count), self.sum_x],
                [self.sum_x, self.sum_xx],
            ],
            dtype = np.float64
        )
        vector = np.array([self.sum_y, self.sum_xy], dtype = np.float64)
        alpha_hat, beta_hat = np.linalg.solve(matrix, vector)
        return float(alpha_hat), float(beta_hat)


def least_squares_estimate(prices: ArrayLike, demands: ArrayLike) -> tuple[float, float]:
    """Estimate alpha and positive beta from price-demand arrays.

    Parameters:
        prices: Historical posted prices.
        demands: Historical realized demands.
    """

    price_array = np.asarray(prices, dtype = np.float64)
    demand_array = np.asarray(demands, dtype = np.float64)
    if price_array.size < 2:
        raise ValueError("At least two observations are required for least squares.")

    x_values = -price_array.reshape(-1)
    y_values = demand_array.reshape(-1)
    design = np.column_stack(
        [
            np.ones_like(x_values, dtype = np.float64),
            x_values,
        ]
    )
    alpha_hat, beta_hat = np.linalg.lstsq(design, y_values, rcond = None)[0]
    return float(alpha_hat), float(beta_hat)


def estimated_optimal_price(
    alpha_hat: float,
    beta_hat: float,
    price_lower: float,
    price_upper: float
) -> float:
    """Compute and clip the estimated optimal fixed price.

    Parameters:
        alpha_hat: Estimated demand intercept.
        beta_hat: Estimated positive price-sensitivity coefficient.
        price_lower: Lower admissible price.
        price_upper: Upper admissible price.
    """

    if np.isclose(beta_hat, 0.0):
        candidate = np.inf
    else:
        candidate = alpha_hat / (2.0 * beta_hat)
    return float(np.clip(candidate, price_lower, price_upper))
