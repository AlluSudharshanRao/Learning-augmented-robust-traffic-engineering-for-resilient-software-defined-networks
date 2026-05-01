from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.plotting import generate_summary_plots


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate report-ready plots from aggregated sweep results.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "sweeps_full" / "aggregated_summary.csv",
        help="Path to aggregated_summary.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs" / "sweeps_full" / "plots",
        help="Directory where summary plots will be written",
    )
    args = parser.parse_args()

    created = generate_summary_plots(args.input, args.output_dir)
    print("Created plot artifacts:")
    for name, path in created.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
