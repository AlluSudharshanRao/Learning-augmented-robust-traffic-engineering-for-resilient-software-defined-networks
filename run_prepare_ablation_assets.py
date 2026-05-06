import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.ablation_reporting import prepare_ablation_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare report-ready ablation tables and figures.")
    parser.add_argument(
        "--sweep-dir",
        type=Path,
        default=ROOT / "outputs" / "ablations_final",
        help="Directory containing ablation aggregated_summary.csv.",
    )
    args = parser.parse_args()

    outputs = prepare_ablation_assets(args.sweep_dir)
    print("Prepared ablation assets:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
