from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TrafficDataset:
    matrices: np.ndarray

    @property
    def num_steps(self) -> int:
        return int(self.matrices.shape[0])

    @property
    def num_nodes(self) -> int:
        return int(self.matrices.shape[1])


def generate_dynamic_traffic(
    num_nodes: int,
    num_steps: int,
    seed: int = 7,
    base_scale: float = 4.0,
    load_scale: float = 1.0,
) -> TrafficDataset:
    rng = np.random.default_rng(seed)
    base = rng.uniform(0.6, 1.4, size=(num_nodes, num_nodes)) * base_scale * load_scale
    np.fill_diagonal(base, 0.0)

    hotspot_pairs = [
        (0, min(3, num_nodes - 1)),
        (min(2, num_nodes - 1), min(5, num_nodes - 1)),
        (min(1, num_nodes - 1), min(4, num_nodes - 1)),
    ]
    hotspot_pairs = [(src, dst) for src, dst in hotspot_pairs if src != dst]
    matrices = []

    for t in range(num_steps):
        daily_cycle = 1.0 + 0.25 * np.sin((2.0 * np.pi * t) / 12.0)
        slow_cycle = 1.0 + 0.15 * np.cos((2.0 * np.pi * t) / 24.0)
        noise = rng.normal(loc=0.0, scale=0.25, size=(num_nodes, num_nodes))
        matrix = base * daily_cycle * slow_cycle + noise
        matrix = np.clip(matrix, 0.0, None)
        np.fill_diagonal(matrix, 0.0)

        if t % 9 == 0:
            for src, dst in hotspot_pairs:
                matrix[src, dst] *= 1.8

        matrices.append(matrix)

    return TrafficDataset(matrices=np.array(matrices, dtype=float))
