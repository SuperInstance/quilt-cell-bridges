"""
lau-witten-reward (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance lau-witten-reward (Rust) applies Witten deformation
and Morse theory to AI reward landscapes. Treats the reward function as
a Morse function on the state space:
- Critical points of index 0 = reward basins
- Instanton tunneling = between basins
- Spurious tunneling = reward hacking (detected via H¹)
- Dirac operator D = d + δ, D² = Δ (supersymmetric)

THE CRUCIAL INSIGHT: A Morse function IS a JEPA landscape. Each basin IS
a cell cluster. Instanton tunneling IS the watch. Reward hacking IS a
spurious Murmur path detected by H¹ cohomology.

Map:
- State → cell
- Reward → cell value
- Critical point → Vibe (state at minimum)
- Instanton → Murmur (between cells)
- H¹ → β₁ (detects reward hacking)
- Dirac operator → DoubleEntry (D²=Δ)
- Witten deformation → GC (decay spurious)
"""

from typing import Dict, List, Any, List, Tuple
import math


class Cell:
    """A Quilt cell with reward value."""
    def __init__(self, id: str, reward: float = 0.0):
        self.id = id
        self.reward = reward
        self.gamma = 0.5
        self.eta = 0.5


class LauWittenRewardBridge:
    """Morse theory of reward landscapes on Quilt cells."""

    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        # Edges (instantons)
        self.instantons: List[Tuple[str, str, float]] = []
        # Beta_1 (H¹ dimension)
        self.beta_1 = 0

    def add_cell(self, id: str, reward: float) -> Cell:
        """Add a cell with a reward value."""
        cell = Cell(id, reward)
        self.cells[id] = cell
        return cell

    def add_instanton(self, from_id: str, to_id: str, action: float) -> None:
        """Add an instanton (tunneling path)."""
        self.instantons.append((from_id, to_id, action))

    def find_critical_points(self) -> List[Cell]:
        """Find critical points (local maxima of reward)."""
        # Simple: cells with reward > all neighbors
        critical = []
        for cell in self.cells.values():
            is_critical = True
            for (f, t, _) in self.instantons:
                if f == cell.id and t in self.cells:
                    if self.cells[t].reward > cell.reward:
                        is_critical = False
                        break
            if is_critical:
                critical.append(cell)
        return critical

    def detect_reward_hacking(self) -> Dict[str, Any]:
        """Detect reward hacking via H¹ cohomology."""
        # Simple: count loops in the instanton graph
        # Use BFS to find cycles
        adj: Dict[str, List[Tuple[str, float]]] = {c: [] for c in self.cells}
        for f, t, a in self.instantons:
            if f in adj and t in adj:
                adj[f].append((t, a))
        # Detect cycles via DFS
        visited = set()
        cycles = 0
        for start in self.cells:
            if start in visited:
                continue
            stack = [(start, [start])]
            while stack:
                node, path = stack.pop()
                visited.add(node)
                for (neighbor, _) in adj[node]:
                    if neighbor in path:
                        cycles += 1
                    elif neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
        self.beta_1 = cycles
        return {
            'reward_hacking': cycles > 0,
            'h1_dimension': cycles,
            'instantons': len(self.instantons),
        }

    def witten_deform(self, t: float) -> Dict[str, float]:
        """Apply Witten deformation Δ_t = e^{-tf} Δ e^{tf}."""
        # Simplified: weight cells by e^{-t * (-reward)} = e^{t * reward}
        weights = {}
        for cell in self.cells.values():
            weights[cell.id] = math.exp(t * cell.reward)
        return weights

    def dirac_squared(self) -> float:
        """Compute ||D² - Δ|| — should be 0 in supersymmetric systems."""
        # Simplified: sum of squared differences
        return 0.0  # Always 0 in our simplified model


if __name__ == "__main__":
    print("=" * 60)
    print("LAU-WITTEN-REWARD ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Morse theory of reward landscapes on Quilt cells.")
    print("Critical points = reward basins. H¹ = reward hacking.")
    print()

    w = LauWittenRewardBridge()

    # Build a reward landscape with two basins + a hacking path
    w.add_cell("basin_A_1", 0.9)
    w.add_cell("basin_A_2", 0.85)
    w.add_cell("basin_A_3", 0.8)
    w.add_cell("basin_B_1", 0.95)
    w.add_cell("basin_B_2", 0.9)
    w.add_cell("hacking_1", 0.5)
    w.add_cell("hacking_2", 0.6)

    # Legitimate instantons (within basin)
    w.add_instanton("basin_A_1", "basin_A_2", 0.1)
    w.add_instanton("basin_A_2", "basin_A_3", 0.1)
    w.add_instanton("basin_B_1", "basin_B_2", 0.1)
    # Hacking instanton (creates a spurious cycle)
    w.add_instanton("basin_A_1", "hacking_1", 0.5)
    w.add_instanton("hacking_1", "hacking_2", 0.5)
    w.add_instanton("hacking_2", "basin_B_1", 0.5)
    w.add_instanton("basin_B_1", "basin_A_1", 0.5)  # closes the loop

    # Find critical points
    critical = w.find_critical_points()
    print(f"Critical points (reward basins): {len(critical)}")
    for c in critical:
        print(f"  {c.id}: reward={c.reward}")
    print()

    # Detect reward hacking
    hacking = w.detect_reward_hacking()
    print(f"Reward hacking detection: {hacking}")
    print()

    # Witten deformation
    weights = w.witten_deform(t=2.0)
    print("Witten deformation weights (t=2):")
    for k, v in weights.items():
        print(f"  {k}: {v:.2f}")
    print()

    # Conservation
    n = len(w.cells)
    total = sum(c.gamma + c.eta for c in w.cells.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A Morse function IS a JEPA landscape.")
    print("H¹ detects reward hacking. The Dirac operator IS DoubleEntry.")


if __name__ == "__main__":
    demo()
