"""Core tests for dynamic pricing replication modules."""

import os
import sys

import numpy as np

sys.path.append(os.getcwd())

from model.demand import DemandParameters, expected_demand, optimal_static_price
from model.reference import update_exponential_reference
from metrics.regret import benchmark_revenue, expected_revenue
from strategies.slow_moving import run_slow_moving
from strategies.robust_calibration import run_robust_calibration
from estimators.least_squares import least_squares_estimate, estimated_optimal_price


def test_expected_demand_left_and_right_segments():
    """Check that demand uses the correct reference-effect side.

    Parameters:
        None: This test uses fixed numeric examples.
    """

    params = DemandParameters(alpha = 1.1, beta = 0.5, eta_plus = 0.1, eta_minus = 0.3)
    left = expected_demand(0.9, 1.0, params)
    right = expected_demand(1.1, 1.0, params)
    assert np.isclose(left, 1.1 - 0.5 * 0.9 + 0.1 * 0.1)
    assert np.isclose(right, 1.1 - 0.5 * 1.1 - 0.3 * 0.1)


def test_reference_price_update():
    """Check exponential reference-price updating.

    Parameters:
        None: This test uses fixed numeric examples.
    """

    updated = update_exponential_reference(1.0, 1.2, 0.1)
    assert np.isclose(updated, 0.1 * 1.0 + 0.9 * 1.2)


def test_optimal_static_price():
    """Check the clipped full-information static price.

    Parameters:
        None: This test uses default model parameters.
    """

    params = DemandParameters()
    assert np.isclose(optimal_static_price(params), 1.1)


def test_least_squares_estimator_positive_beta_notation():
    """Check OLS recovers alpha and positive beta.

    Parameters:
        None: This test constructs exact linear observations.
    """

    prices = np.array([0.8, 1.0, 1.2], dtype = np.float64)
    demands = 1.1 - 0.5 * prices
    alpha_hat, beta_hat = least_squares_estimate(prices, demands)
    assert np.isclose(alpha_hat, 1.1)
    assert np.isclose(beta_hat, 0.5)
    assert np.isclose(estimated_optimal_price(alpha_hat, beta_hat, 0.5, 1.5), 1.1)


def test_revenue_and_benchmark_use_expected_demand():
    """Check expected revenue and benchmark computations.

    Parameters:
        None: This test uses default model parameters.
    """

    params = DemandParameters(eta_plus = 0.0, eta_minus = 0.0)
    price = 1.1
    assert np.isclose(expected_revenue(price, 0.8, params), price * (1.1 - 0.5 * price))
    assert np.isclose(benchmark_revenue(1, 0.8, price, params), price * (1.1 - 0.5 * price))


def test_slow_moving_accepts_calibration_parameters():
    """Check configurable slow-moving perturbation settings.

    Parameters:
        None: This test runs a short deterministic simulation.
    """

    params = DemandParameters(eta_plus = 0.1, eta_minus = 0.3)
    result = run_slow_moving(
        params = params,
        t_max = 12,
        n_sim = 2,
        seed = 7,
        c_0 = 0.15,
        delta_decay_power = 0.30
    )
    assert np.isclose(result["metadata"]["c_0"], 0.15)
    assert np.isclose(result["metadata"]["delta_decay_power"], 0.30)
    assert np.isclose(result["metadata"]["initial_delta"], 0.15 * 2.0 ** (-0.30))
    assert result["regret"].shape == (12, 2)


def test_robust_calibration_marks_default_and_minimax_candidates():
    """Check RARC summary ranking and role labels.

    Parameters:
        None: This test runs a small robust-calibration grid.
    """

    result = run_robust_calibration(
        t_max = 12,
        n_sim = 2,
        seed = 11,
        zeta_values = [0.1],
        eta_minus_values = [0.3, 0.45],
        c_0_values = [0.05, 0.10],
        delta_decay_values = [0.25]
    )
    candidate_summary = result["candidate_summary"]
    assert set(candidate_summary["candidate_id"]) == {"c0_0_05_decay_0_25", "c0_0_1_decay_0_25"}
    assert "default" in ";".join(candidate_summary["role"].tolist())
    assert candidate_summary["rank_by_worst"].min() == 1
    assert result["summary"].shape[0] == 4
