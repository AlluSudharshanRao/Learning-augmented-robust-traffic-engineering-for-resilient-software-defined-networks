from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from teproject.config import ExperimentConfig
from teproject.failure import (
    evaluate_fixed_routing_after_failure,
    evaluate_single_link_failure,
    pick_critical_link_bundle,
    pick_random_link_bundle,
    select_robust_failure_scenarios,
)
from teproject.metrics import (
    average_link_utilization,
    fairness_of_served_ratios,
    maximum_link_utilization,
    mean_absolute_error,
    root_mean_squared_error,
)
from teproject.optimizer import solve_failure_aware_min_max_utilization, solve_min_max_utilization
from teproject.paths import decompose_commodity_flow_paths
from teproject.predictors import LSTMPredictor, LinearAutoRegressivePredictor, MovingAveragePredictor
from teproject.topology import load_topology
from teproject.traffic import generate_dynamic_traffic


def run_default_experiment(output_dir: Path, config: ExperimentConfig | None = None) -> dict[str, Any]:
    config = config or ExperimentConfig()
    output_dir.mkdir(parents=True, exist_ok=True)
    topology = load_topology(config.topology)
    traffic = generate_dynamic_traffic(
        num_nodes=topology.graph.number_of_nodes(),
        num_steps=config.num_steps,
        seed=config.seed,
        load_scale=config.load_scale,
    )
    node_order = list(topology.graph.nodes())
    node_to_index = {node: idx for idx, node in enumerate(node_order)}

    predictors = [
        MovingAveragePredictor(),
        LinearAutoRegressivePredictor(),
    ]
    if config.enable_lstm:
        predictors.append(LSTMPredictor(history_window=config.history_window, epochs=100, hidden_size=48))

    train_data = traffic.matrices[: config.train_steps]
    for predictor in predictors:
        predictor.fit(train_data)

    rows = []
    disruption_rows = []
    path_rows = []

    for t in range(config.train_steps, traffic.num_steps - 1):
        history = traffic.matrices[t - config.history_window + 1 : t + 1]
        current_matrix = traffic.matrices[t]
        actual_next = traffic.matrices[t + 1]

        baselines = [("current_demand_lp", current_matrix)]
        for predictor in predictors:
            predicted = predictor.predict_next(history)
            baselines.append((predictor.name, predicted))

        for method_name, optimized_demand in baselines:
            if method_name == "current_demand_lp" and config.enable_robust_baseline:
                routing = solve_min_max_utilization(topology.graph, optimized_demand)
                robust_scenarios = select_robust_failure_scenarios(
                    topology.graph,
                    seed=t,
                    routing=routing,
                    max_scenarios=config.robust_max_scenarios,
                    num_central_scenarios=config.robust_num_central_scenarios,
                    include_random_scenario=config.robust_include_random_scenario,
                )
                robust_routing = solve_failure_aware_min_max_utilization(
                    topology.graph,
                    optimized_demand,
                    failure_scenarios=robust_scenarios,
                    nominal_weight=config.robust_nominal_weight,
                    worst_case_weight=config.robust_worst_case_weight,
                )
                candidate_routings = [
                    (method_name, routing),
                    ("robust_current_demand_lp", robust_routing),
                ]
            else:
                routing = solve_min_max_utilization(topology.graph, optimized_demand)
                candidate_routings = [(method_name, routing)]

            for active_method_name, active_routing in candidate_routings:
                _record_method_result(
                    rows=rows,
                    disruption_rows=disruption_rows,
                    path_rows=path_rows,
                    topology=topology,
                    node_to_index=node_to_index,
                    time_step=t,
                    method_name=active_method_name,
                    routing=active_routing,
                    optimized_demand=optimized_demand,
                    actual_next=actual_next,
                    seed=t,
                    config=config,
                )

    df = pd.DataFrame(rows)
    csv_path = output_dir / "experiment_results.csv"
    df.to_csv(csv_path, index=False)

    disruption_df = pd.DataFrame(disruption_rows)
    disruption_path = output_dir / "failure_disruptions.csv"
    disruption_df.to_csv(disruption_path, index=False)

    path_df = pd.DataFrame(path_rows)
    path_path = output_dir / "failure_paths.csv"
    path_df.to_csv(path_path, index=False)

    summary = (
        df.groupby("method")[
            [
                "prediction_mae",
                "prediction_rmse",
                "nominal_max_utilization",
                "critical_failure_reopt_max_utilization",
                "random_failure_reopt_max_utilization",
                "critical_failure_fixed_served_fraction",
                "random_failure_fixed_served_fraction",
                "critical_failure_fixed_disrupted_fraction",
                "random_failure_fixed_disrupted_fraction",
                "critical_failure_fixed_fairness",
                "random_failure_fixed_fairness",
                "robust_nominal_utilization",
                "robust_worst_case_utilization",
            ]
        ]
        .mean()
        .sort_values("nominal_max_utilization")
    )
    summary_path = output_dir / "summary_results.csv"
    summary.to_csv(summary_path)

    plot_path = output_dir / "nominal_utilization_by_method.png"
    _plot_summary(df, plot_path, topology.name)
    failure_case_plot_path = output_dir / "worst_failure_case.png"
    _plot_worst_failure_case(topology.graph, disruption_df, path_df, failure_case_plot_path)

    print("Saved detailed results to:", csv_path)
    print("Saved disruption details to:", disruption_path)
    print("Saved path details to:", path_path)
    print("Saved summary results to:", summary_path)
    print("Saved plot to:", plot_path)
    print("Saved failure-case plot to:", failure_case_plot_path)
    print("Topology:", topology.name, f"({topology.source})")
    print()
    print(summary.round(4).to_string())
    return {
        "detailed": df,
        "disruptions": disruption_df,
        "paths": path_df,
        "summary": summary.reset_index(),
        "output_dir": output_dir,
    }


def _record_method_result(
    *,
    rows: list[dict[str, object]],
    disruption_rows: list[dict[str, object]],
    path_rows: list[dict[str, object]],
    topology,
    node_to_index: dict[object, int],
    time_step: int,
    method_name: str,
    routing,
    optimized_demand,
    actual_next,
    seed: int,
    config: ExperimentConfig,
) -> None:
    critical_links = pick_critical_link_bundle(topology.graph, routing)
    random_links = pick_random_link_bundle(topology.graph, seed=seed)
    critical_failure = evaluate_single_link_failure(
        topology.graph,
        optimized_demand,
        critical_links,
    )
    random_failure = evaluate_single_link_failure(
        topology.graph,
        optimized_demand,
        random_links,
    )
    fixed_critical = evaluate_fixed_routing_after_failure(routing, optimized_demand, critical_links)
    fixed_random = evaluate_fixed_routing_after_failure(routing, optimized_demand, random_links)
    critical_failure_fairness = fairness_of_served_ratios(
        optimized_demand,
        fixed_critical.per_commodity_disruption,
        list(topology.graph.nodes()),
    )
    random_failure_fairness = fairness_of_served_ratios(
        optimized_demand,
        fixed_random.per_commodity_disruption,
        list(topology.graph.nodes()),
    )

    prediction_mae = mean_absolute_error(actual_next, optimized_demand)
    prediction_rmse = root_mean_squared_error(actual_next, optimized_demand)

    rows.append(
        {
            "time_step": time_step,
            "topology": topology.name,
            "topology_source": topology.source,
            "seed": config.seed,
            "load_scale": config.load_scale,
            "method": method_name,
            "solver_status": routing.status,
            "prediction_mae": prediction_mae,
            "prediction_rmse": prediction_rmse,
            "nominal_max_utilization": maximum_link_utilization(topology.graph, routing),
            "nominal_avg_utilization": average_link_utilization(topology.graph, routing),
            "critical_failure_reopt_max_utilization": maximum_link_utilization(topology.graph, critical_failure),
            "random_failure_reopt_max_utilization": maximum_link_utilization(topology.graph, random_failure),
            "critical_failure_fixed_served_fraction": fixed_critical.served_fraction,
            "critical_failure_fixed_disrupted_fraction": fixed_critical.disrupted_fraction,
            "random_failure_fixed_served_fraction": fixed_random.served_fraction,
            "random_failure_fixed_disrupted_fraction": fixed_random.disrupted_fraction,
            "critical_failure_fixed_fairness": critical_failure_fairness,
            "random_failure_fixed_fairness": random_failure_fairness,
            "robust_nominal_utilization": (
                float(routing.metadata.get("nominal_utilization"))
                if routing.metadata and "nominal_utilization" in routing.metadata
                else None
            ),
            "robust_worst_case_utilization": (
                float(routing.metadata.get("worst_case_utilization"))
                if routing.metadata and "worst_case_utilization" in routing.metadata
                else None
            ),
            "robust_failure_scenarios": (
                " | ".join(routing.metadata.get("failure_scenarios", []))
                if routing.metadata
                else ""
            ),
        }
    )

    for scenario_name, evaluation in (
        ("critical_failure_fixed", fixed_critical),
        ("random_failure_fixed", fixed_random),
    ):
        for rank, ((src, dst), disrupted_amount) in enumerate(evaluation.top_disrupted_commodities, start=1):
            disruption_rows.append(
                {
                    "time_step": time_step,
                    "topology": topology.name,
                    "seed": config.seed,
                    "load_scale": config.load_scale,
                    "method": method_name,
                    "scenario": scenario_name,
                    "failed_link": _format_failure_bundle(evaluation.failed_links),
                    "commodity_rank": rank,
                    "source": src,
                    "destination": dst,
                    "disrupted_amount": disrupted_amount,
                    "demand_value": float(optimized_demand[node_to_index[src], node_to_index[dst]]),
                    "commodity_disruption_ratio": (
                        disrupted_amount
                        / float(optimized_demand[node_to_index[src], node_to_index[dst]])
                        if float(optimized_demand[node_to_index[src], node_to_index[dst]]) > 1e-9
                        else 0.0
                    ),
                }
            )
            commodity_paths = decompose_commodity_flow_paths(routing, src, dst)
            for commodity_path in commodity_paths:
                path_rows.append(
                    {
                        "time_step": time_step,
                        "topology": topology.name,
                        "seed": config.seed,
                        "load_scale": config.load_scale,
                        "method": method_name,
                        "scenario": scenario_name,
                        "failed_link": _format_failure_bundle(evaluation.failed_links),
                        "commodity_rank": rank,
                        "source": src,
                        "destination": dst,
                        "path_rank": commodity_path.path_rank,
                        "path_flow": commodity_path.flow,
                        "path_nodes": " | ".join(str(node) for node in commodity_path.nodes),
                        "path_edges": " | ".join(f"{u}->{v}" for u, v in commodity_path.edges),
                        "contains_failed_link": int(any(edge in commodity_path.edges for edge in evaluation.failed_links)),
                    }
                )


def _plot_summary(df: pd.DataFrame, plot_path: Path, topology_name: str) -> None:
    grouped = df.groupby("method")["nominal_max_utilization"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    palette = ["#4c78a8", "#f58518", "#54a24b", "#e45756"]
    ax.bar(grouped.index, grouped.values, color=palette[: len(grouped.index)])
    ax.set_title(f"Average Nominal Maximum Link Utilization\n{topology_name}")
    ax.set_ylabel("Utilization")
    ax.set_xlabel("Method")
    ax.set_ylim(0, max(1.0, grouped.max() * 1.15))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(plot_path, dpi=160)
    plt.close(fig)


def _plot_worst_failure_case(
    graph: nx.DiGraph,
    disruption_df: pd.DataFrame,
    path_df: pd.DataFrame,
    plot_path: Path,
) -> None:
    if disruption_df.empty or path_df.empty:
        return

    worst_row = disruption_df.sort_values("disrupted_amount", ascending=False).iloc[0]
    selected_paths = path_df[
        (path_df["time_step"] == worst_row["time_step"])
        & (path_df["method"] == worst_row["method"])
        & (path_df["scenario"] == worst_row["scenario"])
        & (path_df["source"] == worst_row["source"])
        & (path_df["destination"] == worst_row["destination"])
    ]

    failed_link_text = str(worst_row["failed_link"])
    failed_edges = []
    for edge_text in failed_link_text.split(" & "):
        if "->" in edge_text:
            failed_u, failed_v = [part.strip() for part in edge_text.split("->", maxsplit=1)]
            failed_edges.append((failed_u, failed_v))

    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes())
    for u, v in graph.edges():
        undirected.add_edge(u, v)
    positions = nx.spring_layout(undirected, seed=11)

    highlighted_edges = set()
    for edge_text in selected_paths["path_edges"].tolist():
        for edge_part in str(edge_text).split(" | "):
            if "->" in edge_part:
                u, v = edge_part.split("->", maxsplit=1)
                highlighted_edges.add((u, v))

    fig, ax = plt.subplots(figsize=(11, 7))
    nx.draw_networkx_nodes(undirected, positions, node_size=650, node_color="#d9e6f2", ax=ax)
    nx.draw_networkx_labels(undirected, positions, font_size=8, ax=ax)
    nx.draw_networkx_edges(undirected, positions, edge_color="#c5c5c5", width=1.1, ax=ax)

    if highlighted_edges:
        nx.draw_networkx_edges(
            undirected,
            positions,
            edgelist=[tuple(edge) for edge in highlighted_edges if undirected.has_edge(*edge)],
            edge_color="#f58518",
            width=2.6,
            ax=ax,
        )

    drawable_failed_edges = []
    for failed_u, failed_v in failed_edges:
        if undirected.has_edge(failed_u, failed_v):
            drawable_failed_edges.append((failed_u, failed_v))
        elif undirected.has_edge(failed_v, failed_u):
            drawable_failed_edges.append((failed_v, failed_u))
    if drawable_failed_edges:
        nx.draw_networkx_edges(
            undirected,
            positions,
            edgelist=drawable_failed_edges,
            edge_color="#d62728",
            width=3.6,
            style="dashed",
            ax=ax,
        )

    ax.set_title(
        "Worst Fixed-Failure Commodity Case\n"
        f"{worst_row['method']} | {worst_row['source']} -> {worst_row['destination']} | "
        f"failed {failed_link_text}"
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=160)
    plt.close(fig)


def _format_failure_bundle(failed_links: tuple[tuple[object, object], ...]) -> str:
    return " & ".join(f"{u} -> {v}" for u, v in failed_links)
