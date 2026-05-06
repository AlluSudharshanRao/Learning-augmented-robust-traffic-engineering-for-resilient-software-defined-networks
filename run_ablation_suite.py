import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.ablation import run_ablation_suite
from teproject.config import ExperimentConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run focused ablation experiments.")
    parser.add_argument(
        "--base-config",
        type=str,
        default=str(ROOT / "configs" / "nsfnet_transformer.json"),
        help="Base JSON config used as a template for ablation runs.",
    )
    parser.add_argument(
        "--topologies",
        nargs="+",
        default=["abilene", "nsfnet"],
        help="Topologies to evaluate.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=[7, 11, 13],
        help="Seeds for repeated evaluation.",
    )
    parser.add_argument(
        "--load-scale",
        type=float,
        default=1.0,
        help="Single load scale for focused ablations.",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        default=["transformer", "uncertainty", "robust"],
        help="Ablation families to run.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "outputs" / "ablations_final"),
        help="Folder for ablation outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_config = ExperimentConfig.from_json(Path(args.base_config))
    results = run_ablation_suite(
        output_dir=Path(args.output_dir),
        base_config=base_config,
        topologies=args.topologies,
        seeds=args.seeds,
        load_scale=args.load_scale,
        families=args.families,
    )
    print("Saved ablation outputs to:", Path(args.output_dir))
    print()
    print(results["aggregated_summary"].round(4).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
