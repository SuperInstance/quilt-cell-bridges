"""
style-dna (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance style-dna (Python) extracts a composer's irreducible
musical fingerprint from MIDI corpora. Every composer has a DNA signature
— topological, dynamical, and statistical invariants that survive across
their entire corpus.

- StyleExtractor.extract() — returns DNA fingerprint
- PERSONALITIES — predefined styles
- StyleMorpher — morph music toward target styles

THE CRUCIAL INSIGHT: A composer's DNA IS a Quilt sheet. The fingerprint IS
a cell graph with 8 primitives. Morphing IS JEPA prediction.

Map:
- Composer → cell
- MIDI note → cell value
- DNA fingerprint → Vibe (state of style)
- Topological invariants → β₀, β₁
- Statistical invariants → DoubleEntry
- Morphing → JEPA
"""

from typing import Dict, List, Any
import math


class StyleCell:
    """A Quilt cell representing a style feature."""
    def __init__(self, name: str, value: float = 0.0):
        self.name = name
        self.value = value
        self.gamma = 0.5
        self.eta = 0.5


class StyleDNA:
    """A composer's DNA as a Quilt sheet."""
    def __init__(self, composer: str):
        self.composer = composer
        # Topological features
        self.betti_0: float = 0.0
        self.betti_1: float = 0.0
        # Dynamical features
        self.tempo: float = 120.0
        self.dynamics_range: float = 0.0
        # Statistical features
        self.interval_entropy: float = 0.0
        self.rhythm_complexity: float = 0.0
        # Cells
        self.cells: Dict[str, StyleCell] = {}

    def add_feature(self, name: str, value: float) -> StyleCell:
        """Add a style feature as a cell."""
        cell = StyleCell(name, value)
        self.cells[name] = cell
        return cell

    def to_vector(self) -> List[float]:
        """Convert DNA to a vector. Vibe state."""
        return [
            self.betti_0, self.betti_1,
            self.tempo, self.dynamics_range,
            self.interval_entropy, self.rhythm_complexity,
        ] + [c.value for c in self.cells.values()]

    def distance_to(self, other: 'StyleDNA') -> float:
        """Distance between two DNA fingerprints. JEPA error."""
        v1 = self.to_vector()
        v2 = other.to_vector()
        if len(v1) != len(v2):
            return float('inf')
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def morph_toward(self, target: 'StyleDNA', rate: float = 0.5) -> 'StyleDNA':
        """Morph toward a target style. JEPA prediction."""
        result = StyleDNA(f"{self.composer}_morphed")
        result.betti_0 = self.betti_0 + (target.betti_0 - self.betti_0) * rate
        result.betti_1 = self.betti_1 + (target.betti_1 - self.betti_1) * rate
        result.tempo = self.tempo + (target.tempo - self.tempo) * rate
        result.dynamics_range = self.dynamics_range + (target.dynamics_range - self.dynamics_range) * rate
        result.interval_entropy = self.interval_entropy + (target.interval_entropy - self.interval_entropy) * rate
        result.rhythm_complexity = self.rhythm_complexity + (target.rhythm_complexity - self.rhythm_complexity) * rate
        return result


class StyleDNABridge:
    """Style DNA extraction and morphing on Quilt cells."""

    def __init__(self):
        self.styles: Dict[str, StyleDNA] = {}

    def add_style(self, composer: str, tempo: float = 120, **features) -> StyleDNA:
        """Add a composer's style. A DNA sheet."""
        dna = StyleDNA(composer)
        dna.tempo = tempo
        for name, value in features.items():
            if name == 'betti_0':
                dna.betti_0 = value
            elif name == 'betti_1':
                dna.betti_1 = value
            elif name == 'dynamics_range':
                dna.dynamics_range = value
            elif name == 'interval_entropy':
                dna.interval_entropy = value
            elif name == 'rhythm_complexity':
                dna.rhythm_complexity = value
            else:
                dna.add_feature(name, value)
        self.styles[composer] = dna
        return dna

    def compute_distance(self, composer_a: str, composer_b: str) -> float:
        """Distance between two composers. JEPA error."""
        if composer_a not in self.styles or composer_b not in self.styles:
            return float('inf')
        return self.styles[composer_a].distance_to(self.styles[composer_b])


if __name__ == "__main__":
    print("=" * 60)
    print("STYLE-DNA ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Composer's musical DNA as Quilt sheets.")
    print("DNA fingerprint IS Vibe. Morphing IS JEPA.")
    print()

    sd = StyleDNABridge()

    # Add some composer styles
    bach = sd.add_style("Bach",
                        tempo=108,
                        betti_0=0.5, betti_1=0.1,
                        dynamics_range=0.3,
                        interval_entropy=0.7,
                        rhythm_complexity=0.6)
    beethoven = sd.add_style("Beethoven",
                             tempo=132,
                             betti_0=0.7, betti_1=0.3,
                             dynamics_range=0.8,
                             interval_entropy=0.5,
                             rhythm_complexity=0.7)
    cage = sd.add_style("Cage",
                        tempo=80,
                        betti_0=0.3, betti_1=0.9,
                        dynamics_range=0.5,
                        interval_entropy=0.9,
                        rhythm_complexity=0.4)

    # Distances
    print("Style distances:")
    print(f"  Bach ↔ Beethoven: {sd.compute_distance('Bach', 'Beethoven'):.2f}")
    print(f"  Bach ↔ Cage: {sd.compute_distance('Bach', 'Cage'):.2f}")
    print(f"  Beethoven ↔ Cage: {sd.compute_distance('Beethoven', 'Cage'):.2f}")
    print()

    # Morph
    morphed = bach.morph_toward(beethoven, rate=0.5)
    print(f"Morphed: {morphed.composer}, tempo={morphed.tempo}, betti_1={morphed.betti_1:.2f}")
    print()

    # Conservation
    n = sum(len(s.cells) for s in sd.styles.values())
    total = sum(c.gamma + c.eta for s in sd.styles.values() for c in s.cells.values())
    print(f"Conservation: {n} feature cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A composer's DNA IS a Quilt sheet.")
    print("Fingerprint IS Vibe. Morphing IS JEPA.")


if __name__ == "__main__":
    demo()
