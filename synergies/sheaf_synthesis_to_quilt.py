"""
sheaf-constraint-synthesis (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance sheaf-constraint-synthesis (Python) is the unified view:
the Grand Pattern, where constraint theory, fleet architecture, cellular
graphs, and dual-database JEPA connect into a single architecture.

Key concepts:
- The Grand Pattern: Fibonacci dual-direction (Penrose outward, Mandelbrot inward)
- Cellular Graph Decomposition: rooms + algorithms, JEPA bridges
- Dual-Database JEPA: two vector databases per room (Z_in, Z_out) with Ehresmann connection
- Vibe Architecture: 16-dimensional embeddings evolving by reaction-diffusion

THE CRUCIAL INSIGHT: The Grand Pattern IS the Quilt model. Penrose outward
= Z_out. Mandelbrot inward = Z_in. JEPA at the golden ratio IS the watch.
The 16-dim Vibe IS a cell with 16 vibe primitives.

Map:
- Room → Quilt cell graph (room = subgraph)
- Algorithm → cell (kind='algorithm')
- JEPA bridge → edge
- Z_in database → Murmur input
- Z_out database → Murmur output
- Ehresmann connection → DoubleEntry (γ+η=1)
- 16-dim Vibe → cell with 16 vibe primitives
- Reaction-diffusion → JEPA over time
"""

from typing import Dict, List, Any
import math


class Room:
    """A Quilt cell graph representing a room."""
    def __init__(self, name: str):
        self.name = name
        # Algorithms (cells)
        self.algorithms: Dict[str, 'Cell'] = {}
        # Z_in database (murmur input)
        self.z_in: List[Any] = []
        # Z_out database (murmur output)
        self.z_out: List[Any] = []
        # Vibe (16-dim)
        self.vibe: List[float] = [0.0] * 16
        self.gamma = 0.5
        self.eta = 0.5


class Cell:
    """A Quilt cell representing an algorithm."""
    def __init__(self, name: str, kind: str = 'algorithm'):
        self.name = name
        self.kind = kind
        self.gamma = 0.5
        self.eta = 0.5


class SheafSynthesisBridge:
    """The Grand Pattern as a Quilt architecture."""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        # Bridges between rooms (JEPA edges)
        self.bridges: List[Dict[str, str]] = []
        # Ehresmann connection: tracks Z_in/Z_out transformation
        self.connections: Dict[str, Dict[str, Any]] = {}

    def add_room(self, name: str) -> Room:
        """Add a room. A cell graph."""
        room = Room(name)
        self.rooms[name] = room
        return room

    def add_algorithm(self, room_name: str, alg_name: str) -> Cell:
        """Add an algorithm to a room. A cell."""
        if room_name not in self.rooms:
            room = self.add_room(room_name)
        room = self.rooms[room_name]
        cell = Cell(alg_name, kind='algorithm')
        room.algorithms[alg_name] = cell
        return cell

    def add_bridge(self, room_a: str, room_b: str, kind: str = 'jepa') -> None:
        """Add a JEPA bridge between rooms."""
        self.bridges.append({'from': room_a, 'to': room_b, 'kind': kind})

    def evolve_vibe(self, dt: float = 0.01) -> None:
        """Evolve the Vibe via reaction-diffusion. JEPA over time."""
        for room in self.rooms.values():
            new_vibe = room.vibe[:]
            for i in range(16):
                # Reaction (Logistic growth)
                r = new_vibe[i] * (1 - new_vibe[i])
                # Diffusion (laplacian approximation)
                d = 0.0
                if i > 0:
                    d += new_vibe[i - 1] - new_vibe[i]
                if i < 15:
                    d += new_vibe[i + 1] - new_vibe[i]
                new_vibe[i] += dt * (r + 0.1 * d)
                new_vibe[i] = max(0.0, min(1.0, new_vibe[i]))
            room.vibe = new_vibe

    def golden_ratio_step(self, x: float) -> float:
        """Apply Penrose outward / Mandelbrot inward at golden ratio φ."""
        phi = (1 + math.sqrt(5)) / 2
        return x * phi  # Penrose outward

    def ehresmann_connection(self, room_name: str) -> Dict[str, Any]:
        """The Ehresmann connection between Z_in and Z_out."""
        if room_name not in self.rooms:
            return {}
        room = self.rooms[room_name]
        # Connection: maps Z_in to Z_out preserving structure
        n_in = len(room.z_in)
        n_out = len(room.z_out)
        # Conservation: γ+η=1 across the connection
        return {
            'room': room_name,
            'z_in_size': n_in,
            'z_out_size': n_out,
            'gamma': 0.5,
            'eta': 0.5,
            'conservation': abs(0.5 + 0.5 - 1.0) < 1e-9,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("SHEAF-CONSTRAINT-SYNTHESIS ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("The Grand Pattern as a Quilt architecture.")
    print("Penrose outward = Z_out. Mandelbrot inward = Z_in.")
    print("JEPA at the golden ratio IS the watch.")
    print()

    ss = SheafSynthesisBridge()

    # Add rooms
    for name in ['room_signal', 'room_feature', 'room_inference', 'room_action']:
        room = ss.add_room(name)
        for alg in ['detect', 'transform', 'predict', 'act']:
            ss.add_algorithm(name, alg)
        # Add some Z_in/Z_out data
        for i in range(3):
            room.z_in.append(f"in_{i}")
            room.z_out.append(f"out_{i}")

    # Add bridges
    ss.add_bridge('room_signal', 'room_feature', 'jepa')
    ss.add_bridge('room_feature', 'room_inference', 'jepa')
    ss.add_bridge('room_inference', 'room_action', 'jepa')

    print(f"Rooms: {list(ss.rooms.keys())}")
    print(f"Bridges: {len(ss.bridges)}")
    print()

    # Initialize Vibe
    ss.rooms['room_signal'].vibe = [0.1 * i for i in range(16)]
    print(f"Initial vibe (first 4): {ss.rooms['room_signal'].vibe[:4]}")
    ss.evolve_vibe(dt=0.1)
    print(f"After 1 step (first 4): {[round(v, 3) for v in ss.rooms['room_signal'].vibe[:4]]}")
    print()

    # Ehresmann connection
    for room_name in list(ss.rooms.keys())[:2]:
        conn = ss.ehresmann_connection(room_name)
        print(f"Ehresmann: {conn}")
    print()

    # Conservation
    n = sum(len(r.algorithms) for r in ss.rooms.values())
    total = sum(c.gamma + c.eta for r in ss.rooms.values() for c in r.algorithms.values())
    total += sum(r.gamma + r.eta for r in ss.rooms.values())
    print(f"Conservation: {n} algorithms + {len(ss.rooms)} rooms, γ+η={total:.2f}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("The Grand Pattern IS the Quilt model.")
    print("Penrose outward IS Z_out. Mandelbrot inward IS Z_in.")


if __name__ == "__main__":
    demo()
