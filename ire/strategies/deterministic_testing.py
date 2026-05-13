"""Deterministic-testing policy used for Figures 2 and 3."""

import os
import sys
import logging
from typing import Any

import numpy as np

sys.path.append(os.getcwd())

from ire.model.demand import DemandParameters
from ire.model.demand import expected_demand
from ire.model.demand import optimal_static_price
from ire.model.reference import update_exponential_reference
from ire.metrics.regret import benchmark_revenue, expected_revenue
from ire.estimators.least_squares import OnlineLeastSquares, estimated_optimal_price

logger = logging.getLogger(__name__)


def run_deterministic_testing(
    params: DemandParameters,
    t_max: int = 10000,
    n_sim: int = 10,
    seed: int = 20260513,
    increment: int = 10,
    scenario_name: str = "reference_effect"
) -> dict[str, Any]:
    """Run iterated least squares with deterministic testing.

    Parameters:
        params: Demand and reference-effect parameters.
        t_max: Number of time periods.
        n_sim: Number of simulation replications.
        seed: Base deterministic random seed.
        increment: Plotting increment used by the published study package.
        scenario_name: Scenario label stored in metadata.
    """

    prices = np.zeros((t_max, n_sim), dtype = np.float64)
    demands = np.zeros((t_max, n_sim), dtype = np.float64)
    regret = np.zeros((t_max, n_sim), dtype = np.float64)
    reference_paths = np.zeros((t_max, n_sim), dtype = np.float64)
    price_paths = np.zeros((t_max - 2, n_sim), dtype = np.float64)
    initial_reference_prices = np.zeros(n_sim, dtype = np.float64)

    p_star = optimal_static_price(params)
    test_price_1 = params.price_lower + (params.price_upper - params.price_lower) / 3.0
    test_price_2 = params.price_lower + 2.0 * (params.price_upper - params.price_lower) / 3.0

    for sim_index in range(n_sim):
        rng = np.random.default_rng(seed + sim_index)
        shocks = rng.normal(0.0, params.sigma, size = t_max).astype(np.float64)
        initial_reference_price = float(rng.uniform(params.price_lower, params.price_upper))
        initial_reference_prices[sim_index] = initial_reference_price
        reference_price = initial_reference_price
        cycle = 0
        cumulative_regret = 0.0
        current_price_estimate = np.nan
        estimator = OnlineLeastSquares()

        for period_index in range(t_max):
            period = period_index + 1
            if period == 1 + 2 * cycle + cycle * (cycle + 1) // 2:
                cycle += 1
                price = test_price_1
            elif period == 2 + 2 * (cycle - 1) + (cycle - 1) * cycle // 2:
                price = test_price_2
            else:
                alpha_hat, beta_hat = estimator.estimate()
                current_price_estimate = estimated_optimal_price(
                    alpha_hat,
                    beta_hat,
                    params.price_lower,
                    params.price_upper
                )
                price = current_price_estimate

            expected = float(expected_demand(price, reference_price, params))
            realized = expected + shocks[period_index]
            policy_revenue = expected_revenue(price, reference_price, params)
            benchmark = benchmark_revenue(period, initial_reference_price, p_star, params)
            cumulative_regret += benchmark - policy_revenue

            prices[period_index, sim_index] = price
            demands[period_index, sim_index] = realized
            regret[period_index, sim_index] = cumulative_regret

            reference_price = float(update_exponential_reference(reference_price, price, params.zeta))
            reference_paths[period_index, sim_index] = reference_price
            estimator.update(price, realized)

            if period > 2:
                if np.isnan(current_price_estimate):
                    alpha_hat, beta_hat = estimator.estimate()
                    current_price_estimate = estimated_optimal_price(
                        alpha_hat,
                        beta_hat,
                        params.price_lower,
                        params.price_upper
                    )
                price_paths[period - 3, sim_index] = current_price_estimate

    metadata = {
        "policy_name": "deterministic_testing",
        "scenario_name": scenario_name,
        "seed": seed,
        "t_max": t_max,
        "n_sim": n_sim,
        "increment": increment,
        "alpha": params.alpha,
        "beta_positive_notation": params.beta,
        "eta_plus": params.eta_plus,
        "eta_minus": params.eta_minus,
        "sigma": params.sigma,
        "zeta": params.zeta,
        "p_min": params.price_lower,
        "p_max": params.price_upper,
        "p_star": p_star,
        "test_price_1": test_price_1,
        "test_price_2": test_price_2,
        "reproduction_note": "Deterministic IRE random stream is used; exact PSB random-stream matching is not attempted.",
    }

    return {
        "prices": prices,
        "demands": demands,
        "regret": regret,
        "output": regret.mean(axis = 1),
        "price_paths": price_paths,
        "reference_paths": reference_paths,
        "initial_reference_prices": initial_reference_prices,
        "price_path_start_period": 3,
        "metadata": metadata,
    }
