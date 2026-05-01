from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.reporting import prepare_report_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare report-ready tables and figures from a completed sweep.")
    parser.add_argument(
        "--sweep-dir",
        type=Path,
        default=ROOT / "outputs" / "sweeps_report",
        help="Directory containing aggregated_summary.csv and sweep subfolders.",
    )
    args = parser.parse_args()

    outputs = prepare_report_assets(args.sweep_dir)
    print("Prepared report assets:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
