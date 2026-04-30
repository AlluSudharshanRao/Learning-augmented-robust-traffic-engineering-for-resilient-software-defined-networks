from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np

from teproject.optimizer import RoutingResult, solve_min_max_utilization


@dataclass
class FixedRoutingFailureEvaluation:
    failed_links: tuple[tuple[object, object], ...]
    disrupted_flow: float
    total_demand: float
    served_fraction: float
    disrupted_fraction: float
    surviving_edge_loads: dict[tuple[object, object], float]
    per_commodity_disruption: dict[tuple[object, object], float]
    top_disrupted_commodities: list[tuple[tuple[object, object], float]]


def get_failure_bundle(graph: nx.DiGraph, edge: tuple[object, object]) -> tuple[tuple[object, object], ...]:
    u, v = edge
    bundle = [edge]
    if graph.has_edge(v, u) and (v, u) != edge:
        bundle.append((v, u))
    return tuple(bundle)


def _canonical_bundle_key(edge: tuple[object, object]) -> tuple[str, str]:
    u, v = edge
    return tuple(sorted((str(u), str(v))))


def pick_critical_link_bundle(graph: nx.DiGraph, routing: RoutingResult) -> tuple[tuple[object, object], ...]:
    bundle_loads: dict[tuple[str, str], float] = {}
    representative: dict[tuple[str, str], tuple[object, object]] = {}
    for edge, load in routing.edge_loads.items():
        key = _canonical_bundle_key(edge)
        bundle_loads[key] = bundle_loads.get(key, 0.0) + load
        representative.setdefault(key, edge)
    chosen_key = max(bundle_loads.items(), key=lambda item: item[1])[0]
    return get_failure_bundle(graph, representative[chosen_key])


def evaluate_single_link_failure(
    graph: nx.DiGraph,
    demand_matrix: np.ndarray,
    failed_links: tuple[tuple[object, object], ...],
) -> RoutingResult:
    failed_graph = graph.copy()
    for edge in failed_links:
        if failed_graph.has_edge(*edge):
            failed_graph.remove_edge(*edge)
    return solve_min_max_utilization(failed_graph, demand_matrix)


def pick_random_link_bundle(graph: nx.DiGraph, seed: int) -> tuple[tuple[object, object], ...]:
    rng = np.random.default_rng(seed)
    bundles = unique_failure_bundles(graph)
    index = int(rng.integers(low=0, high=len(bundles)))
    return bundles[index]


def unique_failure_bundles(graph: nx.DiGraph) -> list[tuple[tuple[object, object], ...]]:
    seen = set()
    bundles = []
    for edge in graph.edges():
        key = _canonical_bundle_key(edge)
        if key in seen:
            continue
        seen.add(key)
        bundles.append(get_failure_bundle(graph, edge))
    return bundles


def select_robust_failure_scenarios(
    graph: nx.DiGraph,
    seed: int,
    max_scenarios: int = 3,
) -> list[tuple[tuple[object, object], ...]]:
    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes())
    undirected.add_edges_from(graph.edges())
    betweenness = nx.edge_betweenness_centrality(undirected)
    ranked = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)

    scenarios: list[tuple[tuple[object, object], ...]] = []
    for edge, _ in ranked[:2]:
        bundle = get_failure_bundle(graph, edge)
        if bundle not in scenarios:
            scenarios.append(bundle)

    random_bundle = pick_random_link_bundle(graph, seed=seed)
    if random_bundle not in scenarios:
        scenarios.append(random_bundle)

    return scenarios[:max_scenarios]


def evaluate_fixed_routing_after_failure(
    routing: RoutingResult,
    demand_matrix: np.ndarray,
    failed_links: tuple[tuple[object, object], ...],
) -> FixedRoutingFailureEvaluation:
    disrupted_flow = 0.0
    per_commodity_disruption: dict[tuple[object, object], float] = {}
    for (src, dst, u, v), flow in routing.commodity_flows.items():
        if (u, v) in failed_links:
            disrupted_flow += flow
            key = (src, dst)
            per_commodity_disruption[key] = per_commodity_disruption.get(key, 0.0) + flow

    total_demand = float(demand_matrix.sum())
    served_demand = max(total_demand - disrupted_flow, 0.0)
    served_fraction = (served_demand / total_demand) if total_demand > 0 else 1.0
    disrupted_fraction = (disrupted_flow / total_demand) if total_demand > 0 else 0.0
    surviving_edge_loads = {
        edge: load
        for edge, load in routing.edge_loads.items()
        if edge not in failed_links
    }
    top_disrupted_commodities = sorted(
        per_commodity_disruption.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    return FixedRoutingFailureEvaluation(
        failed_links=failed_links,
        disrupted_flow=disrupted_flow,
        total_demand=total_demand,
        served_fraction=served_fraction,
        disrupted_fraction=disrupted_fraction,
        surviving_edge_loads=surviving_edge_loads,
        per_commodity_disruption=per_commodity_disruption,
        top_disrupted_commodities=top_disrupted_commodities,
    )
