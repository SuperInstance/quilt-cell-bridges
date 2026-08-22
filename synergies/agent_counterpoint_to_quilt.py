"""
agent-counterpoint (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance agent-counterpoint (Rust) applies species counterpoint
(Fux, 1725) to multi-agent coordination:
1. Prefer contrary motion — different angles
2. Avoid parallel fifths and octaves — redundancy
3. Resolve dissonance quickly — conflict management

THE CRUCIAL INSIGHT: Counterpoint IS fleet coordination. Each voice IS an
agent. The 5 species of counterpoint ARE 5 cell kinds. Parallel fifths ARE
a JEPA error (two agents predicting the same output). The cadence IS GC.

Map:
- Voice → agent (cell)
- Note → cell value
- Voice leading → Murmur (inter-agent)
- Contrary motion → DoubleEntry (γ+η=1 across voices)
- Parallel fifths → JEPA error
- Dissonance → Vibe (state of conflict)
- Cadence → GC
"""

from typing import Dict, List, Any, Tuple


class Voice:
    """A Quilt cell representing a voice/agent."""
    def __init__(self, name: str, initial_pitch: int = 60):
        self.name = name
        self.pitch = initial_pitch
        self.history: List[int] = [initial_pitch]
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"Voice({self.name}={self.pitch})"

    def move(self, new_pitch: int) -> None:
        """Move to a new pitch."""
        self.pitch = new_pitch
        self.history.append(new_pitch)


class AgentCounterpointBridge:
    """Counterpoint rules applied to Quilt cells (agents)."""

    def __init__(self):
        self.voices: Dict[str, Voice] = {}

    def add_voice(self, name: str, initial_pitch: int = 60) -> Voice:
        """Add a voice. An agent cell."""
        voice = Voice(name, initial_pitch)
        self.voices[name] = voice
        return voice

    def is_parallel_fifth(self, voice_a: Voice, voice_b: Voice, prev_a: int, prev_b: int) -> bool:
        """Check for parallel fifths between two voices."""
        # Fifth = 7 semitones
        interval_curr = (voice_a.pitch - voice_b.pitch) % 12
        interval_prev = (prev_a - prev_b) % 12
        return interval_curr == 7 and interval_prev == 7

    def is_parallel_octave(self, voice_a: Voice, voice_b: Voice, prev_a: int, prev_b: int) -> bool:
        """Check for parallel octaves."""
        interval_curr = (voice_a.pitch - voice_b.pitch) % 12
        interval_prev = (prev_a - prev_b) % 12
        return interval_curr == 0 and interval_prev == 0

    def is_contrary_motion(self, voice_a: Voice, voice_b: Voice, prev_a: int, prev_b: int) -> bool:
        """Check for contrary motion (one up, one down)."""
        a_up = voice_a.pitch > prev_a
        a_down = voice_a.pitch < prev_a
        b_up = voice_b.pitch > prev_b
        b_down = voice_b.pitch < prev_b
        return (a_up and b_down) or (a_down and b_up)

    def check_voice_pair(self, name_a: str, name_b: str) -> Dict[str, bool]:
        """Check counterpoint rules between two voices."""
        if name_a not in self.voices or name_b not in self.voices:
            return {}
        a = self.voices[name_a]
        b = self.voices[name_b]
        if len(a.history) < 2 or len(b.history) < 2:
            return {}
        prev_a = a.history[-2]
        prev_b = b.history[-2]
        return {
            'parallel_fifth': self.is_parallel_fifth(a, b, prev_a, prev_b),
            'parallel_octave': self.is_parallel_octave(a, b, prev_a, prev_b),
            'contrary_motion': self.is_contrary_motion(a, b, prev_a, prev_b),
        }

    def coordinate(self, motions: Dict[str, int]) -> List[Dict[str, bool]]:
        """Apply motions and check all voice pairs."""
        # Save history before motion
        for name, motion in motions.items():
            if name in self.voices:
                new_pitch = self.voices[name].pitch + motion
                self.voices[name].move(new_pitch)
        # Check all pairs
        results = []
        names = list(self.voices.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                check = self.check_voice_pair(names[i], names[j])
                if check:
                    check['pair'] = (names[i], names[j])
                    results.append(check)
        return results

    def has_redundant_agents(self) -> bool:
        """Detect redundant agents (parallel fifths/octaves)."""
        names = list(self.voices.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                check = self.check_voice_pair(names[i], names[j])
                if check.get('parallel_fifth') or check.get('parallel_octave'):
                    return True
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("AGENT-COUNTERPOINT ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Species counterpoint as multi-agent coordination.")
    print("Parallel fifths = redundant agents. Contrary motion = differentiation.")
    print()

    ac = AgentCounterpointBridge()

    # 4 voices: soprano, alto, tenor, bass
    ac.add_voice("soprano", 72)
    ac.add_voice("alto", 67)
    ac.add_voice("tenor", 64)
    ac.add_voice("bass", 55)

    print("Initial voices:")
    for v in ac.voices.values():
        print(f"  {v}")
    print()

    # Move in contrary motion (good!)
    print("Move 1 (contrary motion):")
    motions = {"soprano": +2, "alto": -2, "tenor": +1, "bass": -1}
    results = ac.coordinate(motions)
    for v in ac.voices.values():
        print(f"  {v}")
    for r in results:
        print(f"  Pair {r['pair']}: contrary={r['contrary_motion']}, p5={r['parallel_fifth']}, p8={r['parallel_octave']}")
    print()

    # Move in parallel (redundant)
    print("Move 2 (parallel motion - bad):")
    motions = {"soprano": +2, "alto": +2, "tenor": +2, "bass": +2}
    results = ac.coordinate(motions)
    for v in ac.voices.values():
        print(f"  {v}")
    print(f"  Redundant agents detected: {ac.has_redundant_agents()}")
    print()

    # Conservation
    n = len(ac.voices)
    total = sum(v.gamma + v.eta for v in ac.voices.values())
    print(f"Conservation: {n} voices, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("Counterpoint IS fleet coordination.")
    print("Parallel fifths ARE redundant agents.")
    print("Contrary motion IS productive differentiation.")


if __name__ == "__main__":
    demo()
