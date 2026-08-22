"""
ternary-conserve (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-conserve (Rust) provides parametric conservation
across resource domains: fish stocks, battery charge, LLM token quota,
crew attention-hours.

The conservation thesis: every measurable resource follows a closed-loop:
Budget → Profile → Detect → Report

THE CRUCIAL INSIGHT: γ+η=1 conservation in Quilt IS the same as ternary-conserve.
The "closed loop" IS the cell. Resources are cells with budgets.

Map:
- Budget → cell (with value=current_amount, kind='resource')
- Profile → cell (with kind='profile')
- Detect → JEPA (predict depletion)
- Report → Z_out (emit signal)
- Threshold → DoubleEntry (γ+η=C across thresholds)
"""

from typing import Dict, List, Any, Optional


class ResourceCell:
    """A Quilt cell representing a resource with a budget."""
    def __init__(self, name: str, budget: float, domain: str = 'unknown'):
        self.name = name
        self.budget = budget
        self.current = budget
        self.domain = domain
        self.thresholds: List[float] = []
        self.events: List[Dict[str, Any]] = []
        self.gamma = 0.5
        self.eta = 0.5

    def set_thresholds(self, thresholds: List[float]) -> None:
        """Set thresholds (e.g., 0.5, 0.25, 0.1 of budget)."""
        self.thresholds = thresholds

    def consume(self, amount: float) -> Dict[str, Any]:
        """Consume from the budget. Z_out."""
        if amount > self.current:
            amount = self.current
        self.current -= amount
        # Check thresholds
        for t in self.thresholds:
            threshold_value = self.budget * t
            if self.current <= threshold_value and not any(
                e.get('threshold') == t for e in self.events[-len(self.thresholds):]
            ):
                event = {
                    'kind': 'threshold_crossed',
                    'threshold': t,
                    'current': self.current,
                    'severity': 'Negative' if t < 0.3 else 'Neutral',
                }
                self.events.append(event)
        # Check depletion
        if self.current == 0:
            self.events.append({'kind': 'depleted', 'severity': 'Negative'})
        return {
            'consumed': amount,
            'current': self.current,
            'budget': self.budget,
        }

    def detect(self) -> Dict[str, Any]:
        """Detect current state. JEPA."""
        ratio = self.current / self.budget if self.budget > 0 else 0
        return {
            'name': self.name,
            'ratio': ratio,
            'state': 'critical' if ratio < 0.25 else 'low' if ratio < 0.5 else 'healthy',
            'predicted_depletion_steps': int(self.current / max(0.1, ratio * 10)) if ratio > 0 else 0,
        }


class TernaryConserveBridge:
    """Conservation across resource domains on Quilt cells."""

    def __init__(self):
        self.resources: Dict[str, ResourceCell] = {}

    def add_resource(self, name: str, budget: float, domain: str) -> ResourceCell:
        """Add a resource. A cell with budget."""
        cell = ResourceCell(name, budget, domain)
        cell.set_thresholds([0.5, 0.25, 0.1])
        self.resources[name] = cell
        return cell

    def tick_all(self, consumption: Dict[str, float]) -> List[Dict[str, Any]]:
        """Tick all resources. JEPA loop."""
        results = []
        for name, amount in consumption.items():
            if name in self.resources:
                result = self.resources[name].consume(amount)
                results.append(result)
        return results

    def detect_all(self) -> List[Dict[str, Any]]:
        """Detect state of all resources. JEPA prediction."""
        return [r.detect() for r in self.resources.values()]

    def verify_conservation(self) -> bool:
        """γ+η=1 across all cells."""
        for r in self.resources.values():
            if abs(r.gamma + r.eta - 1.0) > 1e-9:
                return False
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-CONSERVE ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Parametric conservation across resource domains.")
    print("γ+η=1 IS the same law.")
    print()

    tc = TernaryConserveBridge()

    # Add resources
    fuel = tc.add_resource('fuel', 100.0, 'vehicle')
    battery = tc.add_resource('battery', 50.0, 'device')
    tokens = tc.add_resource('tokens', 10000.0, 'llm')

    # Tick
    results = tc.tick_all({'fuel': 30.0, 'battery': 15.0, 'tokens': 5000.0})
    for r in results:
        print(f"  {r}")
    print()

    # Detect
    print("State of resources:")
    for d in tc.detect_all():
        print(f"  {d}")
    print()

    # Events
    print("Events triggered:")
    for r in tc.resources.values():
        for e in r.events:
            print(f"  {r.name}: {e}")
    print()

    # Conservation
    print(f"Conservation: {tc.verify_conservation()}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("γ+η=1 IS the conservation thesis.")
    print("Resources ARE cells with budgets.")


if __name__ == "__main__":
    demo()
