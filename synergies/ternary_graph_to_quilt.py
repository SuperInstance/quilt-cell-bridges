"""
ternary-graph (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-graph (Rust) provides graph algorithms operating
on ternary-weighted edges {-1, 0, +1}:
- Adjacency matrices
- Shortest paths with signed weights
- Graph Laplacian L = D - A
- Normalized Laplacian
- Community detection
- Spectral clustering

THE CRUCIAL INSIGHT: The graph IS the cell graph. The ternary weights ARE
the cell values. The Laplacian IS the conservation operator.

Map:
- Vertex → Quilt cell
- Edge weight w ∈ {-1, 0, +1} → Vibe (state)
- Adjacency matrix → Graph
- Graph Laplacian → DoubleEntry (γ+η=C)
- Community → subgraph (Murmur cluster)
- Spectral clustering → JEPA (eigenvector prediction)
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import math


class Cell:
    """A Quilt cell (vertex)."""
    def __init__(self, id: str, gamma: float = 0.5, eta: float = 0.5):
        self.id = id
        self.gamma = gamma
        self.eta = eta

    def __repr__(self):
        return f"Cell({self.id})"


class Edge:
    """An edge with ternary weight {-1, 0, +1}."""
    def __init__(self, source: str, target: str, weight: int):
        self.source = source
        self.target = target
        self.weight = weight  # -1, 0, or 1

    def __repr__(self):
        return f"Edge({self.source} → {self.target}, w={self.weight})"


class TernaryGraphBridge:
    """A ternary-weighted graph as a Quilt cell graph."""

    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        self.edges: List[Edge] = []
        # Adjacency: cell_id -> {neighbor_id: weight}
        self.adjacency: Dict[str, Dict[str, int]] = {}

    def add_cell(self, id: str) -> Cell:
        """Add a cell (vertex)."""
        if id not in self.cells:
            self.cells[id] = Cell(id)
            self.adjacency[id] = {}
        return self.cells[id]

    def add_edge(self, source: str, target: str, weight: int = 1) -> None:
        """Add an edge with ternary weight."""
        if weight not in (-1, 0, 1):
            raise ValueError(f"Weight must be in {{-1, 0, 1}}, got {weight}")
        self.add_cell(source)
        self.add_cell(target)
        edge = Edge(source, target, weight)
        self.edges.append(edge)
        self.adjacency[source][target] = weight
        self.adjacency[target][source] = weight  # undirected

    def degree(self, cell_id: str) -> int:
        """Degree of a cell. Sum of absolute weights."""
        return sum(abs(w) for w in self.adjacency[cell_id].values())

    def laplacian(self) -> List[List[int]]:
        """Compute the graph Laplacian L = D - A."""
        n = len(self.cells)
        ids = list(self.cells.keys())
        id_to_idx = {cid: i for i, cid in enumerate(ids)}
        L = [[0] * n for _ in range(n)]
        for i, cid in enumerate(ids):
            L[i][i] = self.degree(cid)
            for neighbor, weight in self.adjacency[cid].items():
                j = id_to_idx[neighbor]
                L[i][j] = -weight
        return L

    def detect_communities(self) -> List[Set[str]]:
        """Detect communities by sign of weight."""
        # Simple: cluster by positive vs negative edges
        positive: Set[str] = set()
        for edge in self.edges:
            if edge.weight > 0:
                positive.add(edge.source)
                positive.add(edge.target)
        negative: Set[str] = set(self.cells.keys()) - positive
        communities = []
        if positive:
            communities.append(positive)
        if negative:
            communities.append(negative)
        return communities

    def shortest_path(self, source: str, target: str) -> Tuple[int, List[str]]:
        """Shortest path via BFS for positive weights only."""
        if source not in self.cells or target not in self.cells:
            return 0, []
        from collections import deque
        visited = {source}
        queue = deque([(source, 0, [source])])
        while queue:
            current, dist, path = queue.popleft()
            if current == target:
                return dist, path
            for neighbor, weight in self.adjacency[current].items():
                if neighbor not in visited and weight > 0:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + weight, path + [neighbor]))
        return 0, []  # no path found

    def verify_conservation(self) -> bool:
        """γ+η=1 across all cells."""
        for c in self.cells.values():
            if abs(c.gamma + c.eta - 1.0) > 1e-9:
                return False
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-GRAPH ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Ternary-weighted graphs (-1, 0, +1) on Quilt cells.")
    print("The graph IS the cell graph. Laplacian IS conservation.")
    print()

    g = TernaryGraphBridge()

    # Build a small graph
    g.add_cell("a")
    g.add_cell("b")
    g.add_cell("c")
    g.add_cell("d")
    g.add_edge("a", "b", 1)  # positive
    g.add_edge("b", "c", 1)
    g.add_edge("a", "c", -1)  # negative
    g.add_edge("c", "d", 1)

    print(f"Cells: {list(g.cells.keys())}")
    print(f"Edges: {len(g.edges)}")
    print()

    # Laplacian
    L = g.laplacian()
    print("Laplacian L = D - A:")
    for row in L:
        print(f"  {row}")
    print()

    # Communities
    communities = g.detect_communities()
    print(f"Communities: {[list(c) for c in communities]}")
    print()

    # Shortest path
    dist, path = g.shortest_path("a", "d")
    print(f"Shortest path a → d: distance={dist}, path={path}")
    print()

    # Conservation
    print(f"Conservation: γ+η=1 holds: {g.verify_conservation()}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A ternary graph IS a Quilt cell graph.")
    print("Laplacian IS DoubleEntry. Communities IS Murmur.")


