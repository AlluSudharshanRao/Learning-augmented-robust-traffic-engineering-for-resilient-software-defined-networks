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
