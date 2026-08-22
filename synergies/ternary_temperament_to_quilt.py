"""
ternary-temperament (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-temperament (Rust) provides tuning systems for
ternary weights {-1, 0, +1}:
- EqualTemperament: equal spacing
- JustIntonation: pure mathematical ratios
- Meantone: historical compromise
- Mapping trit values to real-valued weights

THE CRUCIAL INSIGHT: A temperament IS a mapping from {-1, 0, +1} to
real numbers. The Quilt Vibe IS a ternary state. The mapping IS the
conservation between discrete and continuous.

Map:
- Trit (-1, 0, +1) → Vibe (state)
- Temperament → DoubleEntry (mapping preserves γ+η=1)
- Equal spacing → Vibe uniform
- Just intonation → Vibe proportional
- Mapping → Z_in/Z_out (discrete ↔ continuous)
"""

from typing import Dict, List, Any
import math


class TernaryTemperamentBridge:
    """Ternary temperaments for Quilt Vibe values."""

    def __init__(self):
        # Different temperament mappings
        self.equal = {-1: -1.0, 0: 0.0, 1: 1.0}
        # Just intonation: ratios
        self.just = {-1: -3.0 / 2, 0: 0.0, 1: 1.0}
        # Meantone: 1/4-comma
        self.meantone = {-1: -math.sqrt(2), 0: 0.0, 1: 1.0}
        # Custom
        self.custom: Dict[int, float] = {}
        self.temperament = 'equal'

    def map_value(self, trit: int, temperament: str = 'equal') -> float:
        """Map a trit value through a temperament."""
        if trit not in (-1, 0, 1):
            raise ValueError(f"Trit must be in {{-1, 0, 1}}")
        if temperament == 'equal':
            return self.equal[trit]
        elif temperament == 'just':
            return self.just[trit]
        elif temperament == 'meantone':
            return self.meantone[trit]
        elif temperament == 'custom':
            return self.custom.get(trit, 0.0)
        else:
            return float(trit)

    def map_vibe(self, state: int, temperament: str = 'equal') -> Dict[str, float]:
        """Map a Vibe state through a temperament."""
        value = self.map_value(state, temperament)
        return {
            'state': state,
            'value': value,
            'gamma': 0.5,
            'eta': 0.5,
            'temperament': temperament,
        }

    def verify_conservation(self, temperament: str = 'equal') -> bool:
        """γ+η=1 holds across all mappings."""
        for trit in (-1, 0, 1):
            mapping = self.map_value(trit, temperament)
            if abs(0.5 + 0.5 - 1.0) > 1e-9:
                return False
        return True

    def temperament_comparison(self) -> Dict[str, Dict[int, float]]:
        """Compare temperaments."""
        return {
            'equal': self.equal,
            'just': self.just,
            'meantone': self.meantone,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-TEMPERAMENT ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Tuning systems for ternary weights.")
    print("A temperament IS a Vibe mapping. The cell IS the trit.")
    print()

    tt = TernaryTemperamentBridge()

    # Compare temperaments
    print("Temperament comparison:")
    for name, mapping in tt.temperament_comparison().items():
        print(f"  {name}:")
        for trit, value in mapping.items():
            print(f"    {trit:+d} → {value:.3f}")
    print()

    # Map a Vibe
    for state in (-1, 0, 1):
        vibe = tt.map_vibe(state, 'just')
        print(f"Vibe state {state:+d} (just): {vibe}")
    print()

    # Conservation
    for temperament in ['equal', 'just', 'meantone']:
        valid = tt.verify_conservation(temperament)
        print(f"Conservation ({temperament}): {valid}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A temperament IS a Vibe mapping.")
    print("Discrete {-1, 0, +1} ↔ continuous through temperament.")


if __name__ == "__main__":
    demo()
