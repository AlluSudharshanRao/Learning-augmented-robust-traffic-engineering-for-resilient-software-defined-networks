from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd

from teproject.plotting import generate_summary_plots


METHOD_ORDER = [
    "current_demand_lp",
    "robust_current_demand_lp",
    "linear_autoregressive",
    "moving_average",
    "lstm",
]

METHOD_LABELS = {
    "current_demand_lp": "Current-Demand LP",
    "robust_current_demand_lp": "Robust LP",
    "linear_autoregressive": "Linear AR",
    "moving_average": "Moving Average",
    "lstm": "LSTM",
}


def _display_method(method: str) -> str:
    return METHOD_LABELS.get(method, method)


def _rounded(df: pd.DataFrame, digits: int = 4) -> pd.DataFrame:
    result = df.copy()
    numeric_columns = result.select_dtypes(include="number").columns
    result[numeric_columns] = result[numeric_columns].round(digits)
    return result


def _prepare_main_results_table(aggregated: pd.DataFrame) -> pd.DataFrame:
    focus = aggregated[aggregated["load_scale"] == 1.0].copy()
    focus["method"] = pd.Categorical(focus["method"], categories=METHOD_ORDER, ordered=True)
    focus = focus.sort_values(["topology", "method"])
    table = focus[
        [
            "topology",
            "method",
            "prediction_rmse_mean",
            "nominal_max_utilization_mean",
            "critical_failure_reopt_max_utilization_mean",
            "critical_failure_fixed_disrupted_fraction_mean",
            "critical_failure_fixed_fairness_mean",
        ]
    ].copy()
    table["method"] = table["method"].map(_display_method)
    return _rounded(table)


def _prepare_nominal_pivot_table(aggregated: pd.DataFrame) -> pd.DataFrame:
    pivot = aggregated.pivot_table(
        index=["topology", "load_scale"],
        columns="method",
        values="nominal_max_utilization_mean",
        aggfunc="first",
    )
    pivot = pivot.reindex(columns=[m for m in METHOD_ORDER if m in pivot.columns])
    pivot = pivot.rename(columns=METHOD_LABELS).reset_index()
    return _rounded(pivot)


def _prepare_robust_comparison_table(aggregated: pd.DataFrame) -> pd.DataFrame:
    focus = aggregated[
        aggregated["topology"].isin(["abilene", "nsfnet"])
        & aggregated["method"].isin(["current_demand_lp", "robust_current_demand_lp"])
    ].copy()
    pivot = focus.pivot_table(
        index=["topology", "load_scale"],
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
    result["nominal_delta"] = (
        result["nominal_max_utilization_mean__robust_current_demand_lp"]
        - result["nominal_max_utilization_mean__current_demand_lp"]
    )
    result["critical_reopt_delta"] = (
        result["critical_failure_reopt_max_utilization_mean__robust_current_demand_lp"]
        - result["critical_failure_reopt_max_utilization_mean__current_demand_lp"]
    )
    result["critical_fixed_disruption_delta"] = (
        result["critical_failure_fixed_disrupted_fraction_mean__robust_current_demand_lp"]
        - result["critical_failure_fixed_disrupted_fraction_mean__current_demand_lp"]
    )
    result["critical_fixed_fairness_delta"] = (
        result["critical_failure_fixed_fairness_mean__robust_current_demand_lp"]
        - result["critical_failure_fixed_fairness_mean__current_demand_lp"]
    )
    return _rounded(result)


def _prepare_best_method_table(aggregated: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (topology, load_scale), subset in aggregated.groupby(["topology", "load_scale"]):
        best_nominal = subset.loc[subset["nominal_max_utilization_mean"].idxmin()]
        best_fixed_disruption = subset.loc[subset["critical_failure_fixed_disrupted_fraction_mean"].idxmin()]
        best_fairness = subset.loc[subset["critical_failure_fixed_fairness_mean"].idxmax()]
        rows.append(
            {
                "topology": topology,
                "load_scale": load_scale,
                "best_nominal_method": _display_method(str(best_nominal["method"])),
                "best_nominal_utilization": best_nominal["nominal_max_utilization_mean"],
                "best_resilience_method": _display_method(str(best_fixed_disruption["method"])),
                "best_fixed_disruption": best_fixed_disruption["critical_failure_fixed_disrupted_fraction_mean"],
                "best_fairness_method": _display_method(str(best_fairness["method"])),
                "best_fixed_fairness": best_fairness["critical_failure_fixed_fairness_mean"],
            }
        )
    return _rounded(pd.DataFrame(rows))


def _copy_presentation_figures(sweep_dir: Path, asset_figures_dir: Path) -> list[str]:
    copied: list[str] = []
    representative_images = [
        (sweep_dir / "nsfnet_load1p0_seed7" / "worst_failure_case.png", "nsfnet_worst_failure_case.png"),
        (sweep_dir / "abilene_load1p0_seed7" / "worst_failure_case.png", "abilene_worst_failure_case.png"),
    ]
    for source, target_name in representative_images:
        if source.exists():
            shutil.copy2(source, asset_figures_dir / target_name)
            copied.append(target_name)
    return copied


def prepare_report_assets(sweep_dir: Path) -> dict[str, Path]:
    aggregated_path = sweep_dir / "aggregated_summary.csv"
    aggregated = pd.read_csv(aggregated_path)

    asset_dir = sweep_dir / "report_assets"
    tables_dir = asset_dir / "tables"
    figures_dir = asset_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    figure_outputs = generate_summary_plots(aggregated_path, figures_dir)

    main_table = _prepare_main_results_table(aggregated)
    main_table_path = tables_dir / "main_results_load1p0.csv"
    main_table.to_csv(main_table_path, index=False)

    nominal_table = _prepare_nominal_pivot_table(aggregated)
    nominal_table_path = tables_dir / "nominal_utilization_pivot.csv"
    nominal_table.to_csv(nominal_table_path, index=False)

    robust_table = _prepare_robust_comparison_table(aggregated)
    robust_table_path = tables_dir / "robust_lp_direct_comparison.csv"
    robust_table.to_csv(robust_table_path, index=False)

    best_table = _prepare_best_method_table(aggregated)
    best_table_path = tables_dir / "best_method_by_topology_and_load.csv"
    best_table.to_csv(best_table_path, index=False)

    copied_images = _copy_presentation_figures(sweep_dir, figures_dir)

    manifest_path = asset_dir / "PRESENTATION_FIGURES.md"
    manifest_lines = [
        "# Presentation Figures",
        "",
        "Use this folder for the final slide deck and report figures.",
        "",
        "## Core summary figures",
        "",
        "- `summary_nominal_utilization.png`",
        "- `summary_critical_fixed_disruption.png`",
        "- `summary_critical_fixed_fairness.png`",
        "- `abilene_robust_vs_standard_lp.png`",
        "- `nsfnet_robust_vs_standard_lp.png`",
        "",
        "## Example failure visuals",
        "",
    ]
    for image_name in copied_images:
        manifest_lines.append(f"- `{image_name}`")
    manifest_lines += [
        "",
        "## Tables",
        "",
        "- `tables/main_results_load1p0.csv`",
        "- `tables/nominal_utilization_pivot.csv`",
        "- `tables/robust_lp_direct_comparison.csv`",
        "- `tables/best_method_by_topology_and_load.csv`",
    ]
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    outputs = {
        "asset_dir": asset_dir,
        "main_results_table": main_table_path,
        "nominal_pivot_table": nominal_table_path,
        "robust_comparison_table": robust_table_path,
        "best_method_table": best_table_path,
        "presentation_manifest": manifest_path,
    }
    outputs.update(figure_outputs)
    return outputs
