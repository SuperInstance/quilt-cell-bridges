"""
base60-lattice (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance base60-lattice (TypeScript) implements a navigational
lattice where bisection and trisection of 360° interlace to create a
coordinate system rooted in ancient sexagesimal mathematics.

- Base 60 is the smallest number divisible by 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30
- The civil clock is already sexagesimal: 24×60×60
- LatticeStamp: timestamp → lattice coordinate
- "The room at this hour, last week" is a real query

THE CRUCIAL INSIGHT: The sexagesimal lattice IS a Quilt cell graph.
A LatticeStamp IS a cell with hour60, day60, phase, season. Time
IS a graph coordinate.

Map:
- Lattice coordinate → cell
- Hour60 → cell.value (0-60)
- Day60 → cell.position in time
- Phase → Vibe.acceleration
- Season → subgraph
- Timestamp → Z_in
- Query → Z_out
"""

from typing import Dict, List, Any, Tuple
import math


class LatticeCell:
    """A Quilt cell representing a lattice coordinate."""
    def __init__(self, hour60: int, day60: int, phase: int = 0, season: int = 0):
        self.hour60 = hour60  # 0-60
        self.day60 = day60    # 0-60
        self.phase = phase    # 0-3
        self.season = season  # 0-3
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"LatticeCell({self.hour60}h, d{self.day60}, p{self.phase}, s{self.season})"


class Base60LatticeBridge:
    """A base-60 navigational lattice as a Quilt cell graph."""

    def __init__(self):
        # Lattice cells indexed by (hour60, day60)
        self.cells: Dict[Tuple[int, int], LatticeCell] = {}
        # Edges: between adjacent cells
        self.edges: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

    def add_cell(self, hour60: int, day60: int) -> LatticeCell:
        """Add a cell at a lattice coordinate."""
        cell = LatticeCell(hour60, day60)
        self.cells[(hour60, day60)] = cell
        # Add edges to neighbors
        for dh in [-1, 1]:
            neighbor = ((hour60 + dh) % 60, day60)
            if neighbor in self.cells:
                self.edges.append(((hour60, day60), neighbor))
        for dd in [-1, 1]:
            neighbor = (hour60, (day60 + dd) % 60)
            if neighbor in self.cells:
                self.edges.append(((hour60, day60), neighbor))
        return cell

    def from_timestamp(self, hour: int, minute: int, day_of_year: int) -> LatticeCell:
        """Convert timestamp to lattice cell. Z_in."""
        hour60 = int((hour * 60 + minute) / 60) % 60
        day60 = int(day_of_year * 60 / 365) % 60
        return self.add_cell(hour60, day60)

    def query(self, hour60: int, day60: int) -> LatticeCell:
        """Query a cell. Z_out."""
        return self.cells.get((hour60, day60))

    def to_cell_graph(self) -> Dict[str, Any]:
        """Convert to a cell graph representation."""
        return {
            'cells': [
                {'id': f"h{h}_d{d}", 'hour60': h, 'day60': d, 'gamma': 0.5, 'eta': 0.5}
                for (h, d), c in self.cells.items()
            ],
            'edges': [
                {'from': f"h{a[0]}_d{a[1]}", 'to': f"h{b[0]}_d{b[1]}"}
                for (a, b) in self.edges
            ],
        }

    def verify_conservation(self) -> bool:
        """γ+η=1 across all cells."""
        for c in self.cells.values():
            if abs(c.gamma + c.eta - 1.0) > 1e-9:
                return False
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("BASE60-LATTICE ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Sexagesimal navigational lattice as Quilt cell graph.")
    print("Time IS a graph coordinate. The clock IS a Quilt tape.")
    print()

    lattice = Base60LatticeBridge()

    # Add some cells
    for h in range(0, 24, 4):
        for d in range(0, 12, 2):
            lattice.add_cell(h, d)

    # Query
    cell = lattice.query(12, 6)
    if cell:
        print(f"Query (12h, day 6): {cell}")
    print()

    # From timestamp
    ts_cell = lattice.from_timestamp(14, 30, 100)
    print(f"From timestamp (14:30, day 100): {ts_cell}")
    print()

    # Cell graph
    graph = lattice.to_cell_graph()
    print(f"Cell graph: {len(graph['cells'])} cells, {len(graph['edges'])} edges")
    print()

    # Conservation
    n = len(lattice.cells)
    total = sum(c.gamma + c.eta for c in lattice.cells.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("The sexagesimal lattice IS a Quilt cell graph.")
    print("Time IS a graph coordinate. The clock IS a Quilt tape.")


if __name__ == "__main__":
    demo()
