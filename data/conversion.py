"""Convert PSB source files into NumPy and CSV files."""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.io import loadmat

logger = logging.getLogger(__name__)


PSB_DATASETS = {
    "data_for_figures_2a_and_3a.mat": ("deterministic_testing", "no_reference", 3),
    "data_for_figures_2b_and_3b.mat": ("deterministic_testing", "reference_effect", 3),
    "data_for_figure_5a.mat": ("slow_moving", "no_reference", 4),
    "data_for_figures_4_and_5b.mat": ("slow_moving", "reference_effect", 4),
}


def _scalar_value(value: Any) -> Any:
    """Convert scalar arrays into plain scalar values.

    Parameters:
        value: Raw value loaded from a PSB source file.
    """

    if isinstance(value, np.ndarray) and value.size == 1:
        return value.reshape(-1)[0].item()
    return None


def _matrix_frame(matrix: np.ndarray, start_period: int, column_prefix: str) -> pd.DataFrame:
    """Convert a matrix into a CSV-friendly DataFrame.

    Parameters:
        matrix: Matrix with periods on rows and replications on columns.
        start_period: One-indexed period for the first row.
        column_prefix: Prefix for matrix columns.
    """

    matrix_array = np.asarray(matrix, dtype = np.float64)
    if matrix_array.ndim == 1:
        matrix_array = matrix_array.reshape(-1, 1)
    if matrix_array.shape[0] == 1 and matrix_array.shape[1] > 1:
        matrix_array = matrix_array.reshape(-1, 1)
    periods = np.arange(start_period, start_period + matrix_array.shape[0], dtype = np.int64)
    frame = pd.DataFrame(matrix_array)
    frame.columns = [f"{column_prefix}_{index + 1}" for index in range(matrix_array.shape[1])]
    frame.insert(0, "period", periods)
    return frame


def convert_psb_data(
    source_directory: str | Path,
    output_directory: str | Path
) -> list[Path]:
    """Convert released PSB data files into structured outputs.

    Parameters:
        source_directory: Directory containing the released study files.
        output_directory: Directory where converted files should be stored.
    """

    source_path = Path(source_directory)
    output_path = Path(output_directory)
    created_files: list[Path] = []

    for file_name, (policy_name, scenario_name, price_start_period) in PSB_DATASETS.items():
        source_file_path = source_path / file_name
        if not source_file_path.exists():
            raise FileNotFoundError(f"Missing PSB source file: {source_file_path}")

        target_directory = output_path / policy_name / scenario_name
        target_directory.mkdir(parents = True, exist_ok = True)
        source_data = loadmat(source_file_path)
        arrays = {
            key: np.asarray(value)
            for key, value in source_data.items()
            if not key.startswith("__")
        }
        metadata = {
            key: _scalar_value(value)
            for key, value in arrays.items()
            if _scalar_value(value) is not None
        }
        metadata["source_file"] = file_name
        metadata["policy_name"] = policy_name
        metadata["scenario_name"] = scenario_name
        if "beta" in metadata:
            metadata["beta_psb_source_sign"] = metadata["beta"]
            metadata["beta_positive_notation"] = abs(float(metadata["beta"]))

        npz_path = target_directory / "psb_result.npz"
        np.savez_compressed(
            npz_path,
            output = np.asarray(arrays["output"], dtype = np.float64).reshape(-1),
            regret = np.asarray(arrays["regret"], dtype = np.float64),
            price_paths = np.asarray(arrays["price_paths"], dtype = np.float64),
            reference_paths = np.asarray(arrays["ref_price_paths"], dtype = np.float64),
        )
        created_files.append(npz_path)

        output_frame = pd.DataFrame(
            {
                "period": np.arange(1, arrays["output"].size + 1, dtype = np.int64),
                "mean_regret": np.asarray(arrays["output"], dtype = np.float64).reshape(-1),
            }
        )
        output_csv = target_directory / "psb_mean_regret.csv"
        output_frame.to_csv(output_csv, index = False)
        created_files.append(output_csv)

        for key, start_period, prefix, output_name in [
            ("regret", 1, "sim", "psb_regret_paths.csv"),
            ("price_paths", price_start_period, "sim", "psb_price_estimates.csv"),
            ("ref_price_paths", 1, "sim", "psb_reference_paths.csv"),
        ]:
            csv_path = target_directory / output_name
            _matrix_frame(arrays[key], start_period, prefix).to_csv(csv_path, index = False)
            created_files.append(csv_path)

        metadata_path = target_directory / "psb_metadata.json"
        with metadata_path.open("w", encoding = "utf-8") as file:
            json.dump(metadata, file, indent = 2, ensure_ascii = False)
        created_files.append(metadata_path)

    return created_files
