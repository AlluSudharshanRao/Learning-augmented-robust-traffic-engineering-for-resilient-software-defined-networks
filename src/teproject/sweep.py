from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pandas as pd

from teproject.config import ExperimentConfig
from teproject.experiment import run_default_experiment


def run_experiment_sweep(
    *,
    output_dir: Path,
    base_config: ExperimentConfig,
    topologies: list[str],
    load_scales: list[float],
    seeds: list[int],
) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_frames: list[pd.DataFrame] = []
    detailed_index_rows: list[dict[str, object]] = []

    for topology in topologies:
        for load_scale in load_scales:
            for seed in seeds:
                subdir = f"{topology}_load{str(load_scale).replace('.', 'p')}_seed{seed}"
                config = replace(
                    base_config,
                    topology=topology,
                    load_scale=load_scale,
                    seed=seed,
                    output_subdir=subdir,
                )
                result = run_default_experiment(output_dir=output_dir / subdir, config=config)
                summary = result["summary"].copy()
                summary["topology"] = topology
                summary["load_scale"] = load_scale
                summary["seed"] = seed
                summary_frames.append(summary)
                detailed_index_rows.append(
                    {
                        "topology": topology,
                        "load_scale": load_scale,
                        "seed": seed,
                        "output_subdir": subdir,
                    }
                )

    all_summaries = pd.concat(summary_frames, ignore_index=True) if summary_frames else pd.DataFrame()
    all_summaries_path = output_dir / "all_run_summaries.csv"
    all_summaries.to_csv(all_summaries_path, index=False)

    aggregated = (
        all_summaries.groupby(["topology", "load_scale", "method"])
        .agg(
            prediction_mae_mean=("prediction_mae", "mean"),
            prediction_rmse_mean=("prediction_rmse", "mean"),
            nominal_max_utilization_mean=("nominal_max_utilization", "mean"),
            nominal_max_utilization_std=("nominal_max_utilization", "std"),
            critical_failure_reopt_max_utilization_mean=("critical_failure_reopt_max_utilization", "mean"),
            random_failure_reopt_max_utilization_mean=("random_failure_reopt_max_utilization", "mean"),
            critical_failure_fixed_disrupted_fraction_mean=("critical_failure_fixed_disrupted_fraction", "mean"),
            random_failure_fixed_disrupted_fraction_mean=("random_failure_fixed_disrupted_fraction", "mean"),
            critical_failure_fixed_fairness_mean=("critical_failure_fixed_fairness", "mean"),
            random_failure_fixed_fairness_mean=("random_failure_fixed_fairness", "mean"),
            robust_worst_case_utilization_mean=("robust_worst_case_utilization", "mean"),
        )
        .reset_index()
    )
    aggregated_path = output_dir / "aggregated_summary.csv"
    aggregated.to_csv(aggregated_path, index=False)

    run_index = pd.DataFrame(detailed_index_rows)
    run_index_path = output_dir / "run_index.csv"
    run_index.to_csv(run_index_path, index=False)

    return {
        "all_run_summaries": all_summaries,
        "aggregated_summary": aggregated,
        "run_index": run_index,
    }
