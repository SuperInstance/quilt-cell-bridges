"""
Capitaine Family to Quilt Bridge

This module bridges the Capitaine Substrate (captain, commodore, admiral, fleet, bosun) 
to the Quilt data structure system. It provides a transformation layer that maps 
the hierarchical naval hierarchy to a quilt-like tree of data nodes with consistent
serialization, access, and traversal semantics.

The 8 primitives:
1. Captain    - Base entity, single node, no children.
2. Commodore  - Node with ordered children, supports indexing.
3. Admiral    - Node with named children, supports key lookup.
4. Fleet      - Composite node, can be any type, can have both indexed and named children.
5. Bosun      - Specialized node for metadata and labels.
6. Quilt      - The top-level container, root of the hierarchy.
7. Node       - Abstract base for all nodes.
8. Edge       - Lightweight pointer between nodes.

All operations are pure, stateless, and use only the Python standard library.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
import json
import copy


class NodeType(Enum):
    CAPTAIN = "captain"
    COMMODORE = "commodore"
    ADMIRAL = "admiral"
    FLEET = "fleet"
    BOSUN = "bosun"
    QUILT = "quilt"


@dataclass
class Edge:
    """Lightweight pointer between nodes. Captures source, target, and label."""
    source: str
    target: str
    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Edge':
        return cls(
            source=data["source"],
            target=data["target"],
            label=data.get("label")
        )


@dataclass
class Node:
    """Abstract base for all nodes in the hierarchy."""
    id: str
    type: NodeType
    metadata: Dict[str, Any] = None
    children: Any = None  # List or Dict depending on type

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self._validate()

    def _validate(self):
        if not self.id:
            raise ValueError("Node ID cannot be empty")
        if not isinstance(self.id, str):
            raise TypeError("Node ID must be a string")
        if not isinstance(self.metadata, dict):
            raise TypeError("Node metadata must be a dict")
        if self.children is not None and not self._is_valid_children_type():
            raise ValueError(f"Invalid children type for {self.type}")

    def _is_valid_children_type(self) -> bool:
        if self.type in (NodeType.CAPTAIN, NodeType.BOSUN):
            return self.children is None
        elif self.type == NodeType.COMMODORE:
            return isinstance(self.children, list) and all(isinstance(c, str) for c in self.children)
        elif self.type == NodeType.ADMIRAL:
            return isinstance(self.children, dict) and all(isinstance(k, str) for k in self.children.keys())
        elif self.type == NodeType.FLEET:
            return isinstance(self.children, (list, dict)) and (
                (isinstance(self.children, list) and all(isinstance(c, str) for c in self.children)) or
                (isinstance(self.children, dict) and all(isinstance(k, str) for k in self.children.keys()))
            )
        elif self.type == NodeType.QUILT:
            return isinstance(self.children, (list, dict)) and (
                (isinstance(self.children, list) and all(isinstance(c, str) for c in self.children)) or
                (isinstance(self.children, dict) and all(isinstance(k, str) for k in self.children.keys()))
            )
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "metadata": self.metadata,
            "children": self.children
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            metadata=data.get("metadata", {}),
            children=data.get("children")
        )

    def get_child(self, key: Union[str, int]) -> Optional[str]:
        if self.children is None:
            return None
        if isinstance(self.children, list):
            if isinstance(key, int) and 0 <= key < len(self.children):
                return self.children[key]
            elif isinstance(key, str) and key in self.children:
                return key
        elif isinstance(self.children, dict):
            if isinstance(key, str) and key in self.children:
                return key
        return None

    def get_children_keys(self) -> List[Union[str, int]]:
        if self.children is None:
            return []
        if isinstance(self.children, list):
            return list(range(len(self.children)))
        elif isinstance(self.children, dict):
            return list(self.children.keys())
        return []


class Captain(Node):
    """Base node with no children. Represents a leaf unit."""

    def __init__(self, id: str, metadata: Dict[str, Any] = None):
        super().__init__(id=id, type=NodeType.CAPTAIN, metadata=metadata, children=None)

    def __repr__(self):
        return f"Captain(id={self.id}, metadata={self.metadata})"


class Commodore(Node):
    """Ordered list of child node IDs."""

    def __init__(self, id: str, children: List[str], metadata: Dict[str, Any] = None):
        super().__init__(id=id, type=NodeType.COMMODORE, metadata=metadata, children=children)

    def __repr__(self):
        return f"Commodore(id={self.id}, children={self.children}, metadata={self.metadata})"

    def insert_at(self, index: int, child_id: str) -> 'Commodore':
        """Insert child at index, return new instance."""
        new_children = self.children.copy()
        new_children.insert(index, child_id)
        return Commodore(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))

    def remove_at(self, index: int) -> 'Commodore':
        """Remove child at index, return new instance."""
        if not (0 <= index < len(self.children)):
            raise IndexError("Index out of range")
        new_children = self.children.copy()
        del new_children[index]
        return Commodore(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))

    def append(self, child_id: str) -> 'Commodore':
        """Append child, return new instance."""
        new_children = self.children.copy()
        new_children.append(child_id)
        return Commodore(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))


class Admiral(Node):
    """Named children (dictionary)."""

    def __init__(self, id: str, children: Dict[str, str], metadata: Dict[str, Any] = None):
        super().__init__(id=id, type=NodeType.ADMIRAL, metadata=metadata, children=children)

    def __repr__(self):
        return f"Admiral(id={self.id}, children={self.children}, metadata={self.metadata})"

    def add(self, key: str, child_id: str) -> 'Admiral':
        """Add named child, return new instance."""
        new_children = self.children.copy()
        new_children[key] = child_id
        return Admiral(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))

    def remove(self, key: str) -> 'Admiral':
        """Remove child by key, return new instance."""
        if key not in self.children:
            raise KeyError(f"Key {key} not found in children")
        new_children = self.children.copy()
        del new_children[key]
        return Admiral(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))

    def get(self, key: str) -> Optional[str]:
        """Get child by key."""
        return self.children.get(key)


class Fleet(Node):
    """Composite node with mixed or unified child structure."""

    def __init__(self, id: str, children: Union[List[str], Dict[str, str]], metadata: Dict[str, Any] = None):
        super().__init__(id=id, type=NodeType.FLEET, metadata=metadata, children=children)

    def __repr__(self):
        return f"Fleet(id={self.id}, children={self.children}, metadata={self.metadata})"

    def is_indexed(self) -> bool:
        """Check if children are list-based (ordered)."""
        return isinstance(self.children, list)

    def is_named(self) -> bool:
        """Check if children are dict-based (named)."""
        return isinstance(self.children, dict)

    def merge(self, other: 'Fleet') -> 'Fleet':
        """Merge with another fleet. Only supports same type of children."""
        if not isinstance(other, Fleet):
            raise TypeError("Can only merge with Fleet")
        if isinstance(self.children, list) and isinstance(other.children, list):
            new_children = self.children + other.children
            return Fleet(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))
        elif isinstance(self.children, dict) and isinstance(other.children, dict):
            new_children = {**self.children, **other.children}
            return Fleet(id=self.id, children=new_children, metadata=copy.deepcopy(self.metadata))
        else:
            raise ValueError("Cannot merge heterogeneous child types")


class Bosun(Node):
    """Metadata-only node. Used for labels, annotations."""

    def __init__(self, id: str, metadata: Dict[str, Any] = None):
        super().__init__(id=id, type=NodeType.BOSUN, metadata=metadata, children=None)

    def __repr__(self):
        return f"Bosun(id={self.id}, metadata={self.metadata})"

    def set_label(self, key: str, value: Any) -> 'Bosun':
        """Set a label, return new instance."""
        new_metadata = copy.deepcopy(self.metadata)
        new_metadata[key] = value
        return Bosun(id=self.id, metadata=new_metadata)


class Quilt:
    """Top-level container for the entire hierarchy."""

    def __init__(self, root_id: str):
        self._root_id = root_id
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []

    @property
    def root_id(self) -> str:
        return self._root_id

    def add_node(self, node: Node) -> 'Quilt':
        """Add a node to the quilt. Returns new quilt instance."""
        new_quilt = copy.deepcopy(self)
        new_quilt._nodes[node.id] = node
        return new_quilt

    def add_edge(self, source: str, target: str, label: Optional[str] = None) -> 'Quilt':
        """Add an edge between nodes. Returns new quilt instance."""
        new_quilt = copy.deepcopy(self)
        new_quilt._edges.append(Edge(source=source, target=target, label=label))
        return new_quilt

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def get_children(self, parent_id: str) -> List[str]:
        """Get all child IDs of a parent."""
        node = self.get_node(parent_id)
        if not node:
            raise KeyError(f"Parent node {parent_id} not found")
        return node.children if node.children is not None else []

    def get_all_edges(self) -> List[Edge]:
        """Return all edges."""
        return self._edges

    def to_dict(self) -> Dict[str, Any]:
        """Serialize quilt to dictionary."""
        return {
            "root": self._root_id,
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "edges": [e.to_dict() for e in self._edges]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quilt':
        """Deserialize quilt from dictionary."""
        quilt = cls(root_id=data["root"])
        for node_id, node_data in data["nodes"].items():
            node = Node.from_dict(node_data)
            quilt._nodes[node_id] = node
        for edge_data in data["edges"]:
            edge = Edge.from_dict(edge_data)
            quilt._edges.append(edge)
        return quilt

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Quilt':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> bool:
        """Validate internal consistency."""
        # Check root exists
        if self._root_id not in self._nodes:
            return False
        # Check all child references exist
        for node in self._nodes.values():
            if node.children is not None:
                if isinstance(node.children, list):
                    for child_id in node.children:
                        if child_id not in self._nodes:
                            return False
                elif isinstance(node.children, dict):
                    for child_id in node.children.values():
                        if child_id not in self._nodes:
                            return False
        return True

    def __repr__(self):
        return f"Quilt(root={self._root_id}, node_count={len(self._nodes)}, edge_count={len(self._edges)})"


# Bridge functions
def capitaine_to_quilt(captain: Captain, commodore: Commodore, admiral: Admiral, fleet: Fleet, bosun: Bosun) -> Quilt:
    """
    Transform Capitaine family nodes to a Quilt.
    All nodes are added to the quilt with a root node that ties them together.
    """
    quilt = Quilt(root_id="root")

    # Add all nodes
    quilt = quilt.add_node(captain)
    quilt = quilt.add_node(commodore)
    quilt = quilt.add_node(admiral)
    quilt = quilt.add_node(fleet)
    quilt = quilt.add_node(bosun)

    # Create edges to form a directed hierarchy
    # Root points to all major nodes
    quilt = quilt.add_edge("root", captain.id, "chief")
    quilt = quilt.add_edge("root", commodore.id, "command")
    quilt = quilt.add_edge("root", admiral.id, "strategy")
    quilt = quilt.add_edge("root", fleet.id, "fleet")
    quilt = quilt.add_edge("root", bosun.id, "log")

    # Use the commodore's list to link to captains (if any)
    for i, child_id in enumerate(commodore.children):
        if child_id in quilt._nodes:
            quilt = quilt.add_edge(commodore.id, child_id, f"subordinate_{i}")

    # Use admiral's dict to link to specific fleet sections
    for key, child_id in admiral.children.items():
        if child_id in quilt._nodes:
            quilt = quilt.add_edge(admiral.id, child_id, f"assigned_{key}")

    # Use fleet's children to link to each component
    if isinstance(fleet.children, list):
        for child_id in fleet.children:
            if child_id in quilt._nodes:
                quilt = quilt.add_edge(fleet.id, child_id, "component")
    elif isinstance(fleet.children, dict):
        for key, child_id in fleet.children.items():
            if child_id in quilt._nodes:
                quilt = quilt.add_edge(fleet.id, child_id, f"component_{key}")

    return quilt


def quilt_to_capitaine(quilt: Quilt) -> Tuple[Captain, Commodore, Admiral, Fleet, Bosun]:
    """
    Extract Capitaine family nodes from a quilt.
    Assumes the quilt was built by capitaine_to_quilt.
    """
    captain = quilt.get_node("captain")
    commodore = quilt.get_node("commodore")
    admiral = quilt.get_node("admiral")
    fleet = quilt.get_node("fleet")
    bosun = quilt.get_node("bosun")

    if not all(n is not None for n in [captain, commodore, admiral, fleet, bosun]):
        raise ValueError("Missing one or more required Capitaine nodes in quilt")

    return captain, commodore, admiral, fleet, bosun


# Test cases
def test_capitaine_to_quilt():
    """Test full transformation from Capitaine to Quilt."""
    captain = Captain(id="captain-1", metadata={"rank": "Lt. Cmdr"})
    commodore = Commodore(id="commodore-1", children=["captain-1", "captain-2"], metadata={"rank": "Commodore"})
    admiral = Admiral(id="admiral-1", children={"fleet": "fleet-1", "log": "bosun-1"}, metadata={"rank": "Admiral"})
    fleet = Fleet(id="fleet-1", children=["captain-2", "captain-3"], metadata={"type": "task force"})
    bosun = Bosun(id="bosun-1", metadata={"notes": "logbook entry"})

    quilt = capitaine_to_quilt(captain, commodore, admiral, fleet, bosun)

    assert quilt.root_id == "root"
    assert len(quilt._nodes) == 5
    assert len(quilt._edges) == 10  # 5 direct from root + 5 internal
    assert quilt.validate() is True

    # Verify node types
    assert isinstance(quilt.get_node("captain-1"), Captain)
    assert isinstance(quilt.get_node("commodore-1"), Commodore)
    assert isinstance(quilt.get_node("admiral-1"), Admiral)
    assert isinstance(quilt.get_node("fleet-1"), Fleet)
    assert isinstance(quilt.get_node("bosun-1"), Bosun)

    # Test JSON round-trip
    json_str = quilt.to_json()
    quilt2 = Quilt.from_json(json_str)
    assert quilt2.validate() is True
    assert quilt.to_dict() == quilt2.to_dict()


def test_quilt_to_capitaine():
    """Test extraction in reverse."""
    captain = Captain(id="captain-1", metadata={"rank": "Lt. Cmdr"})
    commodore = Commodore(id="commodore-1", children=["captain-1"], metadata={"rank": "Commodore"})
    admiral = Admiral(id="admiral-1", children={"fleet": "fleet-1"}, metadata={"rank": "Admiral"})
    fleet = Fleet(id="fleet-1", children=["captain-2"], metadata={"type": "task force"})
    bosun = Bosun(id="bosun-1", metadata={"notes": "logbook entry"})

    quilt = capitaine_to_quilt(captain, commodore, admiral, fleet, bosun)
    extracted = quilt_to_capitaine(quilt)

    assert extracted[0].id == captain.id
    assert extracted[1].id == commodore.id
    assert extracted[2].id == admiral.id
    assert extracted[3].id == fleet.id
    assert extracted[4].id == bosun.id

    # Verify metadata
    assert extracted[0].metadata == captain.metadata
    assert extracted[3].children == fleet.children
    assert extracted[4].metadata == bosun.metadata


if __name__ == "__main__":
    # Run tests
    test_capitaine_to_quilt()
    test_quilt_to_capitaine()
    print("All tests passed.")
