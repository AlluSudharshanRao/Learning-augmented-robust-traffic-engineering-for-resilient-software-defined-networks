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
    output_subdir: str = "default"
    enable_lstm: bool = True

    @classmethod
    def from_json(cls, path: Path) -> "ExperimentConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)
