from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


METHOD_LABELS = {
    "current_demand_lp": "Current-Demand LP",
    "robust_current_demand_lp": "Robust LP",
    "uncertainty_aware_lstm_robust_lp": "Uncertainty-Aware Robust LP",
    "linear_autoregressive": "Linear AR",
    "moving_average": "Moving Average",
    "lstm": "LSTM",
    "transformer": "Transformer",
}


def _rounded(df: pd.DataFrame, digits: int = 4) -> pd.DataFrame:
    result = df.copy()
    numeric_columns = result.select_dtypes(include="number").columns
    result[numeric_columns] = result[numeric_columns].round(digits)
    return result


def _display_method(method: str) -> str:
    return METHOD_LABELS.get(method, method)


def prepare_ablation_assets(sweep_dir: Path) -> dict[str, Path]:
    aggregated = pd.read_csv(sweep_dir / "aggregated_summary.csv")
    asset_dir = sweep_dir / "report_assets"
    tables_dir = asset_dir / "tables"
    figures_dir = asset_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    best_method = _prepare_best_method_by_topology_load(aggregated)
    best_method_path = tables_dir / "best_method_by_topology_load.csv"
    best_method.to_csv(best_method_path, index=False)

    ml_tradeoff = _prepare_ml_vs_routing_tradeoff(aggregated)
    ml_tradeoff_path = tables_dir / "ml_vs_routing_tradeoff.csv"
    ml_tradeoff.to_csv(ml_tradeoff_path, index=False)

    robustness_tradeoff = _prepare_robustness_tradeoff_summary(aggregated)
    robustness_tradeoff_path = tables_dir / "robustness_tradeoff_summary.csv"
    robustness_tradeoff.to_csv(robustness_tradeoff_path, index=False)

    uncertainty_sensitivity = _prepare_uncertainty_sensitivity(aggregated)
    uncertainty_sensitivity_path = tables_dir / "uncertainty_multiplier_sensitivity.csv"
    uncertainty_sensitivity.to_csv(uncertainty_sensitivity_path, index=False)

    figure_outputs = {
        "transformer_ablation_nominal": _plot_transformer_nominal(aggregated, figures_dir / "transformer_ablation_nominal.png"),
        "transformer_ablation_tradeoff": _plot_transformer_tradeoff(aggregated, figures_dir / "transformer_ablation_tradeoff.png"),
        "uncertainty_sensitivity": _plot_uncertainty_sensitivity(aggregated, figures_dir / "uncertainty_multiplier_sensitivity.png"),
        "robustness_tradeoff": _plot_robustness_tradeoff(aggregated, figures_dir / "robustness_tradeoff.png"),
    }

    manifest = asset_dir / "ABLATION_FIGURES.md"
    manifest.write_text(
        "\n".join(
            [
                "# Ablation Figures",
                "",
                "- `figures/transformer_ablation_nominal.png`",
                "- `figures/transformer_ablation_tradeoff.png`",
                "- `figures/uncertainty_multiplier_sensitivity.png`",
                "- `figures/robustness_tradeoff.png`",
                "",
                "## Tables",
                "",
                "- `tables/best_method_by_topology_load.csv`",
                "- `tables/ml_vs_routing_tradeoff.csv`",
                "- `tables/robustness_tradeoff_summary.csv`",
                "- `tables/uncertainty_multiplier_sensitivity.csv`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    outputs = {
        "asset_dir": asset_dir,
        "best_method_table": best_method_path,
        "ml_tradeoff_table": ml_tradeoff_path,
        "robustness_tradeoff_table": robustness_tradeoff_path,
        "uncertainty_sensitivity_table": uncertainty_sensitivity_path,
        "manifest": manifest,
    }
    outputs.update(figure_outputs)
    return outputs


def _prepare_best_method_by_topology_load(aggregated: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (topology, load_scale), subset in aggregated.groupby(["topology", "load_scale"]):
        best_nominal = subset.loc[subset["nominal_max_utilization_mean"].idxmin()]
        best_resilience = subset.loc[subset["critical_failure_fixed_disrupted_fraction_mean"].idxmin()]
        rows.append(
            {
                "topology": topology,
                "load_scale": load_scale,
                "best_nominal_family": best_nominal["ablation_family"],
                "best_nominal_variant": best_nominal["ablation_variant"],
                "best_nominal_method": _display_method(str(best_nominal["method"])),
                "best_nominal_utilization": best_nominal["nominal_max_utilization_mean"],
                "best_resilience_family": best_resilience["ablation_family"],
                "best_resilience_variant": best_resilience["ablation_variant"],
                "best_resilience_method": _display_method(str(best_resilience["method"])),
                "best_fixed_disruption": best_resilience["critical_failure_fixed_disrupted_fraction_mean"],
            }
        )
    return _rounded(pd.DataFrame(rows))


def _prepare_ml_vs_routing_tradeoff(aggregated: pd.DataFrame) -> pd.DataFrame:
    ml = aggregated[
        (aggregated["ablation_family"] == "transformer")
        & aggregated["method"].isin(["lstm", "transformer"])
    ].copy()
    if ml.empty:
        return pd.DataFrame()
    pivot = ml.pivot_table(
        index=["topology", "ablation_variant"],
        columns="method",
        values=[
            "prediction_rmse_mean",
            "nominal_max_utilization_mean",
            "critical_failure_reopt_max_utilization_mean",
        ],
        aggfunc="first",
    )
    pivot.columns = [f"{metric}__{method}" for metric, method in pivot.columns]
    result = pivot.reset_index()
    result["transformer_rmse_delta_vs_lstm"] = (
        result["prediction_rmse_mean__transformer"] - result["prediction_rmse_mean__lstm"]
    )
    result["transformer_nominal_delta_vs_lstm"] = (
        result["nominal_max_utilization_mean__transformer"] - result["nominal_max_utilization_mean__lstm"]
    )
    result["transformer_reopt_delta_vs_lstm"] = (
        result["critical_failure_reopt_max_utilization_mean__transformer"]
        - result["critical_failure_reopt_max_utilization_mean__lstm"]
    )
    return _rounded(result)


def _prepare_robustness_tradeoff_summary(aggregated: pd.DataFrame) -> pd.DataFrame:
    lp = aggregated[
        aggregated["ablation_family"].isin(["uncertainty", "robust"])
        & aggregated["method"].isin(
            [
                "current_demand_lp",
                "robust_current_demand_lp",
                "uncertainty_aware_lstm_robust_lp",
            ]
        )
    ].copy()
    if lp.empty:
        return pd.DataFrame()
    pivot = lp.pivot_table(
        index=["ablation_family", "ablation_variant", "topology"],
        columns="method",
        values=[
            "nominal_max_utilization_mean",
            "critical_failure_reopt_max_utilization_mean",
            "critical_failure_fixed_disrupted_fraction_mean",
            "critical_failure_fixed_fairness_mean",
        ],
        aggfunc="first",
    )
    pivot.columns = [f"{metric}__{method}" for metric, method in pivot.columns]
    result = pivot.reset_index()
    for method, prefix in (
        ("robust_current_demand_lp", "robust_lp"),
        ("uncertainty_aware_lstm_robust_lp", "uncertainty_aware"),
    ):
        nominal_column = f"nominal_max_utilization_mean__{method}"
        reopt_column = f"critical_failure_reopt_max_utilization_mean__{method}"
        disruption_column = f"critical_failure_fixed_disrupted_fraction_mean__{method}"
        fairness_column = f"critical_failure_fixed_fairness_mean__{method}"
        if nominal_column not in result.columns:
            continue
        result[f"{prefix}_nominal_delta_vs_current"] = (
            result[nominal_column]
            - result["nominal_max_utilization_mean__current_demand_lp"]
        )
        result[f"{prefix}_reopt_delta_vs_current"] = (
            result[reopt_column]
            - result["critical_failure_reopt_max_utilization_mean__current_demand_lp"]
        )
        result[f"{prefix}_fixed_disruption_delta_vs_current"] = (
            result[disruption_column]
            - result["critical_failure_fixed_disrupted_fraction_mean__current_demand_lp"]
        )
        result[f"{prefix}_fairness_delta_vs_current"] = (
            result[fairness_column]
            - result["critical_failure_fixed_fairness_mean__current_demand_lp"]
        )
    return _rounded(result)


def _prepare_uncertainty_sensitivity(aggregated: pd.DataFrame) -> pd.DataFrame:
    uncertainty = aggregated[
        (aggregated["ablation_family"] == "uncertainty")
        & (aggregated["method"] == "uncertainty_aware_lstm_robust_lp")
    ].copy()
    if uncertainty.empty:
        return pd.DataFrame()
    columns = [
        "topology",
        "ablation_variant",
        "uncertainty_multiplier_config",
        "nominal_max_utilization_mean",
        "critical_failure_reopt_max_utilization_mean",
        "critical_failure_fixed_disrupted_fraction_mean",
        "critical_failure_fixed_fairness_mean",
    ]
    return _rounded(uncertainty[columns].sort_values(["topology", "uncertainty_multiplier_config"]))


def _plot_transformer_nominal(aggregated: pd.DataFrame, output_path: Path) -> Path:
    data = aggregated[
        (aggregated["ablation_family"] == "transformer")
        & (aggregated["method"].isin(["lstm", "transformer"]))
    ].copy()
    if data.empty:
        return output_path
    fig, axes = plt.subplots(1, len(data["topology"].unique()), figsize=(12, 4), sharey=True)
    axes = np.atleast_1d(axes).ravel().tolist()
    for ax, topology in zip(axes, sorted(data["topology"].unique())):
        subset = data[data["topology"] == topology]
        x = range(len(sorted(subset["ablation_variant"].unique())))
        transformer_vals = subset[subset["method"] == "transformer"].sort_values("ablation_variant")["nominal_max_utilization_mean"].tolist()
        lstm_vals = subset[subset["method"] == "lstm"].sort_values("ablation_variant")["nominal_max_utilization_mean"].tolist()
        labels = subset[subset["method"] == "transformer"].sort_values("ablation_variant")["ablation_variant"].tolist()
        ax.plot(x, transformer_vals, marker="o", label="Transformer", color="#17becf")
        ax.plot(x, lstm_vals, marker="s", label="LSTM", color="#d62728")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=20)
        ax.set_title(topology.upper())
        ax.set_ylabel("Nominal Max Utilization")
        ax.grid(axis="y", alpha=0.25)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def _plot_transformer_tradeoff(aggregated: pd.DataFrame, output_path: Path) -> Path:
    data = aggregated[
        (aggregated["ablation_family"] == "transformer")
        & (aggregated["method"] == "transformer")
    ].copy()
    if data.empty:
        return output_path
    fig, ax = plt.subplots(figsize=(7, 5))
    for topology, subset in data.groupby("topology"):
        ax.scatter(
            subset["prediction_rmse_mean"],
            subset["nominal_max_utilization_mean"],
            label=topology,
            s=70,
        )
        for _, row in subset.iterrows():
            ax.annotate(str(row["ablation_variant"]), (row["prediction_rmse_mean"], row["nominal_max_utilization_mean"]), fontsize=8)
    ax.set_xlabel("Prediction RMSE")
    ax.set_ylabel("Nominal Max Utilization")
    ax.set_title("Transformer Tuning Tradeoff")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def _plot_uncertainty_sensitivity(aggregated: pd.DataFrame, output_path: Path) -> Path:
    data = aggregated[
        (aggregated["ablation_family"] == "uncertainty")
        & (aggregated["method"] == "uncertainty_aware_lstm_robust_lp")
    ].copy()
    if data.empty:
        return output_path
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    for topology, subset in data.groupby("topology"):
        subset = subset.sort_values("uncertainty_multiplier_config")
        axes[0].plot(
            subset["uncertainty_multiplier_config"],
            subset["nominal_max_utilization_mean"],
            marker="o",
            label=topology,
        )
        axes[1].plot(
            subset["uncertainty_multiplier_config"],
            subset["critical_failure_fixed_fairness_mean"],
            marker="o",
            label=topology,
        )
    axes[0].set_title("Nominal Utilization vs Uncertainty Multiplier")
    axes[0].set_ylabel("Nominal Max Utilization")
    axes[1].set_title("Fairness vs Uncertainty Multiplier")
    axes[1].set_ylabel("Critical Fixed Fairness")
    for ax in axes:
        ax.set_xlabel("Uncertainty Multiplier")
        ax.grid(alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def _plot_robustness_tradeoff(aggregated: pd.DataFrame, output_path: Path) -> Path:
    data = aggregated[
        aggregated["ablation_family"].isin(["robust", "uncertainty"])
        & (aggregated["method"] == "uncertainty_aware_lstm_robust_lp")
    ].copy()
    if data.empty:
        return output_path
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for topology, subset in data.groupby("topology"):
        x_labels = [f"{family}:{variant}" for family, variant in zip(subset["ablation_family"], subset["ablation_variant"])]
        x = range(len(x_labels))
        axes[0].plot(x, subset["critical_failure_reopt_max_utilization_mean"], marker="o", label=topology)
        axes[1].plot(x, subset["critical_failure_fixed_disrupted_fraction_mean"], marker="o", label=topology)
        axes[0].set_xticks(list(x))
        axes[0].set_xticklabels(x_labels, rotation=35, ha="right")
        axes[1].set_xticks(list(x))
        axes[1].set_xticklabels(x_labels, rotation=35, ha="right")
    axes[0].set_title("Re-optimization Sensitivity")
    axes[0].set_ylabel("Critical Failure Reopt Utilization")
    axes[1].set_title("Fixed-Failure Disruption Sensitivity")
    axes[1].set_ylabel("Critical Fixed Disrupted Fraction")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path
