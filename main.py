"""Command-line entry point for the dynamic pricing replication."""

import os
import sys
import logging
import argparse
from pathlib import Path

sys.path.append(os.getcwd())

from data.conversion import convert_psb_data
from model.demand import DemandParameters
from plotting.figures import plot_selected_figures
from utils.result_io import save_simulation_result
from strategies.slow_moving import run_slow_moving
from strategies.robust_calibration import run_robust_calibration
from utils.result_io import save_robust_calibration_result
from strategies.deterministic_testing import run_deterministic_testing

logger = logging.getLogger(__name__)


DEFAULT_SOURCE_DIR = Path("data/replication_package_MS-RMA-19-01931.R2")
DEFAULT_PROCESSED_DIR = Path("data/processed")
DEFAULT_RESULTS_DIR = Path("results")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Parameters:
        None: Arguments are read from the command line.
    """

    parser = argparse.ArgumentParser(
        description = "Replicate dynamic pricing experiments with reference effects."
    )
    subparsers = parser.add_subparsers(dest = "command", required = True)

    convert_parser = subparsers.add_parser(
        "convert-data",
        help = "Convert PSB result files to NumPy and CSV."
    )
    convert_parser.add_argument(
        "--source-dir",
        type = Path,
        default = DEFAULT_SOURCE_DIR,
        help = "Directory containing released study result files."
    )
    convert_parser.add_argument(
        "--processed-dir",
        type = Path,
        default = DEFAULT_PROCESSED_DIR,
        help = "Directory for converted PSB files."
    )

    run_parser = subparsers.add_parser(
        "run",
        help = "Run IRE replication and extension experiments."
    )
    run_parser.add_argument(
        "--experiment",
        choices = ["figure2_3", "figure4_5", "robust_calibration", "all"],
        default = "all",
        help = "Experiment group to run."
    )
    run_parser.add_argument("--results-dir", type = Path, default = DEFAULT_RESULTS_DIR)
    run_parser.add_argument("--seed", type = int, default = 20260513)
    run_parser.add_argument("--t-max", type = int, default = 10000)
    run_parser.add_argument("--n-sim", type = int, default = 10)
    run_parser.add_argument("--increment", type = int, default = 10)

    plot_parser = subparsers.add_parser(
        "plot",
        help = "Generate comparison plots for Figures 2 through 5."
    )
    plot_parser.add_argument(
        "--figure",
        choices = ["figure2", "figure3", "figure4", "figure5", "robust_calibration", "all"],
        default = "all",
        help = "Figure to generate."
    )
    plot_parser.add_argument("--processed-dir", type = Path, default = DEFAULT_PROCESSED_DIR)
    plot_parser.add_argument("--results-dir", type = Path, default = DEFAULT_RESULTS_DIR)

    return parser.parse_args()


def _make_params(eta_plus: float, eta_minus: float) -> DemandParameters:
    """Create default paper parameters for one scenario.

    Parameters:
        eta_plus: Gain-side reference-effect coefficient.
        eta_minus: Loss-side reference-effect coefficient.
    """

    return DemandParameters(
        alpha = 1.1,
        beta = 0.5,
        eta_plus = eta_plus,
        eta_minus = eta_minus,
        sigma = 0.1,
        zeta = 0.1,
        price_lower = 0.5,
        price_upper = 1.5
    )


def _run_figure2_3(args: argparse.Namespace) -> None:
    """Run deterministic-testing scenarios for Figures 2 and 3.

    Parameters:
        args: Parsed command-line arguments.
    """

    scenarios = {
        "no_reference": _make_params(0.0, 0.0),
        "reference_effect": _make_params(0.1, 0.3),
    }
    for scenario_name, params in scenarios.items():
        logger.info("Running deterministic testing scenario: %s", scenario_name)
        result = run_deterministic_testing(
            params = params,
            t_max = args.t_max,
            n_sim = args.n_sim,
            seed = args.seed,
            increment = args.increment,
            scenario_name = scenario_name
        )
        save_simulation_result(
            result,
            args.results_dir / "deterministic_testing" / scenario_name
        )


def _run_figure4_5(args: argparse.Namespace) -> None:
    """Run slow-moving scenarios for Figures 4 and 5.

    Parameters:
        args: Parsed command-line arguments.
    """

    scenarios = {
        "no_reference": _make_params(0.0, 0.0),
        "reference_effect": _make_params(0.1, 0.3),
    }
    for scenario_name, params in scenarios.items():
        logger.info("Running slow-moving scenario: %s", scenario_name)
        result = run_slow_moving(
            params = params,
            t_max = args.t_max,
            n_sim = args.n_sim,
            seed = args.seed,
            increment = args.increment,
            scenario_name = scenario_name
        )
        save_simulation_result(
            result,
            args.results_dir / "slow_moving" / scenario_name
        )


def _run_robust_calibration(args: argparse.Namespace) -> None:
    """Run Reference-Aware Robust Calibration extension experiments.

    Parameters:
        args: Parsed command-line arguments.
    """

    logger.info("Running Reference-Aware Robust Calibration extension.")
    result = run_robust_calibration(
        t_max = args.t_max,
        n_sim = args.n_sim,
        seed = args.seed,
        increment = args.increment
    )
    created_files = save_robust_calibration_result(
        result,
        args.results_dir / "robust_calibration"
    )
    logger.info("Saved %d robust calibration files.", len(created_files))


def main() -> None:
    """Run the selected CLI command.

    Parameters:
        None: Command choice comes from parsed command-line arguments.
    """

    args = parse_args()

    if args.command == "convert-data":
        created_files = convert_psb_data(args.source_dir, args.processed_dir)
        logger.info("Converted %d PSB files.", len(created_files))
    elif args.command == "run":
        if args.experiment in ["figure2_3", "all"]:
            _run_figure2_3(args)
        if args.experiment in ["figure4_5", "all"]:
            _run_figure4_5(args)
        if args.experiment in ["robust_calibration", "all"]:
            _run_robust_calibration(args)
    elif args.command == "plot":
        created_files = plot_selected_figures(
            args.figure,
            args.processed_dir,
            args.results_dir
        )
        logger.info("Generated %d plot files.", len(created_files))
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [logging.StreamHandler()]
    )
    main()
