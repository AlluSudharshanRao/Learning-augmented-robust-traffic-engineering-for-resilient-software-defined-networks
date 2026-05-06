from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any

import pandas as pd

from teproject.config import ExperimentConfig
from teproject.experiment import run_default_experiment


def get_default_ablation_variants() -> dict[str, list[dict[str, Any]]]:
    return {
        "transformer": [
            {
                "variant": "base",
                "overrides": {
                    "method_profile": "ml_only",
                    "enable_transformer": True,
                    "enable_robust_baseline": False,
                    "enable_uncertainty_aware_method": False,
                    "history_window": 4,
                    "transformer_model_dim": 64,
                    "transformer_num_heads": 4,
                    "transformer_num_layers": 2,
                    "transformer_dropout": 0.1,
                    "transformer_epochs": 100,
                    "transformer_learning_rate": 8e-3,
                    "transformer_batch_size": 8,
                },
            },
            {
                "variant": "tuned_a",
                "overrides": {
                    "method_profile": "ml_only",
                    "enable_transformer": True,
                    "enable_robust_baseline": False,
                    "enable_uncertainty_aware_method": False,
                    "history_window": 6,
                    "transformer_model_dim": 96,
                    "transformer_num_heads": 4,
                    "transformer_num_layers": 2,
                    "transformer_dropout": 0.05,
                    "transformer_epochs": 140,
                    "transformer_learning_rate": 3e-3,
                    "transformer_batch_size": 8,
                },
            },
            {
                "variant": "tuned_b",
                "overrides": {
                    "method_profile": "ml_only",
                    "enable_transformer": True,
                    "enable_robust_baseline": False,
                    "enable_uncertainty_aware_method": False,
                    "history_window": 8,
                    "transformer_model_dim": 128,
                    "transformer_num_heads": 8,
                    "transformer_num_layers": 2,
                    "transformer_dropout": 0.1,
                    "transformer_epochs": 160,
                    "transformer_learning_rate": 1e-3,
                    "transformer_batch_size": 8,
                },
            },
            {
                "variant": "tuned_c",
                "overrides": {
                    "method_profile": "ml_only",
                    "enable_transformer": True,
                    "enable_robust_baseline": False,
                    "enable_uncertainty_aware_method": False,
                    "history_window": 6,
                    "transformer_model_dim": 128,
                    "transformer_num_heads": 4,
                    "transformer_num_layers": 3,
                    "transformer_dropout": 0.1,
                    "transformer_epochs": 150,
                    "transformer_learning_rate": 3e-3,
                    "transformer_batch_size": 8,
                },
            },
        ],
        "uncertainty": [
            {
                "variant": "mult_0p1",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.1,
                },
            },
            {
                "variant": "mult_0p25",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.25,
                },
            },
            {
                "variant": "mult_0p4",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.4,
                },
            },
            {
                "variant": "mult_0p5",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.5,
                },
            },
        ],
        "robust": [
            {
                "variant": "nominal_s2",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.25,
                    "robust_max_scenarios": 2,
                    "robust_num_central_scenarios": 1,
                    "robust_include_random_scenario": False,
                    "robust_nominal_weight": 0.7,
                    "robust_worst_case_weight": 0.3,
                },
            },
            {
                "variant": "balanced_s3",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.25,
                    "robust_max_scenarios": 3,
                    "robust_num_central_scenarios": 1,
                    "robust_include_random_scenario": False,
                    "robust_nominal_weight": 0.5,
                    "robust_worst_case_weight": 0.5,
                },
            },
            {
                "variant": "conservative_s4",
                "overrides": {
                    "method_profile": "lp_only",
                    "enable_transformer": False,
                    "enable_robust_baseline": True,
                    "enable_uncertainty_aware_method": True,
                    "uncertainty_multiplier": 0.25,
                    "robust_max_scenarios": 4,
                    "robust_num_central_scenarios": 2,
                    "robust_include_random_scenario": True,
                    "robust_nominal_weight": 0.35,
                    "robust_worst_case_weight": 0.65,
                },
            },
        ],
    }


def run_ablation_suite(
    *,
    output_dir: Path,
    base_config: ExperimentConfig,
    topologies: list[str],
    seeds: list[int],
    load_scale: float,
    families: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    variants_by_family = get_default_ablation_variants()
    selected_families = families or list(variants_by_family.keys())

    summary_frames: list[pd.DataFrame] = []
    run_index_rows: list[dict[str, object]] = []

    for family in selected_families:
        family_dir = output_dir / family
        family_dir.mkdir(parents=True, exist_ok=True)
        for variant in variants_by_family[family]:
            variant_name = str(variant["variant"])
            overrides = dict(variant["overrides"])
            for topology in topologies:
                for seed in seeds:
                    subdir = family_dir / f"{variant_name}_{topology}_load{str(load_scale).replace('.', 'p')}_seed{seed}"
                    existing_summary_path = subdir / "summary_results.csv"
                    existing_manifest_path = subdir / "experiment_manifest.json"
                    config = replace(
                        base_config,
                        topology=topology,
                        seed=seed,
                        load_scale=load_scale,
                        output_subdir=subdir.name,
                        experiment_label=f"{family}:{variant_name}",
                        ablation_family=family,
                        ablation_variant=variant_name,
                        **overrides,
                    )
                    if existing_summary_path.exists():
                        summary = pd.read_csv(existing_summary_path)
                    else:
                        result = run_default_experiment(output_dir=subdir, config=config)
                        summary = result["summary"].copy()
                    summary["topology"] = topology
                    summary["seed"] = seed
                    summary["load_scale"] = load_scale
                    summary["ablation_family"] = family
                    summary["ablation_variant"] = variant_name
                    summary["experiment_label"] = config.experiment_label
                    summary["method_profile"] = config.method_profile
                    summary["history_window"] = config.history_window
                    summary["transformer_model_dim"] = config.transformer_model_dim
                    summary["transformer_num_heads"] = config.transformer_num_heads
                    summary["transformer_num_layers"] = config.transformer_num_layers
                    summary["transformer_dropout"] = config.transformer_dropout
                    summary["transformer_epochs"] = config.transformer_epochs
                    summary["transformer_learning_rate"] = config.transformer_learning_rate
                    summary["robust_max_scenarios"] = config.robust_max_scenarios
                    summary["robust_num_central_scenarios"] = config.robust_num_central_scenarios
                    summary["robust_include_random_scenario"] = int(config.robust_include_random_scenario)
                    summary["robust_nominal_weight"] = config.robust_nominal_weight
                    summary["robust_worst_case_weight"] = config.robust_worst_case_weight
                    summary["uncertainty_multiplier_config"] = config.uncertainty_multiplier
                    summary_frames.append(summary)
                    run_index_rows.append(
                        {
                            "ablation_family": family,
                            "ablation_variant": variant_name,
                            "topology": topology,
                            "seed": seed,
                            "load_scale": load_scale,
                            "method_profile": config.method_profile,
                            "output_subdir": str(subdir.relative_to(output_dir)),
                            "manifest_path": str(existing_manifest_path.relative_to(output_dir)),
                        }
                    )

    all_summaries = pd.concat(summary_frames, ignore_index=True) if summary_frames else pd.DataFrame()
    all_summaries.to_csv(output_dir / "all_run_summaries.csv", index=False)

    aggregated = (
        all_summaries.groupby(
            [
                "ablation_family",
                "ablation_variant",
                "topology",
                "load_scale",
                "method",
                "method_profile",
                "history_window",
                "transformer_model_dim",
                "transformer_num_heads",
                "transformer_num_layers",
                "transformer_dropout",
                "transformer_epochs",
                "transformer_learning_rate",
                "robust_max_scenarios",
                "robust_num_central_scenarios",
                "robust_include_random_scenario",
                "robust_nominal_weight",
                "robust_worst_case_weight",
                "uncertainty_multiplier_config",
            ],
            dropna=False,
        )
        .agg(
            prediction_mae_mean=("prediction_mae", "mean"),
            prediction_rmse_mean=("prediction_rmse", "mean"),
            nominal_max_utilization_mean=("nominal_max_utilization", "mean"),
            nominal_max_utilization_std=("nominal_max_utilization", "std"),
            critical_failure_reopt_max_utilization_mean=("critical_failure_reopt_max_utilization", "mean"),
            critical_failure_fixed_disrupted_fraction_mean=("critical_failure_fixed_disrupted_fraction", "mean"),
            critical_failure_fixed_fairness_mean=("critical_failure_fixed_fairness", "mean"),
            random_failure_fixed_disrupted_fraction_mean=("random_failure_fixed_disrupted_fraction", "mean"),
            random_failure_fixed_fairness_mean=("random_failure_fixed_fairness", "mean"),
            robust_worst_case_utilization_mean=("robust_worst_case_utilization", "mean"),
        )
        .reset_index()
    )
    aggregated.to_csv(output_dir / "aggregated_summary.csv", index=False)

    run_index = pd.DataFrame(run_index_rows)
    run_index.to_csv(output_dir / "run_index.csv", index=False)

    manifest = {
        "suite": "focused_ablation",
        "topologies": topologies,
        "seeds": seeds,
        "load_scale": load_scale,
        "families": selected_families,
        "variant_catalog": {family: [v["variant"] for v in variants_by_family[family]] for family in selected_families},
    }
    (output_dir / "ablation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "all_run_summaries": all_summaries,
        "aggregated_summary": aggregated,
        "run_index": run_index,
    }
