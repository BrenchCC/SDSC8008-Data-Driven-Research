"""Slow-moving pricing policy used for Figures 4 and 5."""

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


def run_slow_moving(
    params: DemandParameters,
    t_max: int = 10000,
    n_sim: int = 10,
    seed: int = 20260513,
    increment: int = 10,
    scenario_name: str = "reference_effect",
    c_0: float | None = None,
    delta_decay_power: float = 0.25
) -> dict[str, Any]:
    """Run the slow-moving pricing policy.

    Parameters:
        params: Demand and reference-effect parameters.
        t_max: Number of time periods.
        n_sim: Number of simulation replications.
        seed: Base deterministic random seed.
        increment: Plotting increment used by the published study package.
        scenario_name: Scenario label stored in metadata.
        c_0: Initial perturbation scale; defaults to one tenth of the price interval.
        delta_decay_power: Exponent in the perturbation decay rule.
    """

    prices = np.zeros((t_max, n_sim), dtype = np.float64)
    demands = np.zeros((t_max, n_sim), dtype = np.float64)
    regret = np.zeros((t_max, n_sim), dtype = np.float64)
    reference_paths = np.zeros((t_max, n_sim), dtype = np.float64)
    price_paths = np.zeros((t_max - 3, n_sim), dtype = np.float64)
    initial_reference_prices = np.zeros(n_sim, dtype = np.float64)

    p_star = optimal_static_price(params)
    c_0_value = (
        (params.price_upper - params.price_lower) / 10.0
        if c_0 is None
        else float(c_0)
    )

    for sim_index in range(n_sim):
        rng = np.random.default_rng(seed + 10000 + sim_index)
        shocks = rng.normal(0.0, params.sigma, size = t_max).astype(np.float64)
        initial_reference_price = float(rng.uniform(params.price_lower, params.price_upper))
        initial_reference_prices[sim_index] = initial_reference_price
        reference_price = initial_reference_price
        cycle_begin = 0
        half_length = 2
        p_star_hat = 1.0
        delta = c_0_value * 2.0 ** (-delta_decay_power)
        cumulative_regret = 0.0
        current_price_estimate = np.nan
        estimator = OnlineLeastSquares()

        for period_index in range(t_max):
            period = period_index + 1
            if period <= cycle_begin + half_length:
                price = float(np.clip(p_star_hat - delta, params.price_lower, params.price_upper))
            elif period <= cycle_begin + 2 * half_length:
                price = float(np.clip(p_star_hat + delta, params.price_lower, params.price_upper))
            else:
                price = float(np.clip(p_star_hat, params.price_lower, params.price_upper))

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

            if period == cycle_begin + 2 * half_length:
                alpha_hat, beta_hat = estimator.estimate()
                current_price_estimate = estimated_optimal_price(
                    alpha_hat,
                    beta_hat,
                    params.price_lower,
                    params.price_upper
                )
                p_star_hat = current_price_estimate
                cycle_begin = cycle_begin + 2 * half_length
                half_length = 2 * half_length
                delta = delta * 2.0 ** (-delta_decay_power)

            estimator.update(price, realized)

            if period > 3:
                if np.isnan(current_price_estimate):
                    current_price_estimate = p_star_hat
                price_paths[period - 4, sim_index] = current_price_estimate

    metadata = {
        "policy_name": "slow_moving",
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
        "c_0": c_0_value,
        "delta_decay_power": delta_decay_power,
        "initial_p_star_hat": 1.0,
        "initial_half_episode_length": 2,
        "initial_delta": c_0_value * 2.0 ** (-delta_decay_power),
        "reproduction_note": "Policy follows the released study procedure; exact PSB random-stream matching is not attempted.",
    }

    return {
        "prices": prices,
        "demands": demands,
        "regret": regret,
        "output": regret.mean(axis = 1),
        "price_paths": price_paths,
        "reference_paths": reference_paths,
        "initial_reference_prices": initial_reference_prices,
        "price_path_start_period": 4,
        "metadata": metadata,
    }
