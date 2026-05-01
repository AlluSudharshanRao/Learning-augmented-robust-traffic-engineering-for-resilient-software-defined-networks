from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np
import pulp


@dataclass
class RoutingResult:
    objective_value: float
    edge_loads: dict[tuple[int, int], float]
    commodity_flows: dict[tuple[int, int, int, int], float]
    status: str
    metadata: dict[str, object] | None = None


def solve_min_max_utilization(
    graph: nx.DiGraph,
    demand_matrix: np.ndarray,
) -> RoutingResult:
    nodes = list(graph.nodes())
    edges = list(graph.edges())
    commodities = [
        (src, dst, float(demand_matrix[src_idx, dst_idx]))
        for src_idx, src in enumerate(nodes)
        for dst_idx, dst in enumerate(nodes)
        if src != dst and demand_matrix[src_idx, dst_idx] > 1e-9
    ]

    problem = pulp.LpProblem("MinMaxUtilization", pulp.LpMinimize)
    utilization = pulp.LpVariable("U", lowBound=0.0)
    flow_vars: dict[tuple[int, int, int, int], pulp.LpVariable] = {}

    for src, dst, _ in commodities:
        for u, v in edges:
            key = (src, dst, u, v)
            flow_vars[key] = pulp.LpVariable(f"f_{src}_{dst}_{u}_{v}", lowBound=0.0)

    problem += utilization

    for u, v in edges:
        capacity = float(graph[u][v]["capacity"])
        load_expr = pulp.lpSum(flow_vars[(src, dst, u, v)] for src, dst, _ in commodities)
        problem += load_expr <= utilization * capacity, f"util_cap_{u}_{v}"

    for src, dst, demand in commodities:
        for node in nodes:
            inflow = pulp.lpSum(flow_vars[(src, dst, u, node)] for u in graph.predecessors(node))
            outflow = pulp.lpSum(flow_vars[(src, dst, node, v)] for v in graph.successors(node))
            rhs = 0.0
            if node == src:
                rhs = demand
            elif node == dst:
                rhs = -demand
            problem += outflow - inflow == rhs, f"flow_{src}_{dst}_{node}"

    solver = pulp.PULP_CBC_CMD(msg=False)
    problem.solve(solver)

    status = pulp.LpStatus[problem.status]
    edge_loads: dict[tuple[int, int], float] = {}
    commodity_flows: dict[tuple[int, int, int, int], float] = {}

    for u, v in edges:
        total = 0.0
        for src, dst, _ in commodities:
            key = (src, dst, u, v)
            value = float(flow_vars[key].value() or 0.0)
            if value > 1e-9:
                commodity_flows[key] = value
            total += value
        edge_loads[(u, v)] = total

    return RoutingResult(
        objective_value=float(utilization.value() or 0.0),
        edge_loads=edge_loads,
        commodity_flows=commodity_flows,
        status=status,
        metadata=None,
    )


def solve_failure_aware_min_max_utilization(
    graph: nx.DiGraph,
    demand_matrix: np.ndarray,
    failure_scenarios: list[tuple[tuple[object, object], ...]],
    *,
    nominal_weight: float = 0.5,
    worst_case_weight: float = 0.5,
) -> RoutingResult:
    nodes = list(graph.nodes())
    edges = list(graph.edges())
    commodities = [
        (src, dst, float(demand_matrix[src_idx, dst_idx]))
        for src_idx, src in enumerate(nodes)
        for dst_idx, dst in enumerate(nodes)
        if src != dst and demand_matrix[src_idx, dst_idx] > 1e-9
    ]

    scenarios: list[tuple[str, set[tuple[object, object]]]] = [("nominal", set())]
    for idx, failed_links in enumerate(failure_scenarios):
        scenarios.append((f"failure_{idx}", set(failed_links)))

    problem = pulp.LpProblem("FailureAwareMinMaxUtilization", pulp.LpMinimize)
    worst_utilization = pulp.LpVariable("U_worst", lowBound=0.0)
    nominal_utilization = pulp.LpVariable("U_nominal", lowBound=0.0)

    flow_vars: dict[tuple[str, object, object, object, object], pulp.LpVariable] = {}

    for scenario_name, failed_edges in scenarios:
        available_edges = [edge for edge in edges if edge not in failed_edges]
        for src, dst, _ in commodities:
            for u, v in available_edges:
                key = (scenario_name, src, dst, u, v)
                flow_vars[key] = pulp.LpVariable(
                    f"f_{scenario_name}_{str(src).replace(' ', '_')}_{str(dst).replace(' ', '_')}_{str(u).replace(' ', '_')}_{str(v).replace(' ', '_')}",
                    lowBound=0.0,
                )

    problem += nominal_weight * nominal_utilization + worst_case_weight * worst_utilization

    for scenario_name, failed_edges in scenarios:
        available_edges = [edge for edge in edges if edge not in failed_edges]
        scenario_util = nominal_utilization if scenario_name == "nominal" else worst_utilization

        for u, v in available_edges:
            capacity = float(graph[u][v]["capacity"])
            load_expr = pulp.lpSum(flow_vars[(scenario_name, src, dst, u, v)] for src, dst, _ in commodities)
            problem += load_expr <= scenario_util * capacity, f"cap_{scenario_name}_{u}_{v}"

        for src, dst, demand in commodities:
            for node in nodes:
                inflow_terms = []
                for u in graph.predecessors(node):
                    if (u, node) in failed_edges:
                        continue
                    key = (scenario_name, src, dst, u, node)
                    if key in flow_vars:
                        inflow_terms.append(flow_vars[key])
                outflow_terms = []
                for v in graph.successors(node):
                    if (node, v) in failed_edges:
                        continue
                    key = (scenario_name, src, dst, node, v)
                    if key in flow_vars:
                        outflow_terms.append(flow_vars[key])
                inflow = pulp.lpSum(inflow_terms)
                outflow = pulp.lpSum(outflow_terms)

                rhs = 0.0
                if node == src:
                    rhs = demand
                elif node == dst:
                    rhs = -demand
                problem += outflow - inflow == rhs, f"flow_{scenario_name}_{src}_{dst}_{node}"

    solver = pulp.PULP_CBC_CMD(msg=False)
    problem.solve(solver)
    status = pulp.LpStatus[problem.status]

    nominal_edge_loads: dict[tuple[object, object], float] = {}
    nominal_flows: dict[tuple[object, object, object, object], float] = {}
    for u, v in edges:
        total = 0.0
        for src, dst, _ in commodities:
            key = ("nominal", src, dst, u, v)
            if key not in flow_vars:
                continue
            value = float(flow_vars[key].value() or 0.0)
            if value > 1e-9:
                nominal_flows[(src, dst, u, v)] = value
            total += value
        nominal_edge_loads[(u, v)] = total

    scenario_utilizations: dict[str, float] = {}
    for scenario_name, failed_edges in scenarios:
        available_edges = [edge for edge in edges if edge not in failed_edges]
        max_util = 0.0
        for u, v in available_edges:
            capacity = float(graph[u][v]["capacity"])
            load = 0.0
            for src, dst, _ in commodities:
                key = (scenario_name, src, dst, u, v)
                if key in flow_vars:
                    load += float(flow_vars[key].value() or 0.0)
            if capacity > 0:
                max_util = max(max_util, load / capacity)
        scenario_utilizations[scenario_name] = max_util

    return RoutingResult(
        objective_value=float(nominal_utilization.value() or worst_utilization.value() or 0.0),
        edge_loads=nominal_edge_loads,
        commodity_flows=nominal_flows,
        status=status,
        metadata={
            "nominal_utilization": float(nominal_utilization.value() or 0.0),
            "worst_case_utilization": float(worst_utilization.value() or 0.0),
            "nominal_weight": nominal_weight,
            "worst_case_weight": worst_case_weight,
            "scenario_utilizations": scenario_utilizations,
            "failure_scenarios": [
                " & ".join(f"{u}->{v}" for u, v in scenario)
                for scenario in failure_scenarios
            ],
        },
    )
