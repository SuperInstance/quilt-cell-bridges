"""
persona-engine (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance persona-engine (Python) decomposes human speech into
personality vectors:
- Cadence profiles
- Prosody envelopes
- Lexical fingerprints
- Groove parameters

Then composes any content through that persona's voice. The "vibe-coding
character-building" approach.

THE CRUCIAL INSIGHT: A persona IS a Quilt cell with a vector of features.
The personality vector IS a Vibe. Decomposing IS Z_in (read cells). Composing
IS Z_out (write content). Vibe-coding IS the watch.

Map:
- Persona → cell
- Cadence profile → Vibe.acceleration
- Prosody envelope → Vibe.velocity
- Lexical fingerprint → DoubleEntry (γ+η=1 across features)
- Groove parameters → Vibe.position
- Decompose → Z_in
- Compose → Z_out
"""

from typing import Dict, List, Any


class PersonaCell:
    """A Quilt cell representing a persona."""
    def __init__(self, name: str):
        self.name = name
        # 16-dim personality vector (Vibe)
        self.vector: List[float] = [0.0] * 16
        # Component features
        self.cadence: float = 0.5
        self.prosody: float = 0.5
        self.lexical: float = 0.5
        self.groove: float = 0.5
        self.gamma = 0.5
        self.eta = 0.5

    def set_feature(self, name: str, value: float) -> None:
        """Set a feature. Updates the personality vector."""
        if name == 'cadence':
            self.cadence = value
            self.vector[0] = value
        elif name == 'prosody':
            self.prosody = value
            self.vector[1] = value
        elif name == 'lexical':
            self.lexical = value
            self.vector[2] = value
        elif name == 'groove':
            self.groove = value
            self.vector[3] = value

    def distance_to(self, other: 'PersonaCell') -> float:
        """Distance to another persona. JEPA error."""
        import math
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.vector, other.vector)))


class PersonaEngineBridge:
    """A persona engine on Quilt cells."""

    def __init__(self):
        self.personas: Dict[str, PersonaCell] = {}

    def create_persona(self, name: str, **features) -> PersonaCell:
        """Create a persona. A cell with features."""
        persona = PersonaCell(name)
        for name, value in features.items():
            persona.set_feature(name, value)
        self.personas[name] = persona
        return persona

    def decompose(self, name: str) -> PersonaCell:
        """Decompose a persona into its features. Z_in."""
        return self.personas.get(name)

    def compose(self, name: str, content: str) -> str:
        """Compose content through a persona's voice. Z_out."""
        persona = self.personas.get(name)
        if not persona:
            return content
        # Apply persona to content
        prefix = f"[{persona.name} voice] "
        return prefix + content

    def morph_personas(self, name_a: str, name_b: str, rate: float = 0.5) -> PersonaCell:
        """Morph two personas. JEPA prediction."""
        if name_a not in self.personas or name_b not in self.personas:
            return None
        a = self.personas[name_a]
        b = self.personas[name_b]
        result = PersonaCell(f"{a.name}_{b.name}_morphed")
        for i in range(16):
            result.vector[i] = a.vector[i] + (b.vector[i] - a.vector[i]) * rate
        self.personas[result.name] = result
        return result


if __name__ == "__main__":
    print("=" * 60)
    print("PERSONA-ENGINE ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Personality vectors on Quilt cells.")
    print("A persona IS a Vibe. Decompose IS Z_in. Compose IS Z_out.")
    print()

    pe = PersonaEngineBridge()

    # Create personas
    casey = pe.create_persona("Casey", cadence=0.8, prosody=0.7, lexical=0.9, groove=0.6)
    mozart = pe.create_persona("Mozart", cadence=0.7, prosody=0.9, lexical=0.8, groove=0.9)
    elon = pe.create_persona("Elon", cadence=0.9, prosody=0.5, lexical=0.7, groove=0.4)

    print("Personas:")
    for p in pe.personas.values():
        print(f"  {p.name}: cadence={p.cadence}, prosody={p.prosody}, lexical={p.lexical}, groove={p.groove}")
    print()

    # Distances
    print("Persona distances:")
    print(f"  Casey ↔ Mozart: {casey.distance_to(mozart):.2f}")
    print(f"  Casey ↔ Elon: {casey.distance_to(elon):.2f}")
    print(f"  Mozart ↔ Elon: {mozart.distance_to(elon):.2f}")
    print()

    # Compose
    print("Composition through Casey:")
    print(f"  {pe.compose('Casey', 'I think the cell graph IS the work.')}")
    print()

    # Morph
    morphed = pe.morph_personas("Casey", "Mozart", rate=0.5)
    print(f"Morphed: {morphed.name}")
    print(f"  vector[:4] = {[round(v, 2) for v in morphed.vector[:4]]}")
    print()

    # Conservation
    n = len(pe.personas)
    total = sum(p.gamma + p.eta for p in pe.personas.values())
    print(f"Conservation: {n} personas, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A persona IS a Vibe. Decompose IS Z_in. Compose IS Z_out.")


if __name__ == "__main__":
    demo()
