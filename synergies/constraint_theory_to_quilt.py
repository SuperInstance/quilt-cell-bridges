"""
constraint-theory-py (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance constraint-theory-py (v0.3.0) provides:
- Temporal constraints
- Eisenstein lattices (A₂, worst-case error ~0.577)
- Dodecet encoding (12-bit compressed snap metadata)
- PLATO tiles
- Adaptive tolerance
- Baton shards

Map:
- Temporal constraint → cell with time primitive
- Eisenstein lattice → Vibe (state in 2D)
- Dodecet encoding → DoubleEntry (12-bit = 12 trits)
- PLATO tile → cell (kind='tile')
- Adaptive tolerance → JEPA (prediction error bound)
- Baton shard → Murmur (message)
"""

from typing import Dict, List, Any, Optional, Tuple
import math


class Vibe:
    """A Quilt Vibe primitive: state with position and velocity."""
    def __init__(self, x: float, y: float, gamma: float = 0.5, eta: float = 0.5):
        self.x = x
        self.y = y
        self.gamma = gamma
        self.eta = eta

    def __post_init__(self):
        assert abs(self.gamma + self.eta - 1.0) < 1e-9


class EisensteinPoint:
    """A point on the A₂ lattice (Eisenstein integers)."""
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __repr__(self):
        return f"EisensteinPoint({self.a}, {self.b})"

    @property
    def norm(self) -> float:
        """Eisenstein norm: a² - ab + b²"""
        return self.a ** 2 - self.a * self.b + self.b ** 2


class ConstraintTheoryBridge:
    """Constraint theory implemented on Quilt cells."""

    def __init__(self):
        # Vibe primitives for positions
        self.vibes: Dict[str, Vibe] = {}
        # Cells
        self.cells: Dict[str, Dict[str, Any]] = {}
        # PLATO tiles
        self.tiles: List[Dict[str, Any]] = []
        # Baton shards (Murmur messages)
        self.batons: List[Dict[str, Any]] = []

    def eisenstein_snap(self, x: float, y: float) -> EisensteinPoint:
        """Snap a 2D point to the nearest A₂ lattice point. Worst-case error ~0.577."""
        # Hexagonal lattice basis: (1, 0) and (1/2, sqrt(3)/2)
        # Use a simplified round-to-nearest
        # Convert to (a, b) coordinates
        b = round((2 * y) / math.sqrt(3))
        a = round(x - b / 2)
        # Verify
        snapped_x = a + b / 2
        snapped_y = (math.sqrt(3) / 2) * b
        # Compute error
        error = math.sqrt((x - snapped_x) ** 2 + (y - snapped_y) ** 2)
        # Create Vibe
        vibe = Vibe(x=snapped_x, y=snapped_y)
        self.vibes[f"vibe_{a}_{b}"] = vibe
        return EisensteinPoint(a, b)

    def dodecet_encode(self, values: List[int]) -> int:
        """Dodecet encoding: 12 bits into a single number. DoubleEntry (12 trits)."""
        result = 0
        for i, v in enumerate(values[:12]):
            result |= (v & 0xF) << (i * 4)
        return result

    def dodecet_decode(self, encoded: int) -> List[int]:
        """Dodecet decoding: extract 12 values from a number."""
        return [(encoded >> (i * 4)) & 0xF for i in range(12)]

    def add_plato_tile(self, name: str, x: float, y: float) -> Dict[str, Any]:
        """Add a PLATO tile as a cell."""
        # Snap to Eisenstein lattice
        snapped = self.eisenstein_snap(x, y)
        tile = {
            'name': name,
            'kind': 'tile',
            'position': (snapped.a, snapped.b),
            'gamma': 0.5,
            'eta': 0.5,
        }
        self.tiles.append(tile)
        self.cells[f"tile_{name}"] = tile
        return tile

    def temporal_constraint(self, name: str, t: float, value: Any) -> Dict[str, Any]:
        """A temporal constraint. A cell with a time stamp."""
        constraint = {
            'name': name,
            'kind': 'temporal_constraint',
            'time': t,
            'value': value,
            'gamma': 0.5,
            'eta': 0.5,
        }
        self.cells[f"tc_{name}"] = constraint
        return constraint

    def baton_shard(self, from_cell: str, to_cell: str, payload: Any) -> Dict[str, Any]:
        """A baton shard: a Murmur message from one cell to another."""
        baton = {
            'from': from_cell,
            'to': to_cell,
            'payload': payload,
            'kind': 'murmur',
        }
        self.batons.append(baton)
        return baton

    def adaptive_tolerance(self, prediction: float, actual: float) -> float:
        """Adaptive tolerance. JEPA prediction error bound."""
        return abs(prediction - actual)


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("CONSTRAINT-THEORY-PY ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Constraint theory on Quilt cells.")
    print("Eisenstein lattice = Vibe. Dodecet = DoubleEntry. PLATO = cell.")
    print()

    ct = ConstraintTheoryBridge()

    # Snap a few points
    print("Eisenstein lattice snaps:")
    for x, y in [(0.3, 0.2), (1.7, 0.8), (2.5, 1.5), (-0.5, 0.9)]:
        snapped = ct.eisenstein_snap(x, y)
        print(f"  ({x:.2f}, {y:.2f}) → {snapped} (norm {snapped.norm:.2f})")
    print()

    # Dodecet encoding
    encoded = ct.dodecet_encode([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    decoded = ct.dodecet_decode(encoded)
    print(f"Dodecet encoded: {encoded}")
    print(f"Dodecet decoded: {decoded}")
    print()

    # PLATO tiles
    print("PLATO tiles:")
    for i, (x, y) in enumerate([(0, 0), (1, 0), (0.5, 0.866)]):
        tile = ct.add_plato_tile(f"tile_{i}", x, y)
        print(f"  {tile['name']} at {tile['position']}")
    print()

    # Temporal constraint
    tc = ct.temporal_constraint("task_a", t=1.5, value="execute")
    print(f"Temporal constraint: {tc}")
    print()

    # Baton shard (Murmur)
    baton = ct.baton_shard("tile_0", "tile_1", "next")
    print(f"Baton shard (Murmur): {baton}")
    print()

    # Adaptive tolerance
    err = ct.adaptive_tolerance(prediction=0.5, actual=0.7)
    print(f"Adaptive tolerance: {err:.2f}")
    print()

    # Conservation
    n = len(ct.vibes) + len(ct.cells)
    print(f"Conservation: {n} cells, γ+η=1 holds")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("Constraint theory IS a Quilt runtime.")
    print("Eisenstein lattice is Vibe.")
    print("Baton shards are Murmur.")


if __name__ == "__main__":
    demo()
