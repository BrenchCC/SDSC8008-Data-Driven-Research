"""Robust calibration experiment for slow-moving pricing."""

import os
import sys
import logging
from itertools import product
from typing import Any

import numpy as np
import pandas as pd

sys.path.append(os.getcwd())

from ire.model.demand import DemandParameters
from ire.strategies.slow_moving import run_slow_moving

logger = logging.getLogger(__name__)


DEFAULT_ZETA_VALUES = [0.02, 0.10, 0.40]
DEFAULT_ETA_MINUS_VALUES = [0.15, 0.30, 0.45]
DEFAULT_C0_VALUES = [0.05, 0.10, 0.15]
DEFAULT_DECAY_VALUES = [0.20, 0.25, 0.30]


def _candidate_id(c_0: float, delta_decay_power: float) -> str:
    """Create a stable candidate identifier.

    Parameters:
        c_0: Perturbation scale.
        delta_decay_power: Perturbation decay exponent.
    """

    c0_text = str(c_0).replace(".", "_")
    decay_text = str(delta_decay_power).replace(".", "_")
    return f"c0_{c0_text}_decay_{decay_text}"


def _role_labels(
    c_0: float,
    delta_decay_power: float,
    mean_best: tuple[float, float],
    minimax_best: tuple[float, float]
) -> str:
    """Return the role labels attached to one candidate.

    Parameters:
        c_0: Perturbation scale.
        delta_decay_power: Perturbation decay exponent.
        mean_best: Candidate with the lowest average final regret.
        minimax_best: Candidate with the lowest worst-case final regret.
    """

    labels = []
    if np.isclose(c_0, 0.10) and np.isclose(delta_decay_power, 0.25):
        labels.append("default")
    if np.isclose(c_0, mean_best[0]) and np.isclose(delta_decay_power, mean_best[1]):
        labels.append("mean-best")
    if np.isclose(c_0, minimax_best[0]) and np.isclose(delta_decay_power, minimax_best[1]):
        labels.append("minimax-best")
    return ";".join(labels) if labels else "candidate"


def _summarize_candidates(summary_frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize environment-level rows by policy candidate.

    Parameters:
        summary_frame: RARC environment-candidate result table.
    """

    candidate_summary = (
        summary_frame
        .groupby(["candidate_id", "c_0", "delta_decay_power"], as_index = False)
        .agg(
            mean_final_regret = ("final_mean_regret", "mean"),
            worst_final_regret = ("final_mean_regret", "max"),
            mean_path_regret = ("mean_path_regret", "mean"),
            final_reference_price = ("final_mean_reference_price", "mean"),
            final_price_estimate = ("final_mean_price_estimate", "mean"),
        )
    )
    candidate_summary["rank_by_mean"] = (
        candidate_summary["mean_final_regret"].rank(method = "min").astype(int)
    )
    candidate_summary["rank_by_worst"] = (
        candidate_summary["worst_final_regret"].rank(method = "min").astype(int)
    )

    mean_row = candidate_summary.sort_values(
        ["mean_final_regret", "worst_final_regret", "c_0", "delta_decay_power"]
    ).iloc[0]
    minimax_row = candidate_summary.sort_values(
        ["worst_final_regret", "mean_final_regret", "c_0", "delta_decay_power"]
    ).iloc[0]
    mean_best = (float(mean_row["c_0"]), float(mean_row["delta_decay_power"]))
    minimax_best = (float(minimax_row["c_0"]), float(minimax_row["delta_decay_power"]))

    candidate_summary["role"] = [
        _role_labels(float(row.c_0), float(row.delta_decay_power), mean_best, minimax_best)
        for row in candidate_summary.itertuples(index = False)
    ]
    return candidate_summary


def run_robust_calibration(
    t_max: int = 10000,
    n_sim: int = 10,
    seed: int = 20260513,
    increment: int = 10,
    zeta_values: list[float] | None = None,
    eta_minus_values: list[float] | None = None,
    c_0_values: list[float] | None = None,
    delta_decay_values: list[float] | None = None
) -> dict[str, Any]:
    """Run Reference-Aware Robust Calibration experiments.

    Parameters:
        t_max: Number of time periods.
        n_sim: Number of simulation replications.
        seed: Base deterministic random seed.
        increment: Plotting increment.
        zeta_values: Candidate reference-memory parameters.
        eta_minus_values: Candidate loss-side reference-effect coefficients.
        c_0_values: Candidate perturbation scales.
        delta_decay_values: Candidate perturbation decay exponents.
    """

    zeta_grid = DEFAULT_ZETA_VALUES if zeta_values is None else zeta_values
    eta_minus_grid = DEFAULT_ETA_MINUS_VALUES if eta_minus_values is None else eta_minus_values
    c_0_grid = DEFAULT_C0_VALUES if c_0_values is None else c_0_values
    decay_grid = DEFAULT_DECAY_VALUES if delta_decay_values is None else delta_decay_values
    rows: list[dict[str, float | str | bool]] = []

    for c_0, delta_decay_power, zeta, eta_minus in product(
        c_0_grid,
        decay_grid,
        zeta_grid,
        eta_minus_grid
    ):
        logger.info(
            "Running RARC candidate c_0=%.3f, decay=%.3f, zeta=%.3f, eta_minus=%.3f",
            c_0,
            delta_decay_power,
            zeta,
            eta_minus
        )
        params = DemandParameters(
            alpha = 1.1,
            beta = 0.5,
            eta_plus = 0.1,
            eta_minus = float(eta_minus),
            sigma = 0.1,
            zeta = float(zeta),
            price_lower = 0.5,
            price_upper = 1.5
        )
        result = run_slow_moving(
            params = params,
            t_max = t_max,
            n_sim = n_sim,
            seed = seed,
            increment = increment,
            scenario_name = "robust_calibration",
            c_0 = float(c_0),
            delta_decay_power = float(delta_decay_power)
        )
        output = np.asarray(result["output"], dtype = np.float64)
        regret = np.asarray(result["regret"], dtype = np.float64)
        candidate = _candidate_id(float(c_0), float(delta_decay_power))
        rows.append(
            {
                "candidate_id": candidate,
                "c_0": float(c_0),
                "delta_decay_power": float(delta_decay_power),
                "zeta": float(zeta),
                "eta_plus": 0.1,
                "eta_minus": float(eta_minus),
                "final_mean_regret": float(output[-1]),
                "mean_path_regret": float(output.mean()),
                "final_regret_std": float(regret[-1, :].std(ddof = 1)) if n_sim > 1 else 0.0,
                "final_mean_reference_price": float(result["reference_paths"][-1, :].mean()),
                "final_mean_price_estimate": float(result["price_paths"][-1, :].mean()),
                "is_default_candidate": bool(
                    np.isclose(c_0, 0.10) and np.isclose(delta_decay_power, 0.25)
                ),
            }
        )

    summary_frame = pd.DataFrame(rows)
    candidate_summary = _summarize_candidates(summary_frame)
    environment_summary = (
        summary_frame
        .groupby(["zeta", "eta_minus"], as_index = False)
        .agg(
            mean_final_regret = ("final_mean_regret", "mean"),
            best_final_regret = ("final_mean_regret", "min"),
            worst_final_regret = ("final_mean_regret", "max"),
        )
    )
    metadata = {
        "experiment_name": "Reference-Aware Robust Calibration",
        "short_name": "RARC",
        "t_max": t_max,
        "n_sim": n_sim,
        "seed": seed,
        "increment": increment,
        "zeta_values": zeta_grid,
        "eta_plus": 0.1,
        "eta_minus_values": eta_minus_grid,
        "c_0_values": c_0_grid,
        "delta_decay_values": decay_grid,
        "default_candidate": {"c_0": 0.10, "delta_decay_power": 0.25},
        "selection_rule": "mean-best minimizes average final regret; minimax-best minimizes worst-case final regret.",
    }

    return {
        "summary": summary_frame,
        "candidate_summary": candidate_summary,
        "environment_summary": environment_summary,
        "metadata": metadata,
    }
