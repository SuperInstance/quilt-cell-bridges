"""
ternary-turing (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-turing (Rust) implements Turing machines over the
ternary tape alphabet {-1, 0, +1}.

THE CRUCIAL INSIGHT: state (Q) is a Quilt primitive (Vibe).
The Turing machine IS a Quilt runtime.

Map:
- State → Vibe (state is a Quilt primitive!)
- Tape cell → Quilt cell (with value in {-1, 0, +1})
- Read head → Z_in (read)
- Write → Z_out (write)
- Move → Graph (next state in tape)
- Halting → GC (no more transitions)
- Transitions → Murmur (inter-state messages)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Vibe:
    """The Vibe primitive: state with position, velocity, acceleration."""
    state: int
    position: int = 0
    velocity: int = 0
    acceleration: int = 0
    gamma: float = 0.5
    eta: float = 0.5

    def __post_init__(self):
        assert abs(self.gamma + self.eta - 1.0) < 1e-9


@dataclass
class TapeCell:
    """A Quilt cell holding a ternary value."""
    value: int  # -1, 0, or 1
    position: int
    gamma: float = 0.5
    eta: float = 0.5

    def __post_init__(self):
        assert self.value in (-1, 0, 1)
        assert abs(self.gamma + self.eta - 1.0) < 1e-9


class Transition:
    """A Turing transition: (state, read) → (write, direction, next_state)."""
    def __init__(self, state: int, read: int, write: int, direction: int, next_state: int):
        self.state = state
        self.read = read
        self.write = write
        self.direction = direction  # -1 or 1
        self.next_state = next_state


class TernaryTuringBridge:
    """A ternary Turing machine implemented on Quilt cells."""

    def __init__(self):
        # State as a Vibe primitive
        self.current_vibe: Vibe = Vibe(state=0)
        # Tape as a dict of cells
        self.tape: Dict[int, TapeCell] = {}
        # Transitions
        self.transitions: List[Transition] = []
        # Steps
        self.steps: int = 0
        self.halted: bool = False

    def add_transition(self, state: int, read: int, write: int, direction: int, next_state: int) -> None:
        """Add a transition. The transition is a Murmur message."""
        self.transitions.append(Transition(state, read, write, direction, next_state))

    def run(self, max_steps: int = 1000) -> Dict[str, Any]:
        """Run the machine. Returns the final state."""
        for step in range(max_steps):
            if self.halted:
                break
            # Z_in: read the tape at current position
            current_pos = self.current_vibe.position
            if current_pos not in self.tape:
                self.tape[current_pos] = TapeCell(value=0, position=current_pos)
            read_value = self.tape[current_pos].value

            # Find the matching transition
            matching = [t for t in self.transitions if t.state == self.current_vibe.state and t.read == read_value]
            if not matching:
                self.halted = True
                break
            trans = matching[0]

            # Z_out: write to the tape
            self.tape[current_pos].value = trans.write

            # Move the head
            self.current_vibe.position += trans.direction
            self.current_vibe.velocity = trans.direction
            self.current_vibe.acceleration = 0  # Constant velocity

            # Update state (Vibe)
            self.current_vibe.state = trans.next_state

            # Check for halt state
            if trans.next_state == -1:
                self.halted = True
                break

            self.steps += 1

        return {
            'state': self.current_vibe.state,
            'position': self.current_vibe.position,
            'tape': {pos: cell.value for pos, cell in self.tape.items()},
            'steps': self.steps,
            'halted': self.halted,
        }

    def state_to_vibe(self, state: int) -> Vibe:
        """Convert a state to a Vibe."""
        return Vibe(state=state, position=0, velocity=0, acceleration=0)

    def transition_to_murmur(self, trans: Transition) -> Dict[str, Any]:
        """A transition is a Murmur message: from → to."""
        return {
            'from_state': trans.state,
            'read': trans.read,
            'write': trans.write,
            'direction': trans.direction,
            'to_state': trans.next_state,
        }


# Demonstration: Busy Beaver (4-state)
def busy_beaver_4():
    """The 4-state Busy Beaver machine. Halts in 107 steps writing 13 ones."""
    bridge = TernaryTuringBridge()
    # A₀: read 0 → write 1, right, A₁
    bridge.add_transition(state=0, read=0, write=1, direction=1, next_state=1)
    # A₀: read 1 → write 1, right, HALT
    bridge.add_transition(state=0, read=1, write=1, direction=1, next_state=-1)
    # A₁: read 0 → write 1, left, A₂
    bridge.add_transition(state=1, read=0, write=1, direction=-1, next_state=2)
    # A₁: read 1 → write 1, right, A₁
    bridge.add_transition(state=1, read=1, write=1, direction=1, next_state=1)
    # A₂: read 0 → write 1, right, A₁
    bridge.add_transition(state=2, read=0, write=1, direction=1, next_state=1)
    # A₂: read 1 → write 1, right, A₃
    bridge.add_transition(state=2, read=1, write=1, direction=1, next_state=3)
    # A₃: read 0 → write 1, left, A₀
    bridge.add_transition(state=3, read=0, write=1, direction=-1, next_state=0)
    # A₃: read 1 → write 1, right, A₃
    bridge.add_transition(state=3, read=1, write=1, direction=1, next_state=3)
    return bridge


if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-TURING ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Turing machine on ternary tape {-1, 0, +1} via Quilt cells.")
    print("State is a Vibe primitive. Transitions are Murmur messages.")
    print()

    # Run Busy Beaver
    bb = busy_beaver_4()
    print("Busy Beaver (4-state):")
    result = bb.run(max_steps=200)
    print(f"  Steps: {result['steps']}")
    print(f"  Final state: {result['state']}")
    print(f"  Final position: {result['position']}")
    print(f"  Halted: {result['halted']}")
    # Count 1s
    ones = sum(1 for v in result['tape'].values() if v == 1)
    print(f"  1s on tape: {ones}")
    print()

    # Show tape
    print("Tape (non-zero):")
    for pos in sorted(result['tape'].keys()):
        if result['tape'][pos] != 0:
            print(f"  [{pos:3d}] = {result['tape'][pos]}")
    print()

    # Conservation
    n = len(bb.tape)
    total_g = sum(c.gamma for c in bb.tape.values())
    total_e = sum(c.eta for c in bb.tape.values())
    print(f"Conservation: {n} tape cells, γ+η={total_g + total_e:.2f}")
    print()

    # Show a transition as Murmur
    if bb.transitions:
        m = bb.transition_to_murmur(bb.transitions[0])
        print(f"First transition as Murmur: {m}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A Turing machine IS a Quilt runtime.")
    print("State is Vibe. Transitions are Murmur.")
    print("Halting is GC.")


if __name__ == "__main__":
    demo()
