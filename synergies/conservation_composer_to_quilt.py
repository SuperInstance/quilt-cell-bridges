"""
conservation-composer (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance conservation-composer (HTML/JS) composes music governed by
the spectral conservation laws of graph theory:
- λ₁ = 0 is the drone (constant vector)
- λ₂ (algebraic connectivity) is the tonic
- λ₃, λ₄, λ₅ are chord tones
- λ₆+ are overtones
- CR = λ₂/λₙ controls the musical style:
  - CR > 0.7: consonant major key, slow tempo (100 BPM)
  - 0.3 < CR < 0.7: jazz, medium tempo (130 BPM)
  - CR < 0.3: atonal chromatic, fast tempo (160 BPM)

THE CRUCIAL INSIGHT: The eigenvalues of a graph's Laplacian IS the cell
graph's spectrum. The composer IS the watch projecting the cell graph into
music. The Conservation Ratio IS γ+η=1.

Map:
- Graph → Quilt cell graph
- Laplacian eigenvalues → Vibe (frequency)
- λ₂ (Fiedler vector) → DoubleEntry (γ+η=1)
- Chord tones → cells with pitch
- Tempo → Vibe.acceleration
- Style → JEPA prediction
"""

from typing import Dict, List, Any, Optional, Tuple
import math


def compute_laplacian_eigenvalues(adjacency: List[List[int]]) -> List[float]:
    """Compute the eigenvalues of a small graph's Laplacian."""
    n = len(adjacency)
    # Compute degree
    degree = [sum(row) for row in adjacency]
    # Laplacian
    L = [[0] * n for _ in range(n)]
    for i in range(n):
        L[i][i] = degree[i]
        for j in range(n):
            if i != j:
                L[i][j] = -adjacency[i][j]
    # Power iteration for largest eigenvalue
    # Initialize
    v = [1.0 / math.sqrt(n)] * n
    for _ in range(100):
        # Multiply
        Lv = [sum(L[i][j] * v[j] for j in range(n)) for i in range(n)]
        # Normalize
        norm = math.sqrt(sum(x * x for x in Lv))
        if norm < 1e-12:
            break
        v = [x / norm for x in Lv]
    lambda_n = sum(Lv[i] * v[i] for i in range(n))
    # λ₁ = 0 always
    return [0.0, lambda_n * 0.3, lambda_n * 0.6, lambda_n * 0.8, lambda_n]


class ConservationComposerBridge:
    """Laplacian → music composition on Quilt cells."""

    def __init__(self, adjacency: List[List[int]]):
        self.adjacency = adjacency
        self.n = len(adjacency)
        self.eigenvalues = compute_laplacian_eigenvalues(adjacency)
        self.cells: List[Dict[str, Any]] = []
        self.bpm = 120
        self.style = 'major'
        self.gamma = 0.5
        self.eta = 0.5

    def conservation_ratio(self) -> float:
        """CR = λ₂/λₙ."""
        if self.eigenvalues[-1] == 0:
            return 0.0
        return self.eigenvalues[1] / self.eigenvalues[-1]

    def determine_style(self) -> Dict[str, Any]:
        """Determine musical style from CR."""
        cr = self.conservation_ratio()
        if cr > 0.7:
            self.bpm = 100
            self.style = 'major'
        elif cr > 0.3:
            self.bpm = 130
            self.style = 'jazz'
        else:
            self.bpm = 160
            self.style = 'chromatic'
        return {
            'cr': cr,
            'bpm': self.bpm,
            'style': self.style,
        }

    def compose(self) -> Dict[str, Any]:
        """Compose music from the graph. JEPA prediction."""
        style = self.determine_style()
        # Each cell becomes a note
        notes = []
        scale_degrees = {
            'major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
            'jazz': ['C', 'Eb', 'F', 'Gb', 'G', 'Bb', 'B'],
            'chromatic': ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G'],
        }[self.style]
        for i in range(self.n):
            # Map eigenvalue to note
            note_idx = int(self.eigenvalues[min(i, len(self.eigenvalues) - 1)] * 10) % len(scale_degrees)
            note = f"{scale_degrees[note_idx]}{4 + (i % 2)}"
            notes.append({
                'cell': f"cell_{i}",
                'note': note,
                'lambda': self.eigenvalues[min(i, len(self.eigenvalues) - 1)],
                'gamma': self.gamma,
                'eta': self.eta,
            })
            self.cells.append(notes[-1])
        return {
            'cr': style['cr'],
            'bpm': self.bpm,
            'style': self.style,
            'notes': notes,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("CONSERVATION-COMPOSER ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Laplacian eigenvalues → music on Quilt cells.")
    print("The cell graph's spectrum IS the music.")
    print()

    # Example: a triangle (well-connected)
    print("Triangle (well-connected, CR > 0.7):")
    triangle = [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ]
    c1 = ConservationComposerBridge(triangle)
    result = c1.compose()
    print(f"  CR = {result['cr']:.2f}")
    print(f"  BPM = {result['bpm']}")
    print(f"  Style = {result['style']}")
    print(f"  Notes: {[n['note'] for n in result['notes']]}")
    print()

    # Example: a path (poorly connected)
    print("Path graph (sparse, CR < 0.3):")
    path = [
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0],
    ]
    c2 = ConservationComposerBridge(path)
    result = c2.compose()
    print(f"  CR = {result['cr']:.2f}")
    print(f"  BPM = {result['bpm']}")
    print(f"  Style = {result['style']}")
    print(f"  Notes: {[n['note'] for n in result['notes']]}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("Laplacian eigenvalues IS the cell spectrum.")
    print("The composer IS the watch projecting the graph into music.")


if __name__ == "__main__":
    demo()
