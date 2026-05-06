from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
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

METHOD_COLORS = {
    "current_demand_lp": "#1f77b4",
    "robust_current_demand_lp": "#d62728",
    "uncertainty_aware_lstm_robust_lp": "#8c564b",
    "linear_autoregressive": "#2ca02c",
    "moving_average": "#ff7f0e",
    "lstm": "#6f42c1",
    "transformer": "#17becf",
}


def _method_label(method: str) -> str:
    return METHOD_LABELS.get(method, method.replace("_", " ").title())


def _method_color(method: str) -> str:
    return METHOD_COLORS.get(method, "#444444")


def _load_label(load_scale: float) -> str:
    return f"{load_scale:.1f}x"


def _plot_metric_by_topology(
    df: pd.DataFrame,
    *,
    metric: str,
    ylabel: str,
    title: str,
    output_path: Path,
    methods: list[str] | None = None,
) -> None:
    topologies = sorted(df["topology"].unique())
    methods = methods or list(dict.fromkeys(df["method"].tolist()))
    fig, axes = plt.subplots(1, len(topologies), figsize=(5 * len(topologies), 4.5), sharey=True)
    if len(topologies) == 1:
        axes = [axes]

    for axis, topology in zip(axes, topologies):
        subset = df[df["topology"] == topology].copy()
        subset = subset.sort_values(["load_scale", "method"])
        load_scales = sorted(subset["load_scale"].unique())
        x_values = list(range(len(load_scales)))

        for method in methods:
            method_subset = subset[subset["method"] == method].sort_values("load_scale")
            if method_subset.empty:
                continue
            axis.plot(
                x_values,
                method_subset[metric].tolist(),
                marker="o",
                linewidth=2.2,
                markersize=6,
                color=_method_color(method),
                label=_method_label(method),
            )

        axis.set_title(topology.upper())
        axis.set_xticks(x_values, [_load_label(scale) for scale in load_scales])
        axis.set_xlabel("Traffic Load Scale")
        axis.grid(True, linestyle="--", alpha=0.3)

    axes[0].set_ylabel(ylabel)
    fig.suptitle(title, fontsize=14, y=1.02)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(5, len(labels)), frameon=False)
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _plot_robust_lp_comparison(
    df: pd.DataFrame,
    *,
    topology: str,
    output_path: Path,
) -> None:
    methods = [
        "current_demand_lp",
        "robust_current_demand_lp",
        "uncertainty_aware_lstm_robust_lp",
    ]
    metrics = [
        ("nominal_max_utilization_mean", "Nominal Max Utilization"),
        ("critical_failure_reopt_max_utilization_mean", "Critical Failure Reopt Utilization"),
        ("critical_failure_fixed_disrupted_fraction_mean", "Critical Failure Fixed Disruption"),
        ("critical_failure_fixed_fairness_mean", "Critical Failure Fixed Fairness"),
    ]
    subset = df[(df["topology"] == topology) & (df["method"].isin(methods))].copy()
    subset = subset.sort_values(["load_scale", "method"])
    load_scales = sorted(subset["load_scale"].unique())
    x_values = list(range(len(load_scales)))

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.5))
    axes_flat = axes.flatten()

    for axis, (metric, ylabel) in zip(axes_flat, metrics):
        for method in methods:
            method_subset = subset[subset["method"] == method].sort_values("load_scale")
            axis.plot(
                x_values,
                method_subset[metric].tolist(),
                marker="o",
                linewidth=2.4,
                markersize=6,
                color=_method_color(method),
                label=_method_label(method),
            )
        axis.set_title(ylabel)
        axis.set_xticks(x_values, [_load_label(scale) for scale in load_scales])
        axis.set_xlabel("Traffic Load Scale")
        axis.grid(True, linestyle="--", alpha=0.3)

    axes_flat[0].legend(frameon=False)
    fig.suptitle(f"{topology.upper()}: Robust LP vs Current-Demand LP", fontsize=14, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _build_robust_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    target = df[
        df["topology"].isin(["abilene", "nsfnet"])
        & df["method"].isin(
            [
                "current_demand_lp",
                "robust_current_demand_lp",
                "uncertainty_aware_lstm_robust_lp",
            ]
        )
    ].copy()
    pivot = target.pivot_table(
        index=["topology", "load_scale"],
        columns="method",
        values=[
            "nominal_max_utilization_mean",
            "critical_failure_reopt_max_utilization_mean",
            "critical_failure_fixed_disrupted_fraction_mean",
            "critical_failure_fixed_fairness_mean",
            "robust_worst_case_utilization_mean",
        ],
        aggfunc="first",
    )
    pivot = pivot.sort_index()
    pivot.columns = [f"{metric}__{method}" for metric, method in pivot.columns]
    comparison = pivot.reset_index()

    for compare_method, prefix in (
        ("robust_current_demand_lp", "robust"),
        ("uncertainty_aware_lstm_robust_lp", "uncertainty"),
    ):
        if f"nominal_max_utilization_mean__{compare_method}" not in comparison.columns:
            continue
        comparison[f"{prefix}_nominal_utilization_delta"] = (
            comparison[f"nominal_max_utilization_mean__{compare_method}"]
            - comparison["nominal_max_utilization_mean__current_demand_lp"]
        )
        comparison[f"{prefix}_critical_reopt_delta"] = (
            comparison[f"critical_failure_reopt_max_utilization_mean__{compare_method}"]
            - comparison["critical_failure_reopt_max_utilization_mean__current_demand_lp"]
        )
        comparison[f"{prefix}_critical_fixed_disruption_delta"] = (
            comparison[f"critical_failure_fixed_disrupted_fraction_mean__{compare_method}"]
            - comparison["critical_failure_fixed_disrupted_fraction_mean__current_demand_lp"]
        )
        comparison[f"{prefix}_critical_fixed_fairness_delta"] = (
            comparison[f"critical_failure_fixed_fairness_mean__{compare_method}"]
            - comparison["critical_failure_fixed_fairness_mean__current_demand_lp"]
        )
    return comparison


def generate_summary_plots(aggregated_summary_path: Path, output_dir: Path) -> dict[str, Path]:
    df = pd.read_csv(aggregated_summary_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    created: dict[str, Path] = {}
    all_methods = [
        "current_demand_lp",
        "robust_current_demand_lp",
        "uncertainty_aware_lstm_robust_lp",
        "linear_autoregressive",
        "moving_average",
        "lstm",
        "transformer",
    ]

    nominal_plot = output_dir / "summary_nominal_utilization.png"
    _plot_metric_by_topology(
        df,
        metric="nominal_max_utilization_mean",
        ylabel="Mean Maximum Link Utilization",
        title="Nominal Congestion Across Topologies and Load Levels",
        output_path=nominal_plot,
        methods=all_methods,
    )
    created["summary_nominal_utilization"] = nominal_plot

    disruption_plot = output_dir / "summary_critical_fixed_disruption.png"
    _plot_metric_by_topology(
        df,
        metric="critical_failure_fixed_disrupted_fraction_mean",
        ylabel="Mean Disrupted Demand Fraction",
        title="Fixed-Routing Disruption Under Critical Link Failures",
        output_path=disruption_plot,
        methods=all_methods,
    )
    created["summary_critical_fixed_disruption"] = disruption_plot

    fairness_plot = output_dir / "summary_critical_fixed_fairness.png"
    _plot_metric_by_topology(
        df,
        metric="critical_failure_fixed_fairness_mean",
        ylabel="Mean Jain Fairness Index",
        title="Failure-Side Fairness Under Critical Link Failures",
        output_path=fairness_plot,
        methods=all_methods,
    )
    created["summary_critical_fixed_fairness"] = fairness_plot

    for topology in ["abilene", "nsfnet"]:
        robust_plot = output_dir / f"{topology}_lp_family_comparison.png"
        _plot_robust_lp_comparison(df, topology=topology, output_path=robust_plot)
        created[f"{topology}_lp_family_comparison"] = robust_plot

    comparison = _build_robust_comparison_table(df)
    comparison_path = output_dir / "robust_lp_comparison.csv"
    comparison.to_csv(comparison_path, index=False)
    created["robust_lp_comparison_csv"] = comparison_path

    ml_methods = ["linear_autoregressive", "moving_average", "lstm", "transformer"]
    ml_nominal_plot = output_dir / "ml_nominal_comparison.png"
    _plot_metric_by_topology(
        df,
        metric="nominal_max_utilization_mean",
        ylabel="Mean Maximum Link Utilization",
        title="ML Predictor Comparison: Nominal Routing Quality",
        output_path=ml_nominal_plot,
        methods=ml_methods,
    )
    created["ml_nominal_comparison"] = ml_nominal_plot

    ml_rmse_plot = output_dir / "ml_prediction_rmse_comparison.png"
    _plot_metric_by_topology(
        df,
        metric="prediction_rmse_mean",
        ylabel="Mean Prediction RMSE",
        title="ML Predictor Comparison: Forecasting Error",
        output_path=ml_rmse_plot,
        methods=ml_methods,
    )
    created["ml_prediction_rmse_comparison"] = ml_rmse_plot

    return created
