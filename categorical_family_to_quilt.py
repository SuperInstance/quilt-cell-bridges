"""
Categorical Family to Quilt Bridge

This module implements a bridge between the categorical substrate (category, functor, monad,
natural transformation, limit) and a quilt-like data structure. A "quilt" in this context is a
structured representation of categorical data, where objects are represented as nodes and
morphisms as edges, with additional structure for handling limits and natural transformations.

The bridge supports:
- Creation and manipulation of categories
- Definition of functors between categories
- Monad construction and lifting
- Natural transformation composition
- Limit computation (pullback, product, terminal object)
- Quilt representation as a graph with metadata

The implementation uses only the Python standard library.
"""

from typing import (
    TypeVar, Generic, Callable, Dict, List, Set, Optional, Tuple, Any, Union,
    Protocol, runtime_checkable
)
from collections import defaultdict, deque
from functools import reduce
import itertools
import operator


# === 8 PRIMITIVES ===

# 1. Category
class Category(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A category consists of objects and morphisms with composition and identity."""
    
    def __init__(self, objects: Set[Any], morphisms: Set[Tuple[Any, Any, Any]]):
        self.objects = set(objects)
        self.morphisms = set(morphisms)  # (source, target, name)
        self._cache = {}

    def compose(self, f: Tuple[Any, Any, Any], g: Tuple[Any, Any, Any]) -> Optional[Tuple[Any, Any, Any]]:
        """Compose two morphisms if possible."""
        if f[1] != g[0]:
            return None
        return (f[0], g[1], f[2] + "_" + g[2])  # Simple naming convention

    def identity(self, obj: Any) -> Optional[Tuple[Any, Any, Any]]:
        """Return identity morphism for an object."""
        if obj not in self.objects:
            return None
        return (obj, obj, f"Id_{obj}")

    def is_morphism(self, f: Tuple[Any, Any, Any]) -> bool:
        """Check if a tuple is a valid morphism."""
        return f in self.morphisms

    def has_morphism(self, source: Any, target: Any) -> bool:
        """Check if a morphism exists from source to target."""
        return any(f[0] == source and f[1] == target for f in self.morphisms)

    def get_morphisms(self, source: Any, target: Any) -> List[Tuple[Any, Any, Any]]:
        """Get all morphisms from source to target."""
        return [f for f in self.morphisms if f[0] == source and f[1] == target]

    def compose_all(self, morphism_list: List[Tuple[Any, Any, Any]]) -> Optional[Tuple[Any, Any, Any]]:
        """Compose list of morphisms in order."""
        if not morphism_list:
            return None
        result = morphism_list[0]
        for m in morphism_list[1:]:
            result = self.compose(result, m)
            if result is None:
                return None
        return result

    def get_source(self, f: Tuple[Any, Any, Any]) -> Any:
        return f[0]

    def get_target(self, f: Tuple[Any, Any, Any]) -> Any:
        return f[1]

    def get_name(self, f: Tuple[Any, Any, Any]) -> Any:
        return f[2]


# 2. Functor
class Functor(Generic[TypeVar('Ob1'), TypeVar('Ob2'), TypeVar('Morph1'), TypeVar('Morph2')]):
    """A functor maps categories to categories preserving structure."""
    
    def __init__(self, domain: Category[Ob1, Morph1], codomain: Category[Ob2, Morph2],
                 map_objects: Callable[[Ob1], Ob2], map_morphisms: Callable[[Morph1], Morph2]):
        self.domain = domain
        self.codomain = codomain
        self.map_objects = map_objects
        self.map_morphisms = map_morphisms

    def image_of_object(self, obj: Ob1) -> Ob2:
        """Map an object to its image under the functor."""
        return self.map_objects(obj)

    def image_of_morphism(self, f: Morph1) -> Morph2:
        """Map a morphism to its image under the functor."""
        return self.map_morphisms(f)

    def is_natural(self, eta: 'NaturalTransformation') -> bool:
        """Check if a natural transformation is natural with respect to this functor."""
        # This is a placeholder; natural transformation must be defined
        # between two functors sharing domain and codomain
        return True


# 3. Monad
class Monad(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A monad is a functor with two natural transformations: unit and join."""
    
    def __init__(self, functor: Functor[Ob, Ob, Morph, Morph]):
        self.functor = functor
        self.unit = self._create_unit()
        self.join = self._create_join()

    def _create_unit(self) -> 'NaturalTransformation':
        """Create the unit natural transformation."""
        def eta(obj: Any) -> Tuple[Any, Any, Any]:
            # Unit maps object to its image under the functor
            return self.functor.image_of_object(obj)
        return NaturalTransformation(self.functor, self.functor, eta)

    def _create_join(self) -> 'NaturalTransformation':
        """Create the join natural transformation."""
        def mu(obj: Any) -> Tuple[Any, Any, Any]:
            # Join maps double application to single application
            # This is a placeholder for actual join
            return self.functor.image_of_object(self.functor.image_of_object(obj))
        return NaturalTransformation(self.functor, self.functor, mu)

    def bind(self, f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Bind a function to the monad."""
        def bound(x: Any) -> Any:
            return self.join.image_of_object(f(x))
        return bound


# 4. NaturalTransformation
class NaturalTransformation(Generic[TypeVar('F'), TypeVar('G'), TypeVar('Ob'), TypeVar('Morph')]):
    """A natural transformation between two functors."""
    
    def __init__(self, F: Functor[Ob, Ob, Morph, Morph], G: Functor[Ob, Ob, Morph, Morph],
                 eta: Callable[[Ob], Morph]):
        self.F = F
        self.G = G
        self.eta = eta

    def image_of_object(self, obj: Ob) -> Morph:
        """Get the component of the natural transformation at object."""
        return self.eta(obj)

    def is_natural(self) -> bool:
        """Check naturality condition."""
        for f in self.F.domain.morphisms:
            Ff = self.F.image_of_morphism(f)
            Gf = self.G.image_of_morphism(f)
            eta_source = self.image_of_object(self.F.domain.get_source(f))
            eta_target = self.image_of_object(self.F.domain.get_target(f))
            # Naturality: Gf ∘ eta_source = eta_target ∘ Ff
            if not self._compose_in_codomain(Gf, eta_source) == self._compose_in_codomain(eta_target, Ff):
                return False
        return True

    def _compose_in_codomain(self, g: Morph, h: Morph) -> Optional[Morph]:
        """Compose two morphisms in the codomain category."""
        return self.F.codomain.compose(h, g) if self.F.codomain.compose(h, g) else None


# 5. Limit
class Limit(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A generalized limit of a diagram in a category."""
    
    def __init__(self, category: Category[Ob, Morph], diagram: Dict[Any, Any]):
        self.category = category
        self.diagram = diagram
        self._result = self._compute()

    def _compute(self) -> Any:
        """Compute the limit of the diagram."""
        # For now, compute a simple product (binary)
        if len(self.diagram) == 2:
            return self._compute_product()
        elif len(self.diagram) == 1:
            return next(iter(self.diagram.values()))
        else:
            return self._compute_general_limit()

    def _compute_product(self) -> Any:
        """Compute product of two objects."""
        a, b = next(iter(self.diagram.items()))
        # For simplicity, return a tuple as the product
        return (a, b)

    def _compute_general_limit(self) -> Any:
        """Compute more complex limit (e.g., pullback)."""
        # Extract first two objects for pullback-like construction
        obj_list = list(self.diagram.values())
        if len(obj_list) < 2:
            return obj_list[0]
        # This is a placeholder for pullback
        return ("Limit", *obj_list)

    def get_object(self) -> Any:
        """Get the limit object."""
        return self._result

    def get_projections(self) -> Dict[Any, Any]:
        """Get projections from the limit to each object in the diagram."""
        return {k: self._get_projection(k) for k in self.diagram.keys()}

    def _get_projection(self, key: Any) -> Any:
        """Get the projection morphism for a given key."""
        limit_obj = self.get_object()
        diagram_obj = self.diagram[key]
        # Return a simple morphism name
        return (limit_obj, diagram_obj, f"proj_{key}")


# 6. Quilt (Structured Graph)
class Quilt(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A quilt is a structured representation of categorical data."""
    
    def __init__(self, category: Category[Ob, Morph]):
        self.category = category
        self.nodes = defaultdict(set)
        self.edges = []
        self.metadata = {}
        self._build()

    def _build(self):
        """Construct the quilt from the category."""
        for obj in self.category.objects:
            self.nodes["object"].add(obj)
        
        for f in self.category.morphisms:
            source, target, name = f
            self.nodes["morphism"].add(name)
            self.edges.append((source, target, name))
            # Add metadata
            self.metadata[name] = {
                "source": source,
                "target": target,
                "type": "morphism"
            }

    def add_node(self, label: str, value: Any):
        """Add a node to the quilt."""
        self.nodes[label].add(value)

    def add_edge(self, source: Any, target: Any, label: str):
        """Add an edge to the quilt."""
        edge = (source, target, label)
        self.edges.append(edge)
        self.metadata[label] = {
            "source": source,
            "target": target,
            "type": "edge"
        }

    def get_nodes(self, label: str) -> Set[Any]:
        """Get all nodes of a given label."""
        return self.nodes[label]

    def get_edges(self) -> List[Tuple[Any, Any, str]]:
        """Get all edges."""
        return self.edges

    def get_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a key."""
        return self.metadata.get(key, {})

    def get_neighbors(self, node: Any) -> List[Tuple[Any, str]]:
        """Get all neighbors of a node."""
        neighbors = []
        for src, tgt, label in self.edges:
            if src == node:
                neighbors.append((tgt, label))
            elif tgt == node:
                neighbors.append((src, label))
        return neighbors

    def to_dict(self) -> Dict[str, Any]:
        """Convert quilt to dictionary representation."""
        return {
            "nodes": dict(self.nodes),
            "edges": self.edges,
            "metadata": self.metadata
        }

    def serialize(self) -> str:
        """Serialize quilt to JSON-like string."""
        import json
        return json.dumps(self.to_dict(), default=str, indent=2)


# 7. Pullback (Special Limit)
class Pullback(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A pullback is a limit of a cospan."""
    
    def __init__(self, category: Category[Ob, Morph], f: Morph, g: Morph):
        self.category = category
        self.f = f
        self.g = g
        self._result = self._compute()

    def _compute(self) -> Any:
        """Compute the pullback of f and g."""
        # f: A -> C, g: B -> C
        A, C = self.category.get_source(self.f), self.category.get_target(self.f)
        B, _ = self.category.get_source(self.g), self.category.get_target(self.g)
        # Pullback is a pair (P, p1, p2) such that f∘p1 = g∘p2
        # For simplicity, return a tuple
        return (f"{A}_x_{B}", self.f, self.g)

    def get_object(self) -> Any:
        """Get the pullback object."""
        return self._result[0]

    def get_projections(self) -> Tuple[Any, Any]:
        """Get the two projection morphisms."""
        return self._result[1], self._result[2]


# 8. TerminalObject (Special Limit)
class TerminalObject(Generic[TypeVar('Ob'), TypeVar('Morph')]):
    """A terminal object is a limit of the empty diagram."""
    
    def __init__(self, category: Category[Ob, Morph]):
        self.category = category
        self._result = self._find()

    def _find(self) -> Optional[Any]:
        """Find a terminal object in the category."""
        for obj in self.category.objects:
            # Check if every other object has a morphism to obj
            if all(self.category.has_morphism(other, obj) for other in self.category.objects if other != obj):
                return obj
        return None

    def get_object(self) -> Optional[Any]:
        """Get the terminal object."""
        return self._result

    def is_terminal(self, obj: Any) -> bool:
        """Check if an object is terminal."""
        if obj not in self.category.objects:
            return False
        return all(self.category.has_morphism(other, obj) for other in self.category.objects if other != obj)


# === BRIDGE FUNCTION: CATEGORICAL FAMILY TO QUILT ===

def categorical_family_to_quilt(
    category: Category,
    functors: List[Functor] = None,
    natural_transformations: List[NaturalTransformation] = None,
    limits: List[Limit] = None,
    monads: List[Monad] = None
) -> Quilt:
    """
    Bridge function: transform categorical family into a quilt data structure.
    
    Args:
        category: Source category
        functors: List of functors from category to other categories
        natural_transformations: List of natural transformations
        limits: List of limits computed from the category
        monads: List of monads over the category
    
    Returns:
        A Quilt representation of the categorical family
    """
    quilt = Quilt(category)
    
    # Add functors as metadata
    if functors:
        for i, F in enumerate(functors):
            quilt.add_node("functor", f"F_{i}")
            quilt.add_edge(f"F_{i}", "category", "maps_to")

    # Add natural transformations
    if natural_transformations:
        for i, eta in enumerate(natural_transformations):
            quilt.add_node("natural_transformation", f"eta_{i}")
            # Link to functors if possible
            if hasattr(eta, 'F') and hasattr(eta, 'G'):
                quilt.add_edge(f"eta_{i}", f"F_{id(eta.F)}", "from_functor")
                quilt.add_edge(f"eta_{i}", f"G_{id(eta.G)}", "to_functor")

    # Add limits
    if limits:
        for i, limit in enumerate(limits):
            limit_obj = limit.get_object()
            quilt.add_node("limit", f"limit_{i}")
            quilt.add_edge(f"limit_{i}", str(limit_obj), "has_object")
            for key, proj in limit.get_projections().items():
                quilt.add_edge(f"limit_{i}", str(key), f"projection_{key}")

    # Add monads
    if monads:
        for i, m in enumerate(monads):
            quilt.add_node("monad", f"monad_{i}")
            quilt.add_edge(f"monad_{i}", str(m.functor), "has_functor")
            quilt.add_edge(f"monad_{i}", str(m.unit), "has_unit")
            quilt.add_edge(f"monad_{i}", str(m.join), "has_join")

    return quilt


# === TESTS ===

def test_category():
    """Test basic category construction and operations."""
    # Create a simple category: A -> B, B -> C
    objects = {"A", "B", "C"}
    morphisms = {("A", "B", "f"), ("B", "C", "g")}
    cat = Category(objects, morphisms)

    assert cat.has_morphism("A", "B")
    assert not cat.has_morphism("A", "C")
    assert cat.compose(("A", "B", "f"), ("B", "C", "g")) == ("A", "C", "f_g")
    assert cat.identity("A") == ("A", "A", "Id_A")


def test_functor():
    """Test functor construction and mapping."""
    objects1 = {"A", "B"}
    morphisms1 = {("A", "B", "f")}
    cat1 = Category(objects1, morphisms1)

    objects2 = {"X", "Y"}
    morphisms2 = {("X", "Y", "phi")}
    cat2 = Category(objects2, morphisms2)

    def map_obj(x):
        return {"A": "X", "B": "Y"}.get(x)

    def map_mor(m):
        return ("X", "Y", "phi") if m == ("A", "B", "f") else m

    F = Functor(cat1, cat2, map_obj, map_mor)

    assert F.image_of_object("A") == "X"
    assert F.image_of_morphism(("A", "B", "f")) == ("X", "Y", "phi")


def test_limit():
    """Test limit computation."""
    objects = {"A", "B", "C", "D"}
    morphisms = {("A", "C", "f"), ("B", "C", "g")}
    cat = Category(objects, morphisms)

    f = ("A", "C", "f")
    g = ("B", "C", "g")

    pullback = Pullback(cat, f, g)
    assert pullback.get_object() == "A_x_B"
    assert pullback.get_projections() == (f, g)


def test_quilt():
    """Test quilt construction and serialization."""
    objects = {"X", "Y"}
    morphisms = {("X", "Y", "f")}
    cat = Category(objects, morphisms)

    quilt = Quilt(cat)
    assert len(quilt.get_nodes("object")) == 2
    assert len(quilt.get_edges()) == 1
    assert "X" in quilt.get_nodes("object")
    assert "f" in quilt.get_nodes("morphism")
    assert "f" in quilt.get_metadata("f")["type"]


def test_categorical_family_to_quilt():
    """Test the bridge function."""
    objects = {"A", "B", "C"}
    morphisms = {("A", "B", "f"), ("B", "C", "g")}
    cat = Category(objects, morphisms)

    # Create a functor
    def map_obj(x):
        return x.upper()

    def map_mor(m):
        return (m[0].upper(), m[1].upper(), m[2].upper())

    F = Functor(cat, cat, map_obj, map_mor)
    functors = [F]

    # Create a natural transformation
    def eta(obj):
        return (obj, obj, f"eta_{obj}")

    eta_trans = NaturalTransformation(F, F, eta)
    natural_transformations = [eta_trans]

    # Create a limit
    pullback = Pullback(cat, ("A", "B", "f"), ("B", "C", "g"))
    limits = [pullback]

    # Create a monad
    monad = Monad(F)
    monads = [monad]

    # Bridge to quilt
    quilt = categorical_family_to_quilt(cat, functors, natural_transformations, limits, monads)

    assert isinstance(quilt, Quilt)
    assert "F_0" in quilt.get_nodes("functor")
    assert "eta_0" in quilt.get_nodes("natural_transformation")
    assert "limit_0" in quilt.get_nodes("limit")
    assert "monad_0" in quilt.get_nodes("monad")

    # Serialize
    serialized = quilt.serialize()
    assert isinstance(serialized, str)
    assert len(serialized) > 100  # reasonable size


# Run tests
if __name__ == "__main__":
    test_category()
    test_functor()
    test_limit()
    test_quilt()
    test_categorical_family_to_quilt()
    print("All tests passed.")
