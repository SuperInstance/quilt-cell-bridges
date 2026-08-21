"""
CRDT to Quilt Bridge
Maps CRDT families to Quilt cells with full primitive support.
Supports: G-Counter, PN-Counter, G-Set, 2P-Set, OR-Set, LWW-Register, MV-Register
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class CRDTToQuiltBridge:
    """
    Bridge that maps CRDT types to Quilt cells with full primitive support.
    Each CRDT becomes a Quilt cell with the 8 primitives.
    DoubleEntry invariant maps to CRDT merge function.
    Vibe maps to CRDT state size.
    Murmur maps to CRDT gossip protocol.
    """

    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self._counter = 0
        self._clock = time.time()

    def register(self, crdt_type: str, crdt: Any) -> str:
        """Register a CRDT instance with the bridge."""
        key = f"crdt_{self._counter}"
        self._registry[key] = {
            "type": crdt_type,
            "crdt": crdt,
            "timestamp": self._clock,
            "state_size": self._get_state_size(crdt),
            "gossip": self._get_gossip_protocol(crdt_type)
        }
        self._counter += 1
        return key

    def _get_state_size(self, crdt: Any) -> int:
        """Estimate state size of CRDT for Vibe mapping."""
        if isinstance(crdt, GCounter):
            return len(crdt.counters)
        elif isinstance(crdt, PNCounter):
            return len(crdt.positive) + len(crdt.negative)
        elif isinstance(crdt, GSet):
            return len(crdt.elements)
        elif isinstance(crdt, TwoPhaseSet):
            return len(crdt.add_set) + len(crdt.remove_set)
        elif isinstance(crdt, ORSet):
            return sum(len(v) for v in crdt.elements.values())
        elif isinstance(crdt, LWWRegister):
            return len(crdt.value) if crdt.value else 0
        elif isinstance(crdt, MVRegister):
            return len(crdt.values)
        return 0

    def _get_gossip_protocol(self, crdt_type: str) -> str:
        """Map CRDT type to a gossip protocol for Murmur."""
        protocols = {
            "G-Counter": "push-pull",
            "PN-Counter": "pull",
            "G-Set": "push",
            "2P-Set": "push-pull",
            "OR-Set": "push-pull",
            "LWW-Register": "push",
            "MV-Register": "pull"
        }
        return protocols.get(crdt_type, "none")

    def get_cell(self, key: str) -> Dict[str, Any]:
        """Retrieve a Quilt cell representation of a CRDT."""
        if key not in self._registry:
            raise KeyError(f"CRDT with key {key} not found")

        r = self._registry[key]
        return {
            "id": key,
            "type": r["type"],
            "state": self._get_state(r["crdt"]),
            "size": r["state_size"],
            "gossip": r["gossip"],
            "timestamp": r["timestamp"],
            "primitives": self._get_primitives(r["crdt"]),
            "invariant": self._get_invariant(r["crdt"]),
            "vibe": self._get_vibe(r["crdt"]),
            "murmur": self._get_murmur(r["crdt"])
        }

    def _get_state(self, crdt: Any) -> Any:
        """Get serialized state of CRDT."""
        if isinstance(crdt, GCounter):
            return {k: v for k, v in crdt.counters.items()}
        elif isinstance(crdt, PNCounter):
            return {
                "positive": {k: v for k, v in crdt.positive.items()},
                "negative": {k: v for k, v in crdt.negative.items()}
            }
        elif isinstance(crdt, GSet):
            return list(crdt.elements)
        elif isinstance(crdt, TwoPhaseSet):
            return {
                "add_set": list(crdt.add_set),
                "remove_set": list(crdt.remove_set)
            }
        elif isinstance(crdt, ORSet):
            return {k: list(v) for k, v in crdt.elements.items()}
        elif isinstance(crdt, LWWRegister):
            return crdt.value
        elif isinstance(crdt, MVRegister):
            return list(crdt.values)
        return None

    def _get_primitives(self, crdt: Any) -> List[str]:
        """Return the 8 standard Quilt primitives."""
        return [
            "create",
            "update",
            "merge",
            "read",
            "delete",
            "conflict",
            "sync",
            "validate"
        ]

    def _get_invariant(self, crdt: Any) -> str:
        """DoubleEntry invariant maps to merge function."""
        if isinstance(crdt, GCounter):
            return "sum_all_counters"
        elif isinstance(crdt, PNCounter):
            return "positive_minus_negative"
        elif isinstance(crdt, GSet):
            return "union_adds"
        elif isinstance(crdt, TwoPhaseSet):
            return "add_before_remove"
        elif isinstance(crdt, ORSet):
            return "add_and_remove_sets"
        elif isinstance(crdt, LWWRegister):
            return "latest_writes_win"
        elif isinstance(crdt, MVRegister):
            return "all_values_present"
        return "none"

    def _get_vibe(self, crdt: Any) -> float:
        """Vibe maps to state size."""
        return float(self._get_state_size(crdt))

    def _get_murmur(self, crdt: Any) -> str:
        """Murmur maps to gossip protocol."""
        return self._get_gossip_protocol(type(crdt).__name__)

    def merge(self, key1: str, key2: str) -> str:
        """Merge two CRDTs and return new key."""
        if key1 not in self._registry or key2 not in self._registry:
            raise KeyError("One or both keys not found")

        crdt1 = self._registry[key1]["crdt"]
        crdt2 = self._registry[key2]["crdt"]
        merged = self._merge_crds(crdt1, crdt2)
        return self.register(type(merged).__name__, merged)

    def _merge_crds(self, crdt1: Any, crdt2: Any) -> Any:
        """Merge two CRDTs of the same type."""
        if type(crdt1) != type(crdt2):
            raise TypeError("Cannot merge different CRDT types")

        if isinstance(crdt1, GCounter):
            return self._merge_gcounter(crdt1, crdt2)
        elif isinstance(crdt1, PNCounter):
            return self._merge_pncounter(crdt1, crdt2)
        elif isinstance(crdt1, GSet):
            return self._merge_gset(crdt1, crdt2)
        elif isinstance(crdt1, TwoPhaseSet):
            return self._merge_twophase_set(crdt1, crdt2)
        elif isinstance(crdt1, ORSet):
            return self._merge_orset(crdt1, crdt2)
        elif isinstance(crdt1, LWWRegister):
            return self._merge_lww_register(crdt1, crdt2)
        elif isinstance(crdt1, MVRegister):
            return self._merge_mv_register(crdt1, crdt2)
        raise ValueError("Unsupported CRDT type")

    def _merge_gcounter(self, c1: 'GCounter', c2: 'GCounter') -> 'GCounter':
        """Merge two G-Counters."""
        result = GCounter()
        for node, count in c1.counters.items():
            result.increment(node, count)
        for node, count in c2.counters.items():
            result.increment(node, count)
        return result

    def _merge_pncounter(self, c1: 'PNCounter', c2: 'PNCounter') -> 'PNCounter':
        """Merge two PN-Counters."""
        result = PNCounter()
        for node, count in c1.positive.items():
            result.increment(node, count)
        for node, count in c1.negative.items():
            result.decrement(node, count)
        for node, count in c2.positive.items():
            result.increment(node, count)
        for node, count in c2.negative.items():
            result.decrement(node, count)
        return result

    def _merge_gset(self, s1: 'GSet', s2: 'GSet') -> 'GSet':
        """Merge two G-Sets."""
        result = GSet()
        result.elements.update(s1.elements)
        result.elements.update(s2.elements)
        return result

    def _merge_twophase_set(self, s1: 'TwoPhaseSet', s2: 'TwoPhaseSet') -> 'TwoPhaseSet':
        """Merge two 2P-Sets."""
        result = TwoPhaseSet()
        result.add_set.update(s1.add_set)
        result.add_set.update(s2.add_set)
        result.remove_set.update(s1.remove_set)
        result.remove_set.update(s2.remove_set)
        return result

    def _merge_orset(self, s1: 'ORSet', s2: 'ORSet') -> 'ORSet':
        """Merge two OR-Sets."""
        result = ORSet()
        for k, v in s1.elements.items():
            result.add(k, v)
        for k, v in s2.elements.items():
            result.add(k, v)
        return result

    def _merge_lww_register(self, r1: 'LWWRegister', r2: 'LWWRegister') -> 'LWWRegister':
        """Merge two LWW-Registers."""
        if r1.timestamp > r2.timestamp:
            return r1
        elif r2.timestamp > r1.timestamp:
            return r2
        return r1  # arbitrary tie-breaker

    def _merge_mv_register(self, r1: 'MVRegister', r2: 'MVRegister') -> 'MVRegister':
        """Merge two MV-Registers."""
        result = MVRegister()
        result.values.update(r1.values)
        result.values.update(r2.values)
        return result

    def list_all(self) -> List[str]:
        """List all registered CRDT keys."""
        return list(self._registry.keys())

    def remove(self, key: str) -> None:
        """Remove a CRDT from the registry."""
        if key in self._registry:
            del self._registry[key]

    def clear(self) -> None:
        """Clear all registered CRDTs."""
        self._registry.clear()


# CRDT Implementations

class GCounter:
    """G-Counter (Grow-only Counter) - supports only increment."""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}

    def increment(self, node_id: str, count: int = 1) -> None:
        """Increment counter for given node."""
        self.counters[node_id] = self.counters.get(node_id, 0) + count

    def value(self) -> int:
        """Get total counter value."""
        return sum(self.counters.values())

    def merge(self, other: 'GCounter') -> 'GCounter':
        """Merge with another GCounter."""
        result = GCounter()
        for node, count in self.counters.items():
            result.increment(node, count)
        for node, count in other.counters.items():
            result.increment(node, count)
        return result


class PNCounter:
    """PN-Counter (Positive-Negative Counter) - supports increment and decrement."""
    
    def __init__(self):
        self.positive: Dict[str, int] = {}
        self.negative: Dict[str, int] = {}

    def increment(self, node_id: str, count: int = 1) -> None:
        """Increment positive counter."""
        self.positive[node_id] = self.positive.get(node_id, 0) + count

    def decrement(self, node_id: str, count: int = 1) -> None:
        """Decrement negative counter."""
        self.negative[node_id] = self.negative.get(node_id, 0) + count

    def value(self) -> int:
        """Get total value."""
        pos = sum(self.positive.values())
        neg = sum(self.negative.values())
        return pos - neg

    def merge(self, other: 'PNCounter') -> 'PNCounter':
        """Merge with another PNCounter."""
        result = PNCounter()
        for node, count in self.positive.items():
            result.increment(node, count)
        for node, count in self.negative.items():
            result.decrement(node, count)
        for node, count in other.positive.items():
            result.increment(node, count)
        for node, count in other.negative.items():
            result.decrement(node, count)
        return result


class GSet:
    """G-Set (Grow-only Set) - supports only add."""
    
    def __init__(self):
        self.elements: Set[str] = set()

    def add(self, element: str) -> None:
        """Add element to set."""
        self.elements.add(element)

    def contains(self, element: str) -> bool:
        """Check if element is in set."""
        return element in self.elements

    def merge(self, other: 'GSet') -> 'GSet':
        """Merge with another GSet."""
        result = GSet()
        result.elements.update(self.elements)
        result.elements.update(other.elements)
        return result


class TwoPhaseSet:
    """2P-Set (Two-Phase Set) - supports explicit add and remove."""
    
    def __init__(self):
        self.add_set: Set[str] = set()
        self.remove_set: Set[str] = set()

    def add(self, element: str) -> None:
        """Add element to add-set."""
        self.add_set.add(element)
        self.remove_set.discard(element)

    def remove(self, element: str) -> None:
        """Remove element from add-set by adding to remove-set."""
        self.remove_set.add(element)
        self.add_set.discard(element)

    def contains(self, element: str) -> bool:
        """Check if element is present."""
        return element in self.add_set and element not in self.remove_set

    def merge(self, other: 'TwoPhaseSet') -> 'TwoPhaseSet':
        """Merge with another 2P-Set."""
        result = TwoPhaseSet()
        result.add_set.update(self.add_set)
        result.add_set.update(other.add_set)
        result.remove_set.update(self.remove_set)
        result.remove_set.update(other.remove_set)
        return result


class ORSet:
    """OR-Set (Observed-Remove Set) - supports add and remove with unique IDs."""
    
    def __init__(self):
        self.elements: Dict[str, Set[str]] = {}

    def add(self, element: str, id: str) -> None:
        """Add element with unique ID."""
        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add(id)

    def remove(self, element: str, id: str) -> None:
        """Remove element with specific ID."""
        if element in self.elements:
            self.elements[element].discard(id)
            if not self.elements[element]:
                del self.elements[element]

    def contains(self, element: str) -> bool:
        """Check if element is present."""
        return element in self.elements and self.elements[element]

    def merge(self, other: 'ORSet') -> 'ORSet':
        """Merge with another ORSet."""
        result = ORSet()
        for k, v in self.elements.items():
            result.elements[k] = set(v)
        for k, v in other.elements.items():
            if k not in result.elements:
                result.elements[k] = set(v)
            else:
                result.elements[k].update(v)
        return result


class LWWRegister:
    """LWW-Register (Last-Writer-Wins Register) - supports value and timestamp."""
    
    def __init__(self, value: Any = None, timestamp: float = None):
        self.value = value
        self.timestamp = timestamp or time.time()

    def write(self, value: Any, timestamp: float = None) -> None:
        """Write new value."""
        self.value = value
        self.timestamp = timestamp or time.time()

    def read(self) -> Any:
        """Read current value."""
        return self.value

    def merge(self, other: 'LWWRegister') -> 'LWWRegister':
        """Merge with another LWWRegister."""
        if self.timestamp >= other.timestamp:
            return self
        return other


class MVRegister:
    """MV-Register (Multi-Value Register) - supports multiple values."""
    
    def __init__(self):
        self.values: Set[Any] = set()

    def write(self, value: Any) -> None:
        """Write new value."""
        self.values.add(value)

    def read(self) -> List[Any]:
        """Read all values."""
        return list(self.values)

    def merge(self, other: 'MVRegister') -> 'MVRegister':
        """Merge with another MVRegister."""
        result = MVRegister()
        result.values.update(self.values)
        result.values.update(other.values)
        return result


# Tests

def test_gcounter():
    bridge = CRDTToQuiltBridge()
    c1 = GCounter()
    c1.increment("node1", 5)
    c1.increment("node2", 3)
    key1 = bridge.register("G-Counter", c1)
    cell = bridge.get_cell(key1)
    assert cell["type"] == "G-Counter"
    assert cell["state"] == {"node1": 5, "node2": 3}
    assert cell["size"] == 8
    assert cell["invariant"] == "sum_all_counters"
    assert cell["vibe"] == 8.0
    assert cell["murmur"] == "push-pull"
    assert cell["primitives"] == ["create", "update", "merge", "read", "delete", "conflict", "sync", "validate"]


def test_pncounter():
    bridge = CRDTToQuiltBridge()
    c1 = PNCounter()
    c1.increment("node1", 5)
    c1.decrement("node1", 2)
    c1.increment("node2", 3)
    key1 = bridge.register("PN-Counter", c1)
    cell = bridge.get_cell(key1)
    assert cell["type"] == "PN-Counter"
    assert cell["state"] == {"positive": {"node1": 5, "node2": 3}, "negative": {"node1": 2}}
    assert cell["size"] == 5
    assert cell["invariant"] == "positive_minus_negative"
    assert cell["vibe"] == 5.0
    assert cell["murmur"] == "pull"


def test_gset():
    bridge = CRDTToQuiltBridge()
    s1 = GSet()
    s1.add("a")
    s1.add("b")
    key1 = bridge.register("G-Set", s1)
    cell = bridge.get_cell(key1)
    assert cell["type"] == "G-Set"
    assert cell["state"] == ["a", "b"]
    assert cell["size"] == 2
    assert cell["invariant"] == "union_adds"
    assert cell["vibe"] == 2.0
    assert cell["murmur"] == "push"


def test_twophase_set():
    bridge = CRDTToQuiltBridge()
    s1 = TwoPhaseSet()
    s1.add("x")
    s1.remove("x")
    key1 = bridge.register("2P-Set", s1)
    cell = bridge.get_cell(key1)
    assert cell["type"] == "2P-Set"
    assert cell["state"] == {"add_set": [], "remove_set": ["x"]}
    assert cell["size"] == 1
    assert cell["invariant"] == "add_before_remove"
    assert cell["vibe"] == 1.0
    assert cell["murmur"] == "push-pull"


def test_orset():
    bridge = CRDTToQuiltBridge()
    s1 = ORSet()
    s1.add("item1", "id1")
    s1.add("item1", "id2")
    s1.remove("item1", "id1")
    key1 = bridge.register("OR-Set", s1)
    cell = bridge.get_cell(key1)
    assert cell["type"] == "OR-Set"
    assert cell["state"] == {"item1": ["id2"]}
    assert cell["size"] == 1
    assert cell["invariant"] == "add_and_remove_sets"
    assert cell["vibe"] == 1.0
    assert cell["murmur"] == "push-pull"


def test_lww_register():
    bridge = CRDTToQuiltBridge()
    r1 = LWWRegister("value1", time.time() - 10)
    r2 = LWWRegister("value2", time.time())
    key1 = bridge.register("LWW-Register", r1)
    key2 = bridge.register("LWW-Register", r2)
    merged_key = bridge.merge(key1, key2)
    merged_cell = bridge.get_cell(merged_key)
    assert merged_cell["type"] == "LWW-Register"
    assert merged_cell["state"] == "value2"
    assert merged_cell["invariant"] == "latest_writes_win"
    assert merged_cell["vibe"] == 0.0
    assert merged_cell["murmur"] == "push"


def test_mv_register():
    bridge = CRDTToQuiltBridge()
    r1 = MVRegister()
    r1.write("val1")
    r1.write("val2")
    r2 = MVRegister()
    r2.write("val3")
    key1 = bridge.register("MV-Register", r1)
    key2 = bridge.register("MV-Register", r2)
    merged_key = bridge.merge(key1, key2)
    merged_cell = bridge.get_cell(merged_key)
    assert merged_cell["type"] == "MV-Register"
    assert sorted(merged_cell["state"]) == ["val1", "val2", "val3"]
    assert merged_cell["invariant"] == "all_values_present"
    assert merged_cell["vibe"] == 3.0
    assert merged_cell["murmur"] == "pull"


def run_tests():
    """Run all tests."""
    print("Running CRDT to Quilt Bridge tests...")
    test_gcounter()
    test_pncounter()
    test_gset()
    test_twophase_set()
    test_orset()
    test_lww_register()
    test_mv_register()
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
