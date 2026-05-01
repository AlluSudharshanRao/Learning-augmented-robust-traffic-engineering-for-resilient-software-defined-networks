from __future__ import annotations

import networkx as nx
import numpy as np

from teproject.optimizer import RoutingResult


def mean_absolute_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def root_mean_squared_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def maximum_link_utilization(graph: nx.DiGraph, routing: RoutingResult) -> float:
    utilizations = []
    for (u, v), load in routing.edge_loads.items():
        capacity = float(graph[u][v]["capacity"])
        utilizations.append(load / capacity if capacity > 0 else 0.0)
    return float(max(utilizations, default=0.0))


def average_link_utilization(graph: nx.DiGraph, routing: RoutingResult) -> float:
    utilizations = []
    for (u, v), load in routing.edge_loads.items():
        capacity = float(graph[u][v]["capacity"])
        utilizations.append(load / capacity if capacity > 0 else 0.0)
    return float(np.mean(utilizations)) if utilizations else 0.0


def jains_fairness_index(values: list[float] | np.ndarray) -> float:
    array = np.array(values, dtype=float)
    if array.size == 0:
        return 1.0
    if np.allclose(array, 0.0):
        return 1.0
    numerator = float(np.sum(array) ** 2)
    denominator = float(array.size * np.sum(array ** 2))
    return numerator / denominator if denominator > 0 else 1.0


def fairness_of_served_ratios(
    demand_matrix: np.ndarray,
    per_commodity_disruption: dict[tuple[object, object], float],
    node_order: list[object],
) -> float:
    node_to_index = {node: idx for idx, node in enumerate(node_order)}
    served_ratios: list[float] = []
    for src in node_order:
        for dst in node_order:
            if src == dst:
                continue
            demand = float(demand_matrix[node_to_index[src], node_to_index[dst]])
            if demand <= 1e-9:
                continue
            disrupted = float(per_commodity_disruption.get((src, dst), 0.0))
            served = max(demand - disrupted, 0.0)
            served_ratios.append(served / demand)
    return jains_fairness_index(served_ratios)
