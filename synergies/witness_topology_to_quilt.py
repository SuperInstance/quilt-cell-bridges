"""
witness-topology (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance witness-topology (Rust) does TDA via witness complexes.
- Landmark selection (max-min sampling)
- Witness complex construction
- Persistent homology (β₀, β₁, β₂)
- Diagram distances (bottleneck, Wasserstein)
- Mapper graphs
- Stability guarantees

Map:
- Landmark agent → cell
- Witness → Z_in
- Complex → Graph
- Persistent homology → Murmur (inter-scale)
- β₀, β₁, β₂ → Quilt invariants
- Diagram distance → DoubleEntry
- Mapper graph → Graph
- Stability → JEPA
"""

from typing import Dict, List, Any, Set, Tuple
import math


class Cell:
    """A Quilt cell representing a point in space."""
    def __init__(self, point: Tuple[float, ...], id: str):
        self.id = id
        self.point = point
        self.value = 0.0
        self.is_landmark = False
        self.gamma = 0.5
        self.eta = 0.5

    def distance_to(self, other: 'Cell') -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.point, other.point)))


class WitnessTopologyBridge:
    """TDA implemented on Quilt cells."""

    def __init__(self, points: List[Tuple[float, ...]]):
        # Each point is a Quilt cell
        self.cells: List[Cell] = [Cell(p, f"p{i}") for i, p in enumerate(points)]
        # Landmarks
        self.landmarks: List[Cell] = []
        # Witness complex
        self.complex_edges: Set[Tuple[str, str]] = set()
        # Persistence pairs (birth, death) for β₀
        self.persistence: List[Tuple[float, float, int]] = []
        # Betti numbers
        self.betti_0: int = 0
        self.betti_1: int = 0

    def select_landmarks(self, k: int) -> None:
        """Max-min landmark selection."""
        if not self.cells:
            return
        # First landmark: random
        self.cells[0].is_landmark = True
        self.landmarks = [self.cells[0]]
        # Subsequent: max-min
        while len(self.landmarks) < k and len(self.landmarks) < len(self.cells):
            max_min_dist = -1
            max_min_cell = None
            for cell in self.cells:
                if cell.is_landmark:
                    continue
                # Find min distance to any landmark
                min_dist = min(cell.distance_to(lm) for lm in self.landmarks)
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    max_min_cell = cell
            if max_min_cell:
                max_min_cell.is_landmark = True
                self.landmarks.append(max_min_cell)

    def build_witness_complex(self, eps: float) -> None:
        """Build a witness complex. Z_in: every non-landmark witnesses a landmark."""
        for cell in self.cells:
            if cell.is_landmark:
                continue
            # Find landmarks within eps
            for lm in self.landmarks:
                if cell.distance_to(lm) <= eps:
                    self.complex_edges.add((cell.id, lm.id))
            # If a cell witnesses multiple landmarks, add edges between them
            witnesses = [lm for lm in self.landmarks if cell.distance_to(lm) <= eps]
            for i in range(len(witnesses)):
                for j in range(i + 1, len(witnesses)):
                    self.complex_edges.add((witnesses[i].id, witnesses[j].id))

    def persistent_homology(self) -> Dict[str, int]:
        """Compute β₀ and β₁. Murmur inter-scale."""
        # β₀: count connected components
        # Build adjacency from complex edges
        adj: Dict[str, Set[str]] = {cell.id: set() for cell in self.cells}
        for u, v in self.complex_edges:
            adj[u].add(v)
            adj[v].add(u)
        # Union-find
        parent = {cell.id: cell.id for cell in self.cells}
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        for u, v in self.complex_edges:
            union(u, v)
        # Count components
        roots = set(find(cell.id) for cell in self.cells)
        self.betti_0 = len(roots)
        # β₁: count loops (approximate)
        v = len(adj)
        e = len(self.complex_edges)
        # For a graph, β₁ = E - V + β₀
        self.betti_1 = max(0, e - v + self.betti_0)
        return {'beta_0': self.betti_0, 'beta_1': self.betti_1}

    def diagram_distance(self, other: 'WitnessTopologyBridge') -> float:
        """Bottleneck distance between diagrams. DoubleEntry."""
        # Simplified: difference in Betti numbers
        return abs(self.betti_0 - other.betti_0) + abs(self.betti_1 - other.betti_1)

    def mapper_graph(self, lens_values: List[float], num_intervals: int = 3) -> Dict[str, Any]:
        """Build a mapper graph. Graph primitive."""
        if not lens_values:
            return {'nodes': [], 'edges': []}
        min_v, max_v = min(lens_values), max(lens_values)
        if max_v == min_v:
            max_v = min_v + 1
        interval_size = (max_v - min_v) / num_intervals
        # Assign cells to intervals
        intervals: Dict[int, List[Cell]] = {i: [] for i in range(num_intervals)}
        for i, v in enumerate(lens_values):
            idx = min(num_intervals - 1, int((v - min_v) / interval_size))
            intervals[idx].append(self.cells[i])
        # Nodes
        nodes = []
        for interval_id, cells in intervals.items():
            if cells:
                nodes.append({
                    'id': f"interval_{interval_id}",
                    'size': len(cells),
                    'cells': [c.id for c in cells],
                })
        # Edges: between overlapping intervals
        edges = []
        for i in range(num_intervals - 1):
            if intervals[i] and intervals[i + 1]:
                edges.append({'from': f"interval_{i}", 'to': f"interval_{i + 1}"})
        return {'nodes': nodes, 'edges': edges}


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("WITNESS-TOPOLOGY ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Topological data analysis via witness complexes on Quilt cells.")
    print("β₀, β₁ are Quilt invariants. Witness is Z_in. Complex is Graph.")
    print()

    # Create a ring of points
    import math
    ring = [(math.cos(2 * math.pi * i / 12), math.sin(2 * math.pi * i / 12)) for i in range(12)]

    bridge = WitnessTopologyBridge(ring)
    bridge.select_landmarks(k=4)
    print(f"Selected {len(bridge.landmarks)} landmarks from {len(bridge.cells)} points")
    bridge.build_witness_complex(eps=1.5)
    print(f"Built witness complex with {len(bridge.complex_edges)} edges")

    betti = bridge.persistent_homology()
    print(f"Betti numbers: β₀={betti['beta_0']}, β₁={betti['beta_1']}")
    print()

    # Conservation
    n = len(bridge.cells)
    total_g = sum(c.gamma for c in bridge.cells)
    total_e = sum(c.eta for c in bridge.cells)
    print(f"Conservation: {n} cells, γ+η={total_g + total_e:.2f}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("TDA is a Quilt runtime.")
    print("β₁ IS a Quilt invariant.")
    print("Stability is JEPA. Witnesses are Z_in.")


if __name__ == "__main__":
    demo()
