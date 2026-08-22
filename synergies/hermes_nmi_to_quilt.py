"""
hermes-nmi (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance hermes-nmi (Rust) is the Neuro-Muscular Interface.
It sits between:
- CNS (where Hermes reasons) - intent downward
- Claw (where cellular agents act) - action downward
- Pincher (reflex engine) - sub-50ms responses

It translates ReasoningPulses into CommandChains, returns TelemetryFrames,
and routes reflex matches.

THE CRUCIAL INSIGHT: The NMI IS the Quilt watch! The watch sits between
the cell graph (CNS) and the action (Claw). It translates Vibe into Z_out
and reads back Z_in. The Pincher IS the GC phase (sub-50ms decay).

Map:
- CNS → cell graph (reasoning)
- Claw → cells (action)
- Pincher → GC (reflex)
- ReasoningPulse → Vibe (state of intent)
- CommandChain → Z_out (write actions)
- TelemetryFrame → Z_in (read results)
- NmiDispatcher → watch (translation)
- Reflex match → GC.urgent (immediate decay)
"""

import math
from typing import Dict, List, Any, Optional, Callable


class Cell:
    """A Quilt cell with a state."""
    def __init__(self, name: str):
        self.name = name
        self.gamma = 0.5
        self.eta = 0.5
        self.value: Any = None
        self.is_urgent: bool = False  # For reflex (Pincher)


class ReasoningPulse:
    """A Vibe state representing intent."""
    def __init__(self, intent: str, energy: float, context: Dict[str, Any]):
        self.intent = intent
        self.energy = energy
        self.context = context


class CommandChain:
    """A sequence of Z_out actions."""
    def __init__(self, commands: List[Dict[str, Any]]):
        self.commands = commands


class TelemetryFrame:
    """A Z_in reading."""
    def __init__(self, sensor_data: Dict[str, Any], status: str, tension: float = 0.0):
        self.sensor_data = sensor_data
        self.status = status
        self.tension = tension


class HermesNMIBridge:
    """The NMI as a Quilt watch (translation between reasoning and action)."""

    def __init__(self):
        # Cells (the cell graph = CNS)
        self.cells: Dict[str, Cell] = {}
        # Action targets (Claw)
        self.action_targets: Dict[str, Cell] = {}
        # Reflexes (Pincher)
        self.reflexes: List[Callable] = []
        # Telemetry
        self.telemetry_history: List[TelemetryFrame] = []

    def add_cell(self, name: str) -> Cell:
        cell = Cell(name)
        self.cells[name] = cell
        return cell

    def add_action_target(self, name: str) -> Cell:
        cell = Cell(name)
        self.action_targets[name] = cell
        return cell

    def add_reflex(self, predicate: Callable) -> None:
        """Add a reflex. A GC.urgent function."""
        self.reflexes.append(predicate)

    def dispatch(self, pulse: ReasoningPulse) -> CommandChain:
        """Translate a reasoning pulse into a command chain. The watch."""
        commands = []
        # Decompose intent into discrete actions
        if pulse.energy < 0.2:
            # Low energy: single action
            commands.append({'action': 'observe', 'target': pulse.intent})
        elif pulse.energy < 0.6:
            # Medium energy: 2 actions
            commands.append({'action': 'analyze', 'target': pulse.intent})
            commands.append({'action': 'respond', 'target': pulse.intent})
        else:
            # High energy: full action sequence
            commands.append({'action': 'analyze', 'target': pulse.intent})
            commands.append({'action': 'plan', 'target': pulse.intent})
            commands.append({'action': 'execute', 'target': pulse.intent})
        return CommandChain(commands)

    def execute(self, chain: CommandChain) -> TelemetryFrame:
        """Execute a command chain. Z_out + Z_in."""
        sensor_data = {}
        status = 'ok'
        for cmd in chain.commands:
            target = cmd.get('target', '')
            action = cmd.get('action', '')
            # Mark target as urgent if it's a reflex
            if target in self.action_targets:
                self.action_targets[target].is_urgent = (action == 'execute')
            # Simulate reading back
            sensor_data[target] = f"result_of_{action}"
        return TelemetryFrame(sensor_data=sensor_data, status=status, tension=0.1)

    def check_reflexes(self, frame: TelemetryFrame) -> bool:
        """Check if any reflex matches. GC.urgent."""
        for reflex in self.reflexes:
            if reflex(frame):
                return True
        return False

    def tick(self, pulse: ReasoningPulse) -> TelemetryFrame:
        """Run a full NMI cycle: pulse → chain → execute → telemetry."""
        chain = self.dispatch(pulse)
        frame = self.execute(chain)
        self.telemetry_history.append(frame)
        return frame


if __name__ == "__main__":
    print("=" * 60)
    print("HERMES-NMI ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Neuro-Muscular Interface as the Quilt watch.")
    print("ReasoningPulse → Vibe. CommandChain → Z_out. Telemetry → Z_in.")
    print()

    nmi = HermesNMIBridge()

    # Add cells (CNS)
    for name in ['perception', 'reasoning', 'planning']:
        nmi.add_cell(name)

    # Add action targets (Claw)
    for name in ['gripper', 'arm', 'wheel']:
        nmi.add_action_target(name)

    # Add a reflex (Pincher)
    nmi.add_reflex(lambda f: 'gripper' in f.sensor_data and 'hot' in str(f.sensor_data))

    # Run a cycle
    pulse = ReasoningPulse(intent='grasp_object', energy=0.7, context={'object': 'cube'})
    frame = nmi.tick(pulse)
    print(f"Pulse: intent={pulse.intent}, energy={pulse.energy}")
    print(f"Status: {frame.status}")
    print(f"Sensor data: {frame.sensor_data}")
    print(f"Tension: {frame.tension}")
    print()

    # Reflex check
    reflex = nmi.check_reflexes(frame)
    print(f"Reflex triggered: {reflex}")
    print()

    # Conservation
    n = len(nmi.cells) + len(nmi.action_targets)
    total = sum(c.gamma + c.eta for c in nmi.cells.values()) + \
            sum(c.gamma + c.eta for c in nmi.action_targets.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("The NMI IS the Quilt watch.")
    print("Pincher IS GC. Claw IS cells. CNS IS the cell graph.")


if __name__ == "__main__":
    demo()
