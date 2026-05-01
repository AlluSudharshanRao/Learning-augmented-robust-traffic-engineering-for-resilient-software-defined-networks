import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.config import ExperimentConfig
from teproject.sweep import run_experiment_sweep


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multi-configuration traffic-engineering sweeps.")
    parser.add_argument(
        "--base-config",
        type=str,
        default=str(ROOT / "configs" / "abilene.json"),
        help="Base JSON config used as a template for sweep runs.",
    )
    parser.add_argument(
        "--topologies",
        nargs="+",
        default=["abilene", "nsfnet"],
        help="Topologies to evaluate.",
    )
    parser.add_argument(
        "--load-scales",
        nargs="+",
        type=float,
        default=[0.8, 1.0, 1.2],
        help="Load scale multipliers.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=[7, 11],
        help="Random seeds for independent traffic realizations.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "outputs" / "sweeps"),
        help="Folder for aggregated sweep outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_config = ExperimentConfig.from_json(Path(args.base_config))
    results = run_experiment_sweep(
        output_dir=Path(args.output_dir),
        base_config=base_config,
        topologies=args.topologies,
        load_scales=args.load_scales,
        seeds=args.seeds,
    )
    print("Saved sweep outputs to:", Path(args.output_dir))
    print()
    print(results["aggregated_summary"].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
