"""
noether-guard (SuperInstance) ↔ Quilt Cell Bridge

noether-guard is a physics linter that uses Noether's theorem for
conservation law verification with RG-style drift detection.

Noether: every differentiable symmetry of a physical system has a
corresponding conservation law.

Quilt's conservation law: γ + η = C
The symmetry: cell graph transformations (merge, split, evolve)
The conserved quantity: γ + η
The drift: cells that violate the conservation

This bridge treats the cell graph as a physical system, applies Noether's
theorem, and detects drift over time.
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class Cell:
    """A Quilt cell as a physical system."""
    def __init__(self, id: str, value: float = 0.0, gamma: float = 0.5, eta: float = 0.5):
        self.id = id
        self.value = value
        self.gamma = gamma
        self.eta = eta
        # Conservation: γ + η = 1
        if abs(gamma + eta - 1.0) > 1e-9:
            self.eta = 1.0 - gamma

    def conserved(self) -> bool:
        return abs(self.gamma + self.eta - 1.0) < 1e-6

    def violation(self) -> float:
        """The magnitude of the conservation violation."""
        return abs(self.gamma + self.eta - 1.0)

    def __repr__(self):
        return f"Cell({self.id}, γ={self.gamma:.3f}, η={self.eta:.3f})"


class NoetherGuard:
    """The Noether guard. Watches the cell graph for conservation violations."""

    def __init__(self, tolerance: float = 1e-6):
        self.tolerance = tolerance
        self.history: List[Tuple[float, float]] = []  # (t, health)

    def check_conservation(self, cells: List[Cell]) -> float:
        """Check the fleet-wide conservation. Returns health score 0-1."""
        if not cells:
            return 1.0
        total_gamma = sum(c.gamma for c in cells)
        total_eta = sum(c.eta for c in cells)
        n = len(cells)
        expected = float(n)
        actual = total_gamma + total_eta
        deviation = abs(actual - expected)
        # Health = 1 - normalized deviation
        if expected == 0:
            return 1.0 if deviation == 0 else 0.0
        health = max(0.0, 1.0 - deviation / expected)
        return health

    def violations(self, cells: List[Cell]) -> List[Cell]:
        """Return cells that violate the conservation law."""
        return [c for c in cells if c.violation() > self.tolerance]

    def detect_drift(self, trajectories: Dict[str, List[float]]) -> Dict[str, float]:
        """Detect drift over time in a set of trajectories.
        
        A trajectory is a time series of γ+η values. Drift is the slope.
        """
        drifts = {}
        for cell_id, values in trajectories.items():
            if len(values) < 2:
                drifts[cell_id] = 0.0
                continue
            # Linear regression slope
            n = len(values)
            x_mean = (n - 1) / 2.0
            y_mean = sum(values) / n
            num = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
            den = sum((i - x_mean) ** 2 for i in range(n))
            slope = num / den if den > 0 else 0.0
            drifts[cell_id] = slope
        return drifts

    def renormalize(self, cells: List[Cell], block_size: int = 2) -> List[Cell]:
        """RG-style renormalization: coarse-grain by merging cells.
        
        Each block of `block_size` cells is replaced by one cell whose
        γ is the average (so conservation is preserved).
        """
        new_cells = []
        for i in range(0, len(cells), block_size):
            block = cells[i:i + block_size]
            if not block:
                continue
            avg_gamma = sum(c.gamma for c in block) / len(block)
            new_id = f"RG_{i//block_size}"
            new_cells.append(Cell(id=new_id, gamma=avg_gamma, eta=1.0 - avg_gamma))
        return new_cells

    def tick(self, cells: List[Cell], t: float) -> float:
        """The watch ticks. Records the health at this time."""
        health = self.check_conservation(cells)
        self.history.append((t, health))
        return health

    def trend(self) -> str:
        """The drift trend: improving, stable, or degrading."""
        if len(self.history) < 2:
            return "STABLE"
        recent = self.history[-5:]
        h0 = recent[0][1]
        h1 = recent[-1][1]
        diff = h1 - h0
        if diff > 0.05:
            return "IMPROVING"
        elif diff < -0.05:
            return "DEGRADING"
        return "STABLE"


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("NOETHER-GUARD ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Noether's theorem: every symmetry has a conservation law.")
    print("Quilt's symmetry: cell graph transformations.")
    print("Quilt's conservation: γ + η = C.")
    print()

    # Create the guard (the watch)
    guard = NoetherGuard()

    # Create 10 cells (the fleet)
    cells = [
        Cell(f"c{i}", value=i * 0.1, gamma=0.5 + (i % 3 - 1) * 0.05, eta=0.5 - (i % 3 - 1) * 0.05)
        for i in range(10)
    ]

    # Force one violation
    cells[3].gamma = 0.7
    cells[3].eta = 0.4  # violation: γ + η = 1.1

    # Check conservation
    health = guard.check_conservation(cells)
    print(f"Fleet health: {health:.4f}")
    print(f"Violations: {len(guard.violations(cells))} cells")
    for v in guard.violations(cells):
        print(f"  - {v} (deviation: {v.violation():.4f})")
    print()

    # Tick (the watch records)
    for t in range(5):
        h = guard.tick(cells, t * 1.0)

    print(f"Trend: {guard.trend()}")
    print(f"History: {[(round(t, 2), round(h, 4)) for t, h in guard.history]}")
    print()

    # Detect drift
    trajectories = {
        "mood.feeling": [1.0, 1.001, 1.002, 1.003, 1.005, 1.01],
        "weather.temp": [1.0, 0.99, 0.98, 0.96, 0.93, 0.89],
        "stable.cell":  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    }
    drifts = guard.detect_drift(trajectories)
    print("Drift detection:")
    for cell_id, slope in drifts.items():
        direction = "drifting up" if slope > 0 else "drifting down" if slope < 0 else "stable"
        print(f"  - {cell_id}: slope={slope:.6f} ({direction})")
    print()

    # Renormalize (RG-style coarsening)
    coarse = guard.renormalize(cells, block_size=2)
    print(f"Renormalized 10 cells → {len(coarse)} cells (block size 2)")
    for c in coarse:
        print(f"  {c}")
    print()

    # Verify the new cells are conserved
    new_health = guard.check_conservation(coarse)
    print(f"After renormalization, health: {new_health:.4f}")
    print()

    print("=" * 60)
    print("BRIDGE SUMMARY")
    print("=" * 60)
    print("✓ Noether's theorem maps to Quilt: symmetry → γ+η=C")
    print("✓ Health score 0-1 measures fleet conservation")
    print("✓ Violations are detected (cells with γ+η≠C)")
    print("✓ Drift is detected (linear slope of γ+η over time)")
    print("✓ Renormalization is RG-style coarsening")
    print("✓ Trend is improving / stable / degrading")
    print()
    print("Iron sharpens iron.")
    print("Noether guards the conservation.")
    print("The watch is the Noether guard.")
    print("The conservation is the act of looking.")
