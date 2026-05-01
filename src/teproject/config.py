from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ExperimentConfig:
    topology: str = "sample"
    num_steps: int = 30
    history_window: int = 4
    train_steps: int = 18
    seed: int = 7
    load_scale: float = 1.0
    output_subdir: str = "default"
    enable_lstm: bool = True
    enable_robust_baseline: bool = True
    robust_max_scenarios: int = 3
    robust_num_central_scenarios: int = 1
    robust_include_random_scenario: bool = False
    robust_nominal_weight: float = 0.5
    robust_worst_case_weight: float = 0.5

    @classmethod
    def from_json(cls, path: Path) -> "ExperimentConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)
