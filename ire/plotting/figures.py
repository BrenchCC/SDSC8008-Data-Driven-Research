"""Plotting utilities for replication and extension figures."""

import os
import sys
import csv
import logging
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())

from ire.utils.result_io import ensure_directory

logger = logging.getLogger(__name__)


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    """Load an NPZ file into a dictionary.

    Parameters:
        path: Path to the NPZ file.
    """

    with np.load(path) as data:
        return {key: np.asarray(data[key], dtype = np.float64) for key in data.files}


def _save_figure(figure: plt.Figure, output_path: Path) -> None:
    """Save a figure in PNG and PDF format.

    Parameters:
        figure: Matplotlib figure to save.
        output_path: Output path without extension.
    """

    figure.savefig(output_path.with_suffix(".png"), dpi = 200, bbox_inches = "tight")
    figure.savefig(output_path.with_suffix(".pdf"), bbox_inches = "tight")
    plt.close(figure)


def _series_mean(value: np.ndarray) -> np.ndarray:
    """Return a one-dimensional mean series.

    Parameters:
        value: One-dimensional series or two-dimensional path matrix.
    """

    value_array = np.asarray(value, dtype = np.float64)
    if value_array.ndim == 1:
        return value_array
    if value_array.ndim == 2:
        return value_array.mean(axis = 1)
    raise ValueError("Only one-dimensional or two-dimensional arrays are supported.")


def _plot_three_view_grid(
    rows: list[tuple[str, np.ndarray, np.ndarray | None, int]],
    title: str,
    y_label: str,
    y_limit: tuple[float, float] | None = None,
    p_star: float | None = None
) -> plt.Figure:
    """Create PSB, IRE, and overlay panels in one figure.

    Parameters:
        rows: Row labels with PSB array, IRE array, and start period.
        title: Figure title.
        y_label: Y-axis label.
        y_limit: Optional fixed y-axis limits.
        p_star: Optional benchmark price line.
    """

    figure, axes = plt.subplots(
        len(rows),
        3,
        figsize = (14.0, 3.2 * len(rows)),
        squeeze = False
    )
    column_titles = ["PSB", "IRE", "Overlay"]

    for row_index, (row_label, psb_value, ire_value, start_period) in enumerate(rows):
        psb_series = _series_mean(psb_value)
        psb_periods = np.arange(
            start_period,
            start_period + psb_series.size,
            dtype = np.int64
        )
        ire_series = None if ire_value is None else _series_mean(ire_value)
        ire_periods = None
        if ire_series is not None:
            ire_periods = np.arange(
                start_period,
                start_period + ire_series.size,
                dtype = np.int64
            )

        max_period = int(psb_periods[-1])
        if ire_periods is not None:
            max_period = max(max_period, int(ire_periods[-1]))

        if y_limit is None:
            data_max = float(np.nanmax(psb_series))
            if ire_series is not None:
                data_max = max(data_max, float(np.nanmax(ire_series)))
            lower_limit = min(0.0, float(np.nanmin(psb_series)))
            upper_limit = max(20.0, data_max * 1.08)
            row_limit = (lower_limit, upper_limit)
        else:
            row_limit = y_limit

        plot_specs = [
            ("PSB", psb_periods, psb_series, "black", "-", "PSB"),
            ("IRE", ire_periods, ire_series, "#1f77b4", "--", "IRE"),
        ]

        for col_index, axis in enumerate(axes[row_index]):
            axis.set_title(f"{column_titles[col_index]} | {row_label}")
            axis.set_xlim(0, max_period)
            axis.set_ylim(*row_limit)
            axis.set_xlabel("Period")
            axis.grid(alpha = 0.2)
            if col_index == 0:
                axis.set_ylabel(y_label)

            if p_star is not None:
                axis.axhline(
                    p_star,
                    color = "#6c6c6c",
                    linestyle = ":",
                    linewidth = 1.3,
                    label = "p*"
                )

            if col_index in [0, 2]:
                axis.plot(
                    plot_specs[0][1],
                    plot_specs[0][2],
                    color = plot_specs[0][3],
                    linestyle = plot_specs[0][4],
                    linewidth = 2.0,
                    label = plot_specs[0][5]
                )
            if col_index in [1, 2] and ire_series is not None and ire_periods is not None:
                axis.plot(
                    plot_specs[1][1],
                    plot_specs[1][2],
                    color = plot_specs[1][3],
                    linestyle = plot_specs[1][4],
                    linewidth = 1.8,
                    label = plot_specs[1][5]
                )
            if col_index == 1 and ire_series is None:
                axis.text(
                    0.5,
                    0.5,
                    "IRE result not found",
                    ha = "center",
                    va = "center",
                    transform = axis.transAxes
                )
            if col_index == 2:
                axis.legend(loc = "best", frameon = False)

    figure.suptitle(title)
    figure.tight_layout()
    return figure


def _plot_figure4(
    psb_result: dict[str, np.ndarray],
    ire_result: dict[str, np.ndarray] | None,
    title: str,
    p_star: float = 1.1
) -> plt.Figure:
    """Create Figure 4 reference and price-estimate three-view panels.

    Parameters:
        psb_result: PSB arrays.
        ire_result: IRE arrays or None.
        title: Figure title.
        p_star: Full-information static optimal price.
    """

    return _plot_three_view_grid(
        [
            (
                "reference price",
                psb_result["reference_paths"],
                None if ire_result is None else ire_result["reference_paths"],
                1
            ),
            (
                "estimated price",
                psb_result["price_paths"],
                None if ire_result is None else ire_result["price_paths"],
                4
            ),
        ],
        title,
        "Price",
        y_limit = (0.5, 1.5),
        p_star = p_star
    )


def _maybe_load_ire_result(results_directory: Path, policy: str, scenario: str) -> dict[str, np.ndarray] | None:
    """Load an IRE result file if it exists.

    Parameters:
        results_directory: Root results directory.
        policy: Policy directory name.
        scenario: Scenario directory name.
    """

    path = results_directory / policy / scenario / "simulation_result.npz"
    if not path.exists():
        return None
    return _load_npz(path)


def _final_mean(value: np.ndarray, key: str) -> float:
    """Return the final scalar or final-row mean for comparison summaries.

    Parameters:
        value: Array to summarize.
        key: Array key used for error messages.
    """

    value_array = np.asarray(value, dtype = np.float64)
    if value_array.ndim == 1:
        return float(value_array[-1])
    if value_array.ndim == 2:
        return float(value_array[-1, :].mean())
    raise ValueError(f"Cannot summarize array for key: {key}")


def _write_comparison_summary(
    output_path: Path,
    rows: list[dict[str, str | float]]
) -> None:
    """Write comparison summary rows to CSV.

    Parameters:
        output_path: CSV file path.
        rows: Summary rows to write.
    """

    fieldnames = [
        "figure",
        "policy",
        "scenario",
        "metric",
        "psb_value",
        "ire_value",
        "absolute_difference",
        "relative_difference_percent",
    ]
    with output_path.open("w", encoding = "utf-8", newline = "") as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _add_summary_row(
    rows: list[dict[str, str | float]],
    figure_name: str,
    policy_name: str,
    scenario_name: str,
    metric_name: str,
    psb_value: float,
    ire_value: float | None
) -> None:
    """Append one metric row to the comparison summary.

    Parameters:
        rows: Mutable summary row list.
        figure_name: Paper figure identifier.
        policy_name: Policy name.
        scenario_name: Scenario name.
        metric_name: Metric label.
        psb_value: Final PSB value.
        ire_value: Final IRE value or None.
    """

    if ire_value is None:
        absolute_difference = np.nan
        relative_difference = np.nan
    else:
        absolute_difference = ire_value - psb_value
        relative_difference = (
            100.0 * absolute_difference / psb_value
            if not np.isclose(psb_value, 0.0)
            else np.nan
        )
    rows.append(
        {
            "figure": figure_name,
            "policy": policy_name,
            "scenario": scenario_name,
            "metric": metric_name,
            "psb_value": psb_value,
            "ire_value": np.nan if ire_value is None else ire_value,
            "absolute_difference": absolute_difference,
            "relative_difference_percent": relative_difference,
        }
    )


def _plot_robust_heatmap(
    candidate_summary: pd.DataFrame,
    value_column: str,
    title: str,
    axis: plt.Axes
) -> None:
    """Plot one robust-calibration heatmap.

    Parameters:
        candidate_summary: Candidate-level RARC summary table.
        value_column: Metric column to draw.
        title: Panel title.
        axis: Matplotlib axis to draw on.
    """

    c_0_values = sorted(candidate_summary["c_0"].unique())
    decay_values = sorted(candidate_summary["delta_decay_power"].unique())
    grid = np.full((len(decay_values), len(c_0_values)), np.nan, dtype = np.float64)
    role_grid: dict[tuple[int, int], str] = {}

    for row in candidate_summary.itertuples(index = False):
        row_index = decay_values.index(float(row.delta_decay_power))
        col_index = c_0_values.index(float(row.c_0))
        grid[row_index, col_index] = float(getattr(row, value_column))
        role_grid[(row_index, col_index)] = str(row.role)

    image = axis.imshow(grid, cmap = "viridis_r", aspect = "auto")
    axis.set_title(title)
    axis.set_xticks(range(len(c_0_values)))
    axis.set_xticklabels([f"{value:.2f}" for value in c_0_values])
    axis.set_yticks(range(len(decay_values)))
    axis.set_yticklabels([f"{value:.2f}" for value in decay_values])
    axis.set_xlabel("c0")
    axis.set_ylabel("delta decay")

    for row_index in range(grid.shape[0]):
        for col_index in range(grid.shape[1]):
            role = role_grid.get((row_index, col_index), "candidate")
            markers = []
            if "default" in role:
                markers.append("D")
            if "mean-best" in role:
                markers.append("M")
            if "minimax-best" in role:
                markers.append("R")
            suffix = f"\n{','.join(markers)}" if markers else ""
            axis.text(
                col_index,
                row_index,
                f"{grid[row_index, col_index]:.2f}{suffix}",
                ha = "center",
                va = "center",
                color = "white" if grid[row_index, col_index] > np.nanmean(grid) else "black",
                fontsize = 8
            )
    plt.colorbar(image, ax = axis, fraction = 0.046, pad = 0.04)


def _plot_robust_calibration(results_directory: Path) -> plt.Figure:
    """Create the RARC robust-calibration figure.

    Parameters:
        results_directory: Root results directory.
    """

    candidate_path = results_directory / "robust_calibration" / "candidate_summary.csv"
    if not candidate_path.exists():
        raise FileNotFoundError(f"Missing RARC candidate summary: {candidate_path}")

    candidate_summary = pd.read_csv(candidate_path)
    figure, axes = plt.subplots(1, 3, figsize = (15.5, 4.4))
    _plot_robust_heatmap(
        candidate_summary,
        "mean_final_regret",
        "Average final regret",
        axes[0]
    )
    _plot_robust_heatmap(
        candidate_summary,
        "worst_final_regret",
        "Worst-case final regret",
        axes[1]
    )

    role_colors = {
        "candidate": "#8a8a8a",
        "default": "#1f77b4",
        "mean-best": "#2ca02c",
        "minimax-best": "#d62728",
    }
    for row in candidate_summary.itertuples(index = False):
        role = str(row.role)
        color = "#9467bd" if ";" in role else role_colors.get(role, "#8a8a8a")
        axes[2].scatter(
            float(row.mean_final_regret),
            float(row.worst_final_regret),
            color = color,
            s = 70,
            alpha = 0.85
        )
        if role != "candidate":
            axes[2].annotate(
                role,
                (float(row.mean_final_regret), float(row.worst_final_regret)),
                textcoords = "offset points",
                xytext = (5, 5),
                fontsize = 8
            )
    axes[2].set_title("Robustness frontier")
    axes[2].set_xlabel("Average final regret")
    axes[2].set_ylabel("Worst-case final regret")
    axes[2].grid(alpha = 0.25)
    figure.suptitle("Reference-Aware Robust Calibration (RARC)")
    figure.tight_layout()
    return figure


def _load_replication_inputs(
    processed_path: Path,
    results_path: Path
) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, dict[str, np.ndarray] | None]]:
    """Load PSB and IRE arrays for Figures 2 through 5.

    Parameters:
        processed_path: Directory containing converted PSB files.
        results_path: Directory containing IRE files.
    """

    psb_results = {
        "det_no": _load_npz(processed_path / "deterministic_testing" / "no_reference" / "psb_result.npz"),
        "det_ref": _load_npz(processed_path / "deterministic_testing" / "reference_effect" / "psb_result.npz"),
        "slow_no": _load_npz(processed_path / "slow_moving" / "no_reference" / "psb_result.npz"),
        "slow_ref": _load_npz(processed_path / "slow_moving" / "reference_effect" / "psb_result.npz"),
    }
    ire_results = {
        "det_no": _maybe_load_ire_result(results_path, "deterministic_testing", "no_reference"),
        "det_ref": _maybe_load_ire_result(results_path, "deterministic_testing", "reference_effect"),
        "slow_no": _maybe_load_ire_result(results_path, "slow_moving", "no_reference"),
        "slow_ref": _maybe_load_ire_result(results_path, "slow_moving", "reference_effect"),
    }
    return psb_results, ire_results


def plot_selected_figures(
    figure: str,
    processed_directory: str | Path,
    results_directory: str | Path
) -> list[Path]:
    """Generate selected PSB/IRE comparison and extension figures.

    Parameters:
        figure: Figure selector: figure2, figure3, figure4, figure5, robust_calibration, or all.
        processed_directory: Directory containing converted PSB files.
        results_directory: Directory containing IRE and extension files.
    """

    processed_path = Path(processed_directory)
    results_path = Path(results_directory)
    figure_directory = ensure_directory(results_path / "figures")
    created: list[Path] = []
    selected = (
        ["figure2", "figure3", "figure4", "figure5", "robust_calibration"]
        if figure == "all"
        else [figure]
    )
    replication_figures = {"figure2", "figure3", "figure4", "figure5"}
    figure_builders: dict[str, Callable[[], plt.Figure]] = {}

    if any(figure_name in replication_figures for figure_name in selected):
        psb_results, ire_results = _load_replication_inputs(processed_path, results_path)
        summary_rows: list[dict[str, str | float]] = []

        for figure_name, policy_name, scenario_name, psb_key, ire_key, array_key, metric_name in [
            ("figure2", "deterministic_testing", "no_reference", "det_no", "det_no", "output", "final_mean_regret"),
            ("figure2", "deterministic_testing", "reference_effect", "det_ref", "det_ref", "output", "final_mean_regret"),
            ("figure3", "deterministic_testing", "no_reference", "det_no", "det_no", "price_paths", "final_mean_price_estimate"),
            ("figure3", "deterministic_testing", "reference_effect", "det_ref", "det_ref", "price_paths", "final_mean_price_estimate"),
            ("figure4", "slow_moving", "reference_effect", "slow_ref", "slow_ref", "reference_paths", "final_mean_reference_price"),
            ("figure4", "slow_moving", "reference_effect", "slow_ref", "slow_ref", "price_paths", "final_mean_price_estimate"),
            ("figure5", "slow_moving", "no_reference", "slow_no", "slow_no", "output", "final_mean_regret"),
            ("figure5", "slow_moving", "reference_effect", "slow_ref", "slow_ref", "output", "final_mean_regret"),
        ]:
            ire_result = ire_results[ire_key]
            _add_summary_row(
                summary_rows,
                figure_name,
                policy_name,
                scenario_name,
                metric_name,
                _final_mean(psb_results[psb_key][array_key], array_key),
                None if ire_result is None else _final_mean(ire_result[array_key], array_key)
            )

        figure_builders.update(
            {
                "figure2": lambda: _plot_three_view_grid(
                    [
                        ("no reference effect", psb_results["det_no"]["output"], None if ire_results["det_no"] is None else ire_results["det_no"]["output"], 1),
                        ("reference effect", psb_results["det_ref"]["output"], None if ire_results["det_ref"] is None else ire_results["det_ref"]["output"], 1),
                    ],
                    "Figure 2: deterministic testing regret",
                    "Cumulative regret"
                ),
                "figure3": lambda: _plot_three_view_grid(
                    [
                        ("no reference effect", psb_results["det_no"]["price_paths"], None if ire_results["det_no"] is None else ire_results["det_no"]["price_paths"], 3),
                        ("reference effect", psb_results["det_ref"]["price_paths"], None if ire_results["det_ref"] is None else ire_results["det_ref"]["price_paths"], 3),
                    ],
                    "Figure 3: deterministic testing estimated prices",
                    "Estimated price",
                    y_limit = (0.5, 1.5),
                    p_star = 1.1
                ),
                "figure4": lambda: _plot_figure4(
                    psb_results["slow_ref"],
                    ire_results["slow_ref"],
                    "Figure 4: slow-moving paths"
                ),
                "figure5": lambda: _plot_three_view_grid(
                    [
                        ("no reference effect", psb_results["slow_no"]["output"], None if ire_results["slow_no"] is None else ire_results["slow_no"]["output"], 1),
                        ("reference effect", psb_results["slow_ref"]["output"], None if ire_results["slow_ref"] is None else ire_results["slow_ref"]["output"], 1),
                    ],
                    "Figure 5: slow-moving regret",
                    "Cumulative regret"
                ),
            }
        )

        summary_path = figure_directory / "comparison_summary.csv"
        _write_comparison_summary(summary_path, summary_rows)
        created.append(summary_path)

    if "robust_calibration" in selected:
        figure_builders["robust_calibration"] = lambda: _plot_robust_calibration(results_path)

    for figure_name in selected:
        if figure_name not in figure_builders:
            raise ValueError(f"Unknown figure selector: {figure_name}")
        figure_object = figure_builders[figure_name]()
        output_stem = figure_name if figure_name == "robust_calibration" else f"{figure_name}_comparison"
        output_path = figure_directory / output_stem
        _save_figure(figure_object, output_path)
        created.extend([output_path.with_suffix(".png"), output_path.with_suffix(".pdf")])

    return created
