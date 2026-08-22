"""
ternary-register-file (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance ternary-register-file (Rust) is a register allocator
for ternary GPU kernels. It tracks physical register usage, builds
interference graphs, and computes spill costs.

Map:
- Physical register → Vibe (state)
- Virtual register → Z_in (input)
- Allocate → Z_out (output)
- Free → GC
- Live range → DoubleEntry
- Interference graph → Graph
- Spill → Vibe.decel (deceleration)
- Pressure → sum of live cells
"""

from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class Register:
    """A Quilt Vibe representing a physical register."""
    name: str
    value: int = 0  # 20 trits fit in a 32-bit register
    is_allocated: bool = False
    spill_cost: float = 0.0
    gamma: float = 0.5
    eta: float = 0.5

    def __post_init__(self):
        assert abs(self.gamma + self.eta - 1.0) < 1e-9


class RegisterFileBridge:
    """A register file implemented on Quilt cells."""

    def __init__(self, num_registers: int = 32):
        # Each register is a Vibe primitive
        self.registers: Dict[str, Register] = {
            f"r{i}": Register(name=f"r{i}")
            for i in range(num_registers)
        }
        # Virtual registers (Z_in)
        self.virtual_registers: Dict[str, Register] = {}
        # Interference graph
        self.interference: Dict[str, Set[str]] = {r: set() for r in self.registers}
        # Allocations
        self.allocation: Dict[str, str] = {}  # vreg -> preg
        # Spilled
        self.spilled: Set[str] = set()

    def add_virtual_register(self, name: str) -> Register:
        """Add a virtual register. Z_in."""
        vreg = Register(name=f"v_{name}")
        self.virtual_registers[f"v_{name}"] = vreg
        return vreg

    def add_interference(self, vreg1: str, vreg2: str) -> None:
        """Add an interference edge. Graph primitive."""
        if vreg1 in self.interference:
            self.interference[vreg1].add(vreg2)
        if vreg2 in self.interference:
            self.interference[vreg2].add(vreg1)

    def allocate(self, vreg: str) -> bool:
        """Allocate a physical register for a virtual register. Z_out."""
        # Find a free register
        for preg_name, preg in self.registers.items():
            if not preg.is_allocated and preg_name not in [self.allocation.get(v) for v in self.virtual_registers if v in self.allocation]:
                preg.is_allocated = True
                self.allocation[vreg] = preg_name
                return True
        # Need to spill
        self.spilled.add(vreg)
        return False

    def free(self, vreg: str) -> None:
        """Free a physical register. GC primitive."""
        if vreg in self.allocation:
            preg = self.allocation[vreg]
            self.registers[preg].is_allocated = False
            del self.allocation[vreg]

    def pressure(self) -> int:
        """Count of live registers. Sum of Vibe cells."""
        return sum(1 for r in self.registers.values() if r.is_allocated)

    def spill_cost(self, vreg: str) -> float:
        """Spill cost. Vibe deceleration."""
        if vreg not in self.virtual_registers:
            return 0.0
        return self.virtual_registers[vreg].spill_cost


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("TERNARY-REGISTER-FILE ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Register allocator for ternary GPU kernels via Quilt cells.")
    print("Physical register = Vibe. Virtual register = Z_in. Allocate = Z_out.")
    print()

    rf = RegisterFileBridge(num_registers=8)

    # Add virtual registers
    for i in range(10):
        rf.add_virtual_register(f"a{i}")

    # Add interferences
    rf.add_interference("v_a0", "v_a1")
    rf.add_interference("v_a1", "v_a2")
    rf.add_interference("v_a0", "v_a3")

    # Allocate
    for v in ["v_a0", "v_a1", "v_a2", "v_a3"]:
        if rf.allocate(v):
            print(f"  Allocated {v} → {rf.allocation[v]}")
        else:
            print(f"  Spilled {v}")

    # Pressure
    print(f"  Pressure: {rf.pressure()} / 8")
    print()

    # Conservation
    n = len(rf.registers)
    total_g = sum(r.gamma for r in rf.registers.values())
    total_e = sum(r.eta for r in rf.registers.values())
    print(f"Conservation: {n} registers, γ+η={total_g + total_e:.2f}")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A register file IS a Vibe substrate.")
    print("Spill is Vibe.decel. Pressure is the sum of live Vibe.")


if __name__ == "__main__":
    demo()
