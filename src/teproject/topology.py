from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import topohub


@dataclass
class NetworkTopology:
    graph: nx.DiGraph
    name: str
    source: str


def _assign_capacity(distance_km: float) -> float:
    """Heuristic capacity tiers for benchmark links without native capacities."""
    if distance_km <= 500:
        return 90.0
    if distance_km <= 1000:
        return 75.0
    if distance_km <= 2000:
        return 60.0
    return 45.0


def _make_directed(graph: nx.Graph) -> nx.DiGraph:
    directed = nx.DiGraph()
    for node, attrs in graph.nodes(data=True):
        directed.add_node(node, **attrs)
    for u, v, attrs in graph.edges(data=True):
        distance = float(attrs.get("dist", 1000.0))
        capacity = float(attrs.get("capacity", _assign_capacity(distance)))
        weight = max(distance / 500.0, 1.0)
        edge_attrs = {
            "distance_km": distance,
            "capacity": capacity,
            "weight": weight,
        }
        directed.add_edge(u, v, **edge_attrs)
        directed.add_edge(v, u, **edge_attrs)
    return directed


def build_sample_backbone() -> NetworkTopology:
    graph = nx.DiGraph()
    edges = [
        (0, 1, 40, 1.0),
        (1, 0, 40, 1.0),
        (0, 2, 35, 1.2),
        (2, 0, 35, 1.2),
        (1, 2, 30, 1.0),
        (2, 1, 30, 1.0),
        (1, 3, 25, 1.1),
        (3, 1, 25, 1.1),
        (2, 3, 45, 0.9),
        (3, 2, 45, 0.9),
        (2, 4, 25, 1.4),
        (4, 2, 25, 1.4),
        (3, 4, 30, 1.0),
        (4, 3, 30, 1.0),
        (3, 5, 35, 1.3),
        (5, 3, 35, 1.3),
        (4, 5, 20, 1.1),
        (5, 4, 20, 1.1),
    ]

    for u, v, capacity, weight in edges:
        graph.add_edge(u, v, capacity=float(capacity), weight=float(weight), distance_km=weight * 100.0)

    return NetworkTopology(graph=graph, name="sample_backbone", source="synthetic")


def load_topohub_topology(key: str) -> NetworkTopology:
    topo = topohub.get(key, use_names=True)
    undirected = nx.node_link_graph(topo, edges="edges")
    directed = _make_directed(undirected)
    return NetworkTopology(graph=directed, name=undirected.graph.get("name", key), source=key)


def load_topology(topology_name: str) -> NetworkTopology:
    normalized = topology_name.strip().lower()
    if normalized in {"sample", "sample_backbone", "synthetic"}:
        return build_sample_backbone()
    if normalized == "abilene":
        return load_topohub_topology("topozoo/Abilene")
    if normalized in {"nsfnet", "nsf"}:
        return load_topohub_topology("topozoo/Nsfnet")
    if normalized in {"geant2012", "geant"}:
        return load_topohub_topology("topozoo/Geant2012")
    raise ValueError(f"Unsupported topology: {topology_name}")
