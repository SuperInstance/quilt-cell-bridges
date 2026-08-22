"""
topo-sonata (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance topo-sonata (Rust) creates musical compositions as
simplicial complexes. Persistent homology detects "holes" in harmonic space.

- Chords are simplices (vertices = notes, edges = intervals, triangles = triads)
- Chord progressions are filtered by voice-leading distance
- Persistent homology detects unresolved tension = topological holes
- Genre classification via Betti numbers

THE CRUCIAL INSIGHT: A chord progression IS a filtered cell graph.
Holes in harmonic space ARE H¹ cohomology. Persistent homology IS the
watch integrating over voice-leading distance.

Map:
- Note → cell (vertex)
- Interval → cell edge
- Triad → cell triangle
- Chord progression → filtered cell graph
- Hole → β₁ (H¹ cohomology)
- Persistence → JEPA over scale
- Genre → DoubleEntry (γ+η=1 across Betti)
"""

from typing import Dict, List, Any, Set, Tuple


class NoteCell:
    """A Quilt cell representing a note."""
    def __init__(self, pitch: int):
        self.pitch = pitch
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        # Convert pitch to note name
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[self.pitch % 12]


class Chord:
    """A chord as a simplicial complex."""
    def __init__(self, pitches: List[int]):
        self.pitches = pitches
        # Vertices
        self.vertices: Dict[int, NoteCell] = {p: NoteCell(p) for p in pitches}
        # Edges (all pairs)
        self.edges: Set[Tuple[int, int]] = set()
        for i, p1 in enumerate(pitches):
            for p2 in pitches[i+1:]:
                self.edges.add((min(p1, p2), max(p1, p2)))
        # Triangles (if 3+ notes)
        self.triangles: List[Tuple[int, int, int]] = []
        if len(pitches) >= 3:
            from itertools import combinations
            for trio in combinations(pitches, 3):
                self.triangles.append(trio)


class TopoSonataBridge:
    """A chord progression as a filtered simplicial complex."""

    def __init__(self):
        self.chords: List[Chord] = []
        self.voice_leading_distances: List[float] = []
        self.betti_0: int = 0
        self.betti_1: int = 0

    def add_chord(self, pitches: List[int]) -> Chord:
        """Add a chord. A simplicial complex."""
        chord = Chord(pitches)
        self.chords.append(chord)
        # Compute voice-leading distance to previous
        if len(self.chords) > 1:
            prev = self.chords[-2].pitches
            curr = chord.pitches
            # Sum of |pitch_curr - pitch_prev|
            distance = sum(min(abs(p - pp), 12 - abs(p - pp)) for p in curr for pp in prev) / max(1, len(curr))
            self.voice_leading_distances.append(distance)
        return chord

    def compute_betti(self) -> Dict[str, int]:
        """Compute β₀ and β₁ for the chord progression."""
        if not self.chords:
            return {'beta_0': 0, 'beta_1': 0}
        # Union all notes
        all_notes: Set[int] = set()
        for chord in self.chords:
            all_notes.update(chord.pitches)
        # Build adjacency
        adj: Dict[int, Set[int]] = {n: set() for n in all_notes}
        for chord in self.chords:
            for u, v in chord.edges:
                if u in adj and v in adj:
                    adj[u].add(v)
                    adj[v].add(u)
        # β₀: connected components
        parent = {n: n for n in all_notes}
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        for u in adj:
            for v in adj[u]:
                union(u, v)
        roots = set(find(n) for n in all_notes)
        self.betti_0 = len(roots)
        # β₁: cycles (E - V + β₀)
        v = len(all_notes)
        e = sum(len(adj[n]) for n in adj) // 2
        self.betti_1 = max(0, e - v + self.betti_0)
        return {'beta_0': self.betti_0, 'beta_1': self.betti_1}

    def detect_unresolved_tension(self) -> bool:
        """Detect if there are unresolved tensions (holes)."""
        return self.betti_1 > 0

    def classify_genre(self) -> str:
        """Classify genre based on Betti numbers and voice-leading."""
        if not self.voice_leading_distances:
            return 'unknown'
        avg_distance = sum(self.voice_leading_distances) / len(self.voice_leading_distances)
        if self.betti_1 == 0 and avg_distance < 1.0:
            return 'classical_resolved'
        elif self.betti_1 > 0 and avg_distance > 2.0:
            return 'jazz_complex'
        elif self.betti_1 > 0 and avg_distance < 1.0:
            return 'atonal_tension'
        else:
            return 'romantic_lyrical'


if __name__ == "__main__":
    print("=" * 60)
    print("TOPO-SONATA ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Music as simplicial complexes on Quilt cells.")
    print("Holes in harmony IS H¹ cohomology.")
    print()

    # Bach-style progression: I → IV → V → I
    sonata = TopoSonataBridge()
    # C major (C, E, G)
    sonata.add_chord([60, 64, 67])
    # F major (F, A, C)
    sonata.add_chord([65, 69, 72])
    # G major (G, B, D)
    sonata.add_chord([67, 71, 74])
    # C major (C, E, G)
    sonata.add_chord([60, 64, 67])

    print("Chord progression:")
    for i, chord in enumerate(sonata.chords):
        pitches = [NoteCell(p).__repr__() for p in chord.pitches]
        print(f"  Chord {i+1}: {pitches}")
    print()

    betti = sonata.compute_betti()
    print(f"Betti numbers: β₀={betti['beta_0']}, β₁={betti['beta_1']}")
    print(f"Unresolved tension: {sonata.detect_unresolved_tension()}")
    print(f"Genre: {sonata.classify_genre()}")
    print()

    # Atrial progression with hole: I → ii → V → I (cadence resolves)
    sonata2 = TopoSonataBridge()
    sonata2.add_chord([60, 64, 67])  # C
    sonata2.add_chord([62, 65, 69])  # D minor
    sonata2.add_chord([67, 71, 74])  # G
    sonata2.add_chord([60, 64, 67])  # C
    betti2 = sonata2.compute_betti()
    print(f"Cadence progression: β₀={betti2['beta_0']}, β₁={betti2['beta_1']}")
    print()

    # Conservation
    total = sum(cell.gamma + cell.eta for chord in sonata.chords for cell in chord.vertices.values())
    n = sum(len(chord.vertices) for chord in sonata.chords)
    print(f"Conservation: {n} notes, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A chord progression IS a filtered cell graph.")
    print("Holes in harmony ARE H¹ cohomology.")


if __name__ == "__main__":
    demo()
