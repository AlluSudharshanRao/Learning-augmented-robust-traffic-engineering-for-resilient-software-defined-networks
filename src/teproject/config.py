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
    enable_transformer: bool = False
    transformer_model_dim: int = 64
    transformer_num_heads: int = 4
    transformer_num_layers: int = 2
    transformer_dropout: float = 0.1
    transformer_epochs: int = 100
    transformer_learning_rate: float = 8e-3
    transformer_batch_size: int = 8
    enable_robust_baseline: bool = True
    enable_uncertainty_aware_method: bool = False
    robust_max_scenarios: int = 3
    robust_num_central_scenarios: int = 1
    robust_include_random_scenario: bool = False
    robust_nominal_weight: float = 0.5
    robust_worst_case_weight: float = 0.5
    uncertainty_multiplier: float = 1.0
    uncertainty_predictor_name: str = "lstm"

    @classmethod
    def from_json(cls, path: Path) -> "ExperimentConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)
