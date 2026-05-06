from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass
class ExperimentConfig:
    topology: str = "sample"
    num_steps: int = 30
    history_window: int = 4
    train_steps: int = 18
    seed: int = 7
    load_scale: float = 1.0
    output_subdir: str = "default"
    method_profile: str = "all"
    experiment_label: str = ""
    ablation_family: str = ""
    ablation_variant: str = ""
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "topology": self.topology,
            "num_steps": self.num_steps,
            "history_window": self.history_window,
            "train_steps": self.train_steps,
            "seed": self.seed,
            "load_scale": self.load_scale,
            "output_subdir": self.output_subdir,
            "method_profile": self.method_profile,
            "experiment_label": self.experiment_label,
            "ablation_family": self.ablation_family,
            "ablation_variant": self.ablation_variant,
            "enable_lstm": self.enable_lstm,
            "enable_transformer": self.enable_transformer,
            "transformer_model_dim": self.transformer_model_dim,
            "transformer_num_heads": self.transformer_num_heads,
            "transformer_num_layers": self.transformer_num_layers,
            "transformer_dropout": self.transformer_dropout,
            "transformer_epochs": self.transformer_epochs,
            "transformer_learning_rate": self.transformer_learning_rate,
            "transformer_batch_size": self.transformer_batch_size,
            "enable_robust_baseline": self.enable_robust_baseline,
            "enable_uncertainty_aware_method": self.enable_uncertainty_aware_method,
            "robust_max_scenarios": self.robust_max_scenarios,
            "robust_num_central_scenarios": self.robust_num_central_scenarios,
            "robust_include_random_scenario": self.robust_include_random_scenario,
            "robust_nominal_weight": self.robust_nominal_weight,
            "robust_worst_case_weight": self.robust_worst_case_weight,
            "uncertainty_multiplier": self.uncertainty_multiplier,
            "uncertainty_predictor_name": self.uncertainty_predictor_name,
        }
