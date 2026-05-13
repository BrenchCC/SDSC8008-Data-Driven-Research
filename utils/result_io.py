"""Input and output helpers for replication results."""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if needed and return it as a Path.

    Parameters:
        path: Directory path to create.
    """

    directory = Path(path)
    directory.mkdir(parents = True, exist_ok = True)
    return directory


def save_json(data: dict[str, Any], path: str | Path) -> None:
    """Save a dictionary as formatted JSON.

    Parameters:
        data: JSON-serializable dictionary.
        path: Output JSON file path.
    """

    output_path = Path(path)
    ensure_directory(output_path.parent)
    with output_path.open("w", encoding = "utf-8") as file:
        json.dump(data, file, indent = 2, ensure_ascii = False)


def matrix_to_frame(
    matrix: np.ndarray,
    start_period: int,
    column_prefix: str
) -> pd.DataFrame:
    """Convert a two-dimensional simulation matrix to a DataFrame.

    Parameters:
        matrix: Matrix with periods on rows and replications on columns.
        start_period: One-indexed period number of the first row.
        column_prefix: Prefix for replication columns.
    """

    matrix_array = np.asarray(matrix, dtype = np.float64)
    periods = np.arange(
        start_period,
        start_period + matrix_array.shape[0],
        dtype = np.int64
    )
    frame = pd.DataFrame(matrix_array)
    frame.columns = [
        f"{column_prefix}_{index + 1}"
        for index in range(matrix_array.shape[1])
    ]
    frame.insert(0, "period", periods)
    return frame


def regret_summary_frame(regret: np.ndarray) -> pd.DataFrame:
    """Create mean regret and uncertainty summary by period.

    Parameters:
        regret: Regret matrix with periods on rows and replications on columns.
    """

    regret_array = np.asarray(regret, dtype = np.float64)
    n_sim = regret_array.shape[1]
    mean_regret = regret_array.mean(axis = 1)
    std_regret = regret_array.std(axis = 1, ddof = 1) if n_sim > 1 else np.zeros_like(mean_regret)
    standard_error = std_regret / np.sqrt(float(n_sim))
    periods = np.arange(1, regret_array.shape[0] + 1, dtype = np.int64)
    return pd.DataFrame(
        {
            "period": periods,
            "mean_regret": mean_regret,
            "std_regret": std_regret,
            "standard_error": standard_error,
            "ci95_lower": mean_regret - 1.96 * standard_error,
            "ci95_upper": mean_regret + 1.96 * standard_error,
        }
    )


def save_simulation_result(result: dict[str, Any], output_directory: str | Path) -> None:
    """Save a simulation result dictionary as NPZ, CSV, and metadata JSON.

    Parameters:
        result: Simulation result dictionary returned by a strategy runner.
        output_directory: Directory where files should be written.
    """

    directory = ensure_directory(output_directory)
    np.savez_compressed(
        directory / "simulation_result.npz",
        regret = result["regret"],
        output = result["output"],
        prices = result["prices"],
        demands = result["demands"],
        price_paths = result["price_paths"],
        reference_paths = result["reference_paths"],
        initial_reference_prices = result["initial_reference_prices"],
    )
    regret_summary_frame(result["regret"]).to_csv(directory / "regret_summary.csv", index = False)
    matrix_to_frame(result["regret"], 1, "sim").to_csv(directory / "regret_paths.csv", index = False)
    matrix_to_frame(result["prices"], 1, "sim").to_csv(directory / "prices.csv", index = False)
    matrix_to_frame(result["reference_paths"], 1, "sim").to_csv(directory / "reference_paths.csv", index = False)
    matrix_to_frame(
        result["price_paths"],
        result["price_path_start_period"],
        "sim"
    ).to_csv(directory / "price_estimates.csv", index = False)
    save_json(result["metadata"], directory / "metadata.json")


def save_robust_calibration_result(result: dict[str, Any], output_directory: str | Path) -> list[Path]:
    """Save robust calibration tables and metadata.

    Parameters:
        result: Robust calibration result dictionary.
        output_directory: Directory where files should be written.
    """

    directory = ensure_directory(output_directory)
    created = [
        directory / "summary.csv",
        directory / "candidate_summary.csv",
        directory / "environment_summary.csv",
        directory / "metadata.json",
    ]
    result["summary"].to_csv(created[0], index = False)
    result["candidate_summary"].to_csv(created[1], index = False)
    result["environment_summary"].to_csv(created[2], index = False)
    save_json(result["metadata"], created[3])
    return created
