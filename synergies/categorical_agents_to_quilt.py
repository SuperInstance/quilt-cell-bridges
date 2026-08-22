"""
categorical-agents (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance categorical-agents (Rust) treats agent composition as
category theory: agents are objects, capabilities are morphisms.

THE CRUCIAL INSIGHT: Quilt cells ARE objects in a category.
Edges ARE morphisms. Functors ARE Murmur patterns.

Map:
- Agent → cell
- Capability → cell (kind='capability')
- Composition → cell graph edge
- Functor → Murmur (inter-category mapping)
- Natural transformation → DoubleEntry (γ+η=C across categories)
- Identity morphism → Z_in
- Composition → Z_out
"""

from typing import Dict, List, Any, Optional, Callable


class Object:
    """An object in a category. A Quilt cell."""
    def __init__(self, name: str, kind: str = 'agent', gamma: float = 0.5, eta: float = 0.5):
        self.name = name
        self.kind = kind
        self.gamma = gamma
        self.eta = eta

    def __repr__(self):
        return f"Object({self.name}, {self.kind})"


class Morphism:
    """A morphism between objects. An edge in the cell graph."""
    def __init__(self, source: Object, target: Object, name: str = ''):
        self.source = source
        self.target = target
        self.name = name

    def __repr__(self):
        return f"Morphism({self.source.name} → {self.target.name})"


class Functor:
    """A functor between categories. A Murmur pattern."""
    def __init__(self, source_cat: 'Category', target_cat: 'Category', name: str = ''):
        self.source = source_cat
        self.target = target_cat
        self.name = name
        self.object_map: Dict[str, Object] = {}
        self.morphism_map: Dict[str, Morphism] = {}

    def map_object(self, obj: Object) -> Object:
        """Map an object from source to target category."""
        if obj.name not in self.object_map:
            new_obj = Object(name=f"{self.name}_{obj.name}", kind=obj.kind)
            self.object_map[obj.name] = new_obj
            self.target.add_object(new_obj)
        return self.object_map[obj.name]

    def map_morphism(self, morph: Morphism) -> Morphism:
        """Map a morphism."""
        new_source = self.map_object(morph.source)
        new_target = self.map_object(morph.target)
        new_morph = Morphism(new_source, new_target, name=f"{self.name}_{morph.name}")
        self.morphism_map[morph.name] = new_morph
        self.target.add_morphism(new_morph)
        return new_morph


class Category:
    """A category. A cell subgraph."""
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, Object] = {}
        self.morphisms: List[Morphism] = []

    def add_object(self, obj: Object) -> None:
        self.objects[obj.name] = obj

    def add_morphism(self, morph: Morphism) -> None:
        self.morphisms.append(morph)

    def identity(self, obj: Object) -> Morphism:
        """The identity morphism. Z_in."""
        morph = Morphism(obj, obj, name=f"id_{obj.name}")
        self.morphisms.append(morph)
        return morph

    def compose(self, m1: Morphism, m2: Morphism) -> Optional[Morphism]:
        """Compose two morphisms. Z_out."""
        if m1.target != m2.source:
            return None
        composed = Morphism(m1.source, m2.target, name=f"{m1.name}_then_{m2.name}")
        self.morphisms.append(composed)
        return composed


class CategoricalAgentsBridge:
    """Categorical agents implemented on Quilt cells."""

    def __init__(self):
        # The category of all agents
        self.fleet = Category('fleet')
        # Functors between categories
        self.functors: Dict[str, Functor] = {}
        # Natural transformations (γ+η=C)
        self.transformations: List[Dict[str, Any]] = []

    def add_agent(self, name: str) -> Object:
        """Add an agent as an object."""
        obj = Object(name=name, kind='agent')
        self.fleet.add_object(obj)
        return obj

    def add_capability(self, from_agent: str, to_agent: str, name: str) -> Morphism:
        """Add a capability as a morphism between agents."""
        source = self.fleet.objects.get(from_agent)
        target = self.fleet.objects.get(to_agent)
        if not source or not target:
            raise ValueError(f"Unknown agent: {from_agent} or {to_agent}")
        morph = Morphism(source, target, name=name)
        self.fleet.add_morphism(morph)
        return morph

    def create_functor(self, name: str, target: Category) -> Functor:
        """Create a functor. Murmur."""
        f = Functor(self.fleet, target, name=name)
        self.functors[name] = f
        return f

    def natural_transformation(self, f1: Functor, f2: Functor) -> Dict[str, Any]:
        """A natural transformation. DoubleEntry (γ+η=C across categories)."""
        # For each object, the components must satisfy γ+η=C
        transformation = {
            'name': f"{f1.name}_to_{f2.name}",
            'components': list(f1.object_map.keys()),
            'conservation': True,
            'gamma': 0.5,
            'eta': 0.5,
        }
        # Check conservation
        if f1.target.objects and f2.target.objects:
            g1 = sum(o.gamma for o in f1.target.objects.values())
            e1 = sum(o.eta for o in f1.target.objects.values())
            n1 = len(f1.target.objects)
            g2 = sum(o.gamma for o in f2.target.objects.values())
            e2 = sum(o.eta for o in f2.target.objects.values())
            n2 = len(f2.target.objects)
            if abs(g1 + e1 - n1) > 1e-9 or abs(g2 + e2 - n2) > 1e-9:
                transformation['conservation'] = False
        self.transformations.append(transformation)
        return transformation


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("CATEGORICAL-AGENTS ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Categorical agents on Quilt cells.")
    print("Agents = objects. Capabilities = morphisms. Functors = Murmur.")
    print()

    ca = CategoricalAgentsBridge()

    # Add agents
    search = ca.add_agent("search")
    summarize = ca.add_agent("summarize")
    act = ca.add_agent("act")

    # Add capabilities (morphisms)
    s2su = ca.add_capability("search", "summarize", "search_to_summarize")
    su2a = ca.add_capability("summarize", "act", "summarize_to_act")

    # Identity
    id_search = ca.fleet.identity(search)
    print(f"Identity: {id_search}")
    print()

    # Composition
    composed = ca.fleet.compose(s2su, su2a)
    if composed:
        print(f"Composed: {composed}")
    print()

    # Functor
    target_cat = Category("image")
    f = ca.create_functor("fleet_to_image", target_cat)
    f.map_object(search)
    f.map_object(summarize)
    print(f"Functor: {f.name}")
    print(f"Mapped objects: {list(f.object_map.keys())}")
    print()

    # Natural transformation
    if len(ca.functors) >= 1:
        target2 = Category("execution")
        f2 = ca.create_functor("fleet_to_execution", target2)
        nt = ca.natural_transformation(f, f2)
        print(f"Natural transformation: {nt}")
    print()

    # Conservation
    n = len(ca.fleet.objects)
    total = sum(o.gamma + o.eta for o in ca.fleet.objects.values())
    print(f"Conservation: {n} agents, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("Quilt cells ARE objects. Edges ARE morphisms.")
    print("Functors ARE Murmur. Compositions ARE cell graphs.")


if __name__ == "__main__":
    demo()
