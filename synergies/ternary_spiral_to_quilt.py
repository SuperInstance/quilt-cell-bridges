"""
ternary-spiral (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-spiral (Rust) implements spiral-wave dynamics
from Rock-Paper-Scissors cyclic dominance on a ternary lattice.
- 3 species (ρ_R, ρ_P, ρ_S) with RPS dominance
- Spiral waves are self-sustaining rotors
- Continuum limit: Reichenbach-Lotka-Volterra PDEs
- Discrete: cellular automaton on ternary lattice

THE CRUCIAL INSIGHT: A spiral wave IS a Quilt cell graph with cyclic
dynamics. The three species ARE three cell types. The spiral IS the
graph topology. RPS dominance IS the Z₃ group.

Map:
- Species (R, P, S) → cell kind
- Spatial lattice → cell graph
- RPS dominance → Z₃ (cyclic mod 3)
- Spiral → connected subgraph
- Reaction-diffusion → Murmur
- Biodiversity metrics → β₀, β₁
"""

from typing import Dict, List, Any, Tuple
import random


class Cell:
    """A Quilt cell representing a species at a location."""
    def __init__(self, x: int, y: int, species: int = 0):
        # 0 = empty, 1 = R, 2 = P, 3 = S
        self.x = x
        self.y = y
        self.species = species
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        symbols = ['.', 'R', 'P', 'S']
        return symbols[self.species]


class TernarySpiralBridge:
    """Spiral wave dynamics on a ternary lattice as Quilt cells."""

    def __init__(self, width: int, height: int, sigma: float = 0.5):
        self.width = width
        self.height = height
        self.sigma = sigma
        # Each cell is a Quilt cell
        self.cells: Dict[Tuple[int, int], Cell] = {}
        for x in range(width):
            for y in range(height):
                self.cells[(x, y)] = Cell(x, y, species=0)

    def get(self, x: int, y: int) -> Cell:
        return self.cells[(x % self.width, y % self.height)]

    def count_neighbors(self, x: int, y: int, target_species: int) -> int:
        """Count neighbors of a target species in 8-neighborhood."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if self.get(x + dx, y + dy).species == target_species:
                    count += 1
        return count

    def step(self) -> None:
        """Run one step of the RPS CA. Each cell is updated."""
        new_species: Dict[Tuple[int, int], int] = {}
        for (x, y), cell in self.cells.items():
            if cell.species == 0:
                # Empty: can be colonized
                n_r = self.count_neighbors(x, y, 1)
                n_p = self.count_neighbors(x, y, 2)
                n_s = self.count_neighbors(x, y, 3)
                total = n_r + n_p + n_s
                if total > 0:
                    # Pick the dominant species
                    if n_r > n_p and n_r > n_s:
                        new_species[(x, y)] = 1
                    elif n_p > n_s:
                        new_species[(x, y)] = 2
                    else:
                        new_species[(x, y)] = 3
                else:
                    new_species[(x, y)] = 0
            else:
                # Occupied: can be replaced by dominant species
                own = cell.species
                # R beats S, S beats P, P beats R
                # R=1, P=2, S=3 → R beats S (3), P beats R (1), S beats P (2)
                if own == 1:  # R
                    threats = 3  # S
                elif own == 2:  # P
                    threats = 1  # R
                else:  # S
                    threats = 2  # P
                n_threats = self.count_neighbors(x, y, threats)
                if n_threats >= 4:  # Threshold
                    new_species[(x, y)] = threats
                else:
                    new_species[(x, y)] = own
        # Apply
        for pos, sp in new_species.items():
            self.cells[pos].species = sp

    def shannon_entropy(self) -> float:
        """Shannon entropy of species distribution. Biodiversity metric."""
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        total = 0
        for cell in self.cells.values():
            counts[cell.species] += 1
            total += 1
        import math
        entropy = 0.0
        for c in counts.values():
            if c > 0 and total > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    def get_graph(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get the cell graph (edges between same-species cells)."""
        edges = []
        for (x, y), cell in self.cells.items():
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = self.get(x + dx, y + dy)
                    if neighbor.species == cell.species and cell.species != 0:
                        edges.append(((x, y), (neighbor.x, neighbor.y)))
        return edges


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-SPIRAL ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Spiral-wave RPS dynamics on ternary lattice as Quilt cells.")
    print("3 species = 3 cell kinds. Spiral = connected subgraph.")
    print()

    spiral = TernarySpiralBridge(width=20, height=20, sigma=0.5)

    # Initialize with a small R-P-S triangle
    spiral.get(10, 10).species = 1  # R
    spiral.get(11, 10).species = 2  # P
    spiral.get(10, 11).species = 3  # S
    spiral.get(11, 11).species = 1  # R

    print("Initial state:")
    for y in range(15):
        for x in range(15):
            cell = spiral.get(x, y)
            print(cell, end='')
        print()
    print()

    # Run 20 steps
    for _ in range(20):
        spiral.step()

    print("After 20 steps:")
    for y in range(15):
        for x in range(15):
            cell = spiral.get(x, y)
            print(cell, end='')
        print()
    print()

    # Biodiversity
    h = spiral.shannon_entropy()
    edges = spiral.get_graph()
    print(f"Shannon entropy (biodiversity): {h:.2f}")
    print(f"Cell graph edges: {len(edges)}")
    print()

    # Conservation
    n = len(spiral.cells)
    total = sum(c.gamma + c.eta for c in spiral.cells.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A spiral wave IS a Quilt cell graph with Z₃ dynamics.")
    print("Three species ARE three cell kinds. RPS IS the Z₃ group.")


if __name__ == "__main__":
    demo()
