from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from teproject.optimizer import RoutingResult


@dataclass
class CommodityPath:
    path_rank: int
    nodes: list[object]
    edges: list[tuple[object, object]]
    flow: float


def _build_commodity_subgraph(
    routing: RoutingResult,
    source: object,
    destination: object,
    tolerance: float = 1e-7,
) -> nx.DiGraph:
    graph = nx.DiGraph()
    for (src, dst, u, v), flow in routing.commodity_flows.items():
        if src == source and dst == destination and flow > tolerance:
            graph.add_edge(u, v, residual=float(flow))
    return graph


def decompose_commodity_flow_paths(
    routing: RoutingResult,
    source: object,
    destination: object,
    max_paths: int = 5,
    tolerance: float = 1e-7,
) -> list[CommodityPath]:
    residual_graph = _build_commodity_subgraph(routing, source, destination, tolerance=tolerance)
    paths: list[CommodityPath] = []

    for rank in range(1, max_paths + 1):
        if source not in residual_graph or destination not in residual_graph:
            break
        try:
            node_path = nx.shortest_path(residual_graph, source=source, target=destination)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            break

        edge_path = list(zip(node_path[:-1], node_path[1:]))
        bottleneck = min(float(residual_graph[u][v]["residual"]) for u, v in edge_path)
        paths.append(
            CommodityPath(
                path_rank=rank,
                nodes=node_path,
                edges=edge_path,
                flow=bottleneck,
            )
        )

        for u, v in edge_path:
            residual_graph[u][v]["residual"] -= bottleneck
            if residual_graph[u][v]["residual"] <= tolerance:
                residual_graph.remove_edge(u, v)

    return paths
