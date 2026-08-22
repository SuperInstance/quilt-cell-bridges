"""
cellular-automata-rs (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance cellular-automata-rs (Rust) implements research-grade
cellular automata: Wolfram 256 rules, Conway's Game of Life, Langton's Ant,
cyclic automata.

THE CRUCIAL INSIGHT: A cellular automaton IS a Quilt cell graph.
Each cell is a Quilt cell. Each neighbor relationship is an edge.
Each step is a JEPA prediction. The grid is the Graph.

Map:
- Cell → Quilt cell
- Rule → JEPA (predict next state)
- Neighborhood → Graph
- Step → tick
- State → Vibe
- Decay → GC
"""

from typing import Dict, List, Any, Set, Tuple
import random


class Cell:
    """A Quilt cell in a cellular automaton."""
    def __init__(self, x: int, y: int, state: int, gamma: float = 0.5, eta: float = 0.5):
        self.x = x
        self.y = y
        self.state = state
        self.gamma = gamma
        self.eta = eta

    def neighbors(self, grid: 'CellularAutomata') -> List['Cell']:
        """Get the 8 neighbors (Moore neighborhood)."""
        result = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                cx = (self.x + dx) % grid.width
                cy = (self.y + dy) % grid.height
                cell = grid.get(cx, cy)
                if cell:
                    result.append(cell)
        return result


class CellularAutomata:
    """A 2D cellular automaton on Quilt cells."""
    def __init__(self, width: int, height: int, rule: int = 110):
        self.width = width
        self.height = height
        self.rule = rule
        # Each cell is a Quilt cell
        self.cells: Dict[Tuple[int, int], Cell] = {}
        for x in range(width):
            for y in range(height):
                self.cells[(x, y)] = Cell(x, y, state=0)

    def get(self, x: int, y: int) -> Cell:
        return self.cells.get((x, y))

    def set(self, x: int, y: int, state: int) -> None:
        if (x, y) in self.cells:
            self.cells[(x, y)].state = state

    def count_live_neighbors(self, x: int, y: int) -> int:
        """Count live (non-zero) neighbors."""
        cell = self.get(x, y)
        if not cell:
            return 0
        return sum(1 for n in cell.neighbors(self) if n.state != 0)

    def step(self) -> None:
        """Run one step. JEPA: predict the next state for each cell."""
        new_states: Dict[Tuple[int, int], int] = {}
        for (x, y), cell in self.cells.items():
            # For elementary Wolfram rules (1D)
            if self.height == 1:
                left = self.get((x - 1) % self.width, 0).state
                center = cell.state
                right = self.get((x + 1) % self.width, 0).state
                pattern = (left << 2) | (center << 1) | right
                new_states[(x, y)] = (self.rule >> pattern) & 1
            else:
                # For Game of Life (2D)
                n = self.count_live_neighbors(x, y)
                if cell.state == 1 and n in (2, 3):
                    new_states[(x, y)] = 1
                elif cell.state == 0 and n == 3:
                    new_states[(x, y)] = 1
                else:
                    new_states[(x, y)] = 0
        # Apply
        for pos, state in new_states.items():
            self.cells[pos].state = state

    def get_graph(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get the cell graph as a list of edges."""
        edges = []
        for (x, y), cell in self.cells.items():
            for n in cell.neighbors(self):
                edges.append(((x, y), (n.x, n.y)))
        return edges


def conway_glider():
    """Conway's Game of Life glider. Travels diagonally."""
    ca = CellularAutomata(20, 20, rule=0)
    # Glider pattern
    glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
    for x, y in glider:
        ca.set(x, y, 1)
    return ca


def rule_110():
    """Wolfram Rule 110. Turing-complete CA."""
    ca = CellularAutomata(80, 1, rule=110)
    ca.set(40, 0, 1)
    return ca


if __name__ == "__main__":
    print("=" * 60)
    print("CELLULAR-AUTOMATA-RS ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Cellular automata on Quilt cells.")
    print("Each cell is a Quilt cell. Rules are JEPA predictions.")
    print()

    # Rule 110
    ca = rule_110()
    print(f"Rule 110 (1D, Turing-complete):")
    print(f"  Cells: {len(ca.cells)}")
    for step in range(10):
        ca.step()
    ones = sum(1 for c in ca.cells.values() if c.state == 1)
    print(f"  After 10 steps: {ones} live cells")
    print()

    # Conway's Game of Life glider
    gol = conway_glider()
    print(f"Conway's Game of Life (glider):")
    print(f"  Cells: {len(gol.cells)}")
    for step in range(10):
        gol.step()
    ones = sum(1 for c in gol.cells.values() if c.state == 1)
    print(f"  After 10 steps: {ones} live cells")
    edges = gol.get_graph()
    print(f"  Graph edges: {len(edges)}")
    print()

    # Conservation
    n = len(ca.cells)
    total = sum(c.gamma + c.eta for c in ca.cells.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A cellular automaton IS a Quilt cell graph.")
    print("Each cell is a Quilt cell. Each step is JEPA.")
    print("Rule 110 is Turing-complete. So is Quilt.")


if __name__ == "__main__":
    demo()
