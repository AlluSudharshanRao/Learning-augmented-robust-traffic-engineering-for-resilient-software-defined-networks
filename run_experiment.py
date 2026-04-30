import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from teproject.config import ExperimentConfig
from teproject.experiment import run_default_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run traffic-engineering experiments.")
    parser.add_argument(
        "--config",
        type=str,
        default=str(ROOT / "configs" / "sample.json"),
        help="Path to a JSON experiment config.",
    )
    args = parser.parse_args()

    config = ExperimentConfig.from_json(Path(args.config))
    output_dir = ROOT / "outputs" / config.output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    run_default_experiment(output_dir=output_dir, config=config)


if __name__ == "__main__":
    main()
