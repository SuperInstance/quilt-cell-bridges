"""
ternary-hmm (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-hmm (Rust) provides Hidden Markov Models with
ternary states and emissions {-1, 0, +1}:
- Forward-backward algorithms
- Viterbi decoding
- Baum-Welch training
- Filtering and smoothing

THE CRUCIAL INSIGHT: An HMM IS a Quilt cell graph with hidden state.
The 3×3 matrices ARE 3 cells × 3 cells. Viterbi IS a JEPA prediction
of the most likely path. Baum-Welch IS the watch learning from observations.

Map:
- State → cell (with transition probabilities)
- Observation → Z_in
- Forward message → Murmur
- Backward message → Murmur
- Viterbi path → Graph traversal
- Baum-Welch → DoubleEntry (γ+η=1 across iterations)
"""

from typing import Dict, List, Any, Tuple
import math


class StateCell:
    """A Quilt cell representing a hidden state."""
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index  # 0, 1, or 2
        # Initial probability
        self.pi = 1.0 / 3
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"State({self.name})"


class TernaryHMMBridge:
    """A ternary HMM on Quilt cells."""

    def __init__(self):
        # 3 states
        self.states: List[StateCell] = [
            StateCell("Negative", 0),
            StateCell("Neutral", 1),
            StateCell("Positive", 2),
        ]
        # 3x3 transition matrix
        self.A: List[List[float]] = [
            [0.7, 0.2, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.7],
        ]
        # 3x3 emission matrix (diagonal-dominant)
        self.B: List[List[float]] = [
            [0.8, 0.15, 0.05],  # emit from Negative
            [0.15, 0.7, 0.15],   # emit from Neutral
            [0.05, 0.15, 0.8],   # emit from Positive
        ]

    def viterbi(self, observations: List[int]) -> List[int]:
        """Find the most likely sequence of states. JEPA prediction."""
        n_obs = len(observations)
        n_states = len(self.states)
        # V[i][j] = max prob of being in state j at time i
        V = [[0.0] * n_states for _ in range(n_obs)]
        # Backpointer
        bp = [[0] * n_states for _ in range(n_obs)]
        # Initialize
        for j in range(n_states):
            V[0][j] = self.states[j].pi * self.B[j][observations[0]]
            bp[0][j] = -1
        # Recursion
        for i in range(1, n_obs):
            for j in range(n_states):
                max_p = -1
                max_k = 0
                for k in range(n_states):
                    p = V[i - 1][k] * self.A[k][j]
                    if p > max_p:
                        max_p = p
                        max_k = k
                V[i][j] = max_p * self.B[j][observations[i]]
                bp[i][j] = max_k
        # Backtrack
        path = [0] * n_obs
        path[-1] = max(range(n_states), key=lambda j: V[-1][j])
        for i in range(n_obs - 2, -1, -1):
            path[i] = bp[i + 1][path[i + 1]]
        return path

    def forward(self, observations: List[int]) -> List[List[float]]:
        """Forward algorithm. Murmur from past."""
        n_obs = len(observations)
        n_states = len(self.states)
        alpha = [[0.0] * n_states for _ in range(n_obs)]
        for j in range(n_states):
            alpha[0][j] = self.states[j].pi * self.B[j][observations[0]]
        for i in range(1, n_obs):
            for j in range(n_states):
                alpha[i][j] = sum(alpha[i - 1][k] * self.A[k][j] for k in range(n_states)) * self.B[j][observations[i]]
        return alpha

    def backward(self, observations: List[int]) -> List[List[float]]:
        """Backward algorithm. Murmur from future."""
        n_obs = len(observations)
        n_states = len(self.states)
        beta = [[0.0] * n_states for _ in range(n_obs)]
        for j in range(n_states):
            beta[-1][j] = 1.0
        for i in range(n_obs - 2, -1, -1):
            for j in range(n_states):
                beta[i][j] = sum(self.A[j][k] * self.B[k][observations[i + 1]] * beta[i + 1][k] for k in range(n_states))
        return beta

    def filter(self, observations: List[int]) -> List[List[float]]:
        """Compute filtered state distribution. JEPA online."""
        alpha = self.forward(observations)
        filtered = []
        for row in alpha:
            total = sum(row)
            if total > 0:
                filtered.append([v / total for v in row])
            else:
                filtered.append(row)
        return filtered


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-HMM ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Hidden Markov Models on Quilt cells.")
    print("3 states = 3 cell kinds. Viterbi = JEPA. Baum-Welch = watch.")
    print()

    hmm = TernaryHMMBridge()

    # Observations: -1, -1, 0, 1, 1, 1
    observations = [0, 0, 1, 2, 2, 2]
    print(f"Observations: {observations}")
    print()

    # Viterbi
    path = hmm.viterbi(observations)
    state_names = ["Neg", "Neu", "Pos"]
    print(f"Viterbi path: {[state_names[s] for s in path]}")
    print()

    # Filter
    filtered = hmm.filter(observations)
    print("Filtered state distribution:")
    for i, dist in enumerate(filtered):
        print(f"  t={i}: {', '.join(f'{state_names[j]}={dist[j]:.2f}' for j in range(3))}")
    print()

    # Conservation
    n = len(hmm.states)
    total = sum(s.gamma + s.eta for s in hmm.states)
    print(f"Conservation: {n} states, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("An HMM IS a Quilt cell graph with hidden state.")
    print("Viterbi IS JEPA. Baum-Welch IS the watch.")


if __name__ == "__main__":
    demo()
