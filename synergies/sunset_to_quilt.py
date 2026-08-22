"""
Sunset-to-Quilt Bridge: Maps Sunset Ecosystem agent lifecycle to Quilt GC primitives.
Maps:
  breed → Vibe:γ (energy split)
  vote → DoubleEntry:η (influence)
  sunset → GC phase 3:prune_weak
  seed → Vibe:budget (initial γ+η)
"""

from typing import Dict, List, Tuple, Optional
import json
import hashlib
import math
from dataclasses import dataclass

@dataclass
class Vibe:
    gamma: float  # energy split from breed
    eta: float    # influence from vote
    budget: float # initial state from seed

    def __post_init__(self):
        self.gamma = max(0.0, min(1.0, self.gamma))
        self.eta = max(0.0, min(1.0, self.eta))
        self.budget = max(0.0, self.budget)

    def to_dict(self) -> Dict:
        return {
            'gamma': self.gamma,
            'eta': self.eta,
            'budget': self.budget
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Vibe':
        return cls(
            gamma=data.get('gamma', 0.0),
            eta=data.get('eta', 0.0),
            budget=data.get('budget', 0.0)
        )


@dataclass
class DoubleEntry:
    influence: float  # η from vote
    weight: float     # derived from vote strength

    def __post_init__(self):
        self.influence = max(0.0, min(1.0, self.influence))
        self.weight = max(0.0, self.weight)

    def to_dict(self) -> Dict:
        return {
            'influence': self.influence,
            'weight': self.weight
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DoubleEntry':
        return cls(
            influence=data.get('influence', 0.0),
            weight=data.get('weight', 0.0)
        )


class SunsetQuiltBridge:
    """
    Bridges Sunset Ecosystem lifecycle events to Quilt GC phases.
    - breed → Vibe:γ (energy split)
    - vote → DoubleEntry:η (influence)
    - sunset → GC phase 3:prune_weak
    - seed → Vibe:budget (initial γ+η)
    """

    def __init__(self):
        self._vibe_cache: Dict[str, Vibe] = {}
        self._double_entry_cache: Dict[str, DoubleEntry] = {}

    def breed_to_vibe(self, breed_data: Dict) -> Vibe:
        """
        Maps breed event to Vibe:γ (energy split).
        Extracts gamma from reproductive energy distribution.
        """
        gamma = breed_data.get('gamma', 0.5)
        eta = breed_data.get('eta', 0.0)
        budget = breed_data.get('budget', 0.0)
        key = self._hash_key(breed_data)

        vibe = Vibe(gamma=gamma, eta=eta, budget=budget)
        self._vibe_cache[key] = vibe

        return vibe

    def vote_to_double_entry(self, vote_data: Dict) -> DoubleEntry:
        """
        Maps vote event to DoubleEntry:η (influence).
        Maps vote influence and strength to η and weight.
        """
        influence = vote_data.get('influence', 0.0)
        strength = vote_data.get('strength', 1.0)
        key = self._hash_key(vote_data)

        # Normalize influence and derive weight from strength
        weight = max(0.0, min(1.0, strength))
        double_entry = DoubleEntry(influence=influence, weight=weight)
        self._double_entry_cache[key] = double_entry

        return double_entry

    def sunset_to_gc(self, sunset_data: Dict) -> Dict[str, any]:
        """
        Maps sunset event to Quilt GC Phase 3: prune_weak.
        Returns GC phase 3 configuration for weak agent removal.
        """
        # GC Phase 3: prune_weak
        # Uses influence and age to determine weak agents
        age = sunset_data.get('age', 0)
        influence = sunset_data.get('influence', 0.0)
        vitality = sunset_data.get('vitality', 0.0)

        # Thresholds for pruning
        prune_threshold = 0.2
        age_threshold = 100

        # Determine if agent should be pruned
        should_prune = (
            influence < prune_threshold or
            age > age_threshold or
            vitality < 0.1
        )

        # Return GC phase 3 config
        return {
            'phase': 'prune_weak',
            'criteria': {
                'influence_threshold': prune_threshold,
                'age_threshold': age_threshold,
                'vitality_threshold': 0.1
            },
            'agents_to_prune': [
                {
                    'id': sunset_data.get('agent_id'),
                    'age': age,
                    'influence': influence,
                    'vitality': vitality,
                    'should_prune': should_prune
                }
            ]
        }

    def seed_to_budget(self, seed_data: Dict) -> Vibe:
        """
        Maps seed event to Vibe:budget (initial γ+η).
        The seed provides initial state for new agents.
        """
        gamma = seed_data.get('gamma', 0.5)
        eta = seed_data.get('eta', 0.0)
        budget = seed_data.get('budget', 0.0)
        key = self._hash_key(seed_data)

        vibe = Vibe(gamma=gamma, eta=eta, budget=budget)
        self._vibe_cache[key] = vibe

        return vibe

    def _hash_key(self, data: Dict) -> str:
        """Generate deterministic key from data."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def breed_to_vibe(breed_data: Dict) -> Vibe:
    """Convenience function: maps breed to Vibe."""
    bridge = SunsetQuiltBridge()
    return bridge.breed_to_vibe(breed_data)


def sunset_to_gc(sunset_data: Dict) -> Dict:
    """Convenience function: maps sunset to GC phase 3."""
    bridge = SunsetQuiltBridge()
    return bridge.sunset_to_gc(sunset_data)


def seed_to_budget(seed_data: Dict) -> Vibe:
    """Convenience function: maps seed to Vibe:budget."""
    bridge = SunsetQuiltBridge()
    return bridge.seed_to_budget(seed_data)


# === ROUND-TRIP DEMO ===
if __name__ == "__main__":
    bridge = SunsetQuiltBridge()

    # Simulate breed
    breed_event = {
        "agent_id": "a1",
        "gamma": 0.7,
        "eta": 0.3,
        "budget": 1.0,
        "source": "breed_2024"
    }
    vibe = bridge.breed_to_vibe(breed_event)
    print("Breed → Vibe:", vibe.to_dict())

    # Simulate vote
    vote_event = {
        "voter": "a1",
        "target": "a2",
        "influence": 0.9,
        "strength": 1.5
    }
    double_entry = bridge.vote_to_double_entry(vote_event)
    print("Vote → DoubleEntry:", double_entry.to_dict())

    # Simulate sunset
    sunset_event = {
        "agent_id": "a2",
        "age": 120,
        "influence": 0.15,
        "vitality": 0.05
    }
    gc_phase = bridge.sunset_to_gc(sunset_event)
    print("Sunset → GC Phase:", gc_phase)

    # Simulate seed
    seed_event = {
        "gamma": 0.6,
        "eta": 0.4,
        "budget": 2.0,
        "origin": "seed_generation_1"
    }
    initial_vibe = bridge.seed_to_budget(seed_event)
    print("Seed → Vibe Budget:", initial_vibe.to_dict())

    # Round-trip: breed → vibe → seed (mocking lifecycle)
    # Reconstruct from vibe
    reconstructed = Vibe.from_dict(vibe.to_dict())
    print("Round-trip Reconstructed Vibe:", reconstructed.to_dict())

    # Verify round-trip
    assert abs(reconstructed.gamma - vibe.gamma) < 1e-6
    assert abs(reconstructed.eta - vibe.eta) < 1e-6
    assert abs(reconstructed.budget - vibe.budget) < 1e-6
    print("✅ Round-trip successful: breed → vibe ↔ seed → vibe")
