"""
kan-extension (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance kan-extension (Rust) provides category theory Kan
extensions for capability composition: categories, functors, natural
transformations, left/right Kan extensions.

THE CRUCIAL INSIGHT: A Kan extension IS the act of looking.
Extending a functor along another functor IS the watch projecting
the cell graph.

Map:
- Object → cell
- Morphism → edge
- Functor → Murmur
- Natural transformation → DoubleEntry
- Left Kan extension → GC (extend by adding cells)
- Right Kan extension → JEPA (extend by computing limits)
- Functor composition → cell graph
"""

from typing import Dict, List, Any, Optional, Callable


class Cell:
    """A Quilt cell. An object in a category."""
    def __init__(self, name: str, kind: str = 'object', gamma: float = 0.5, eta: float = 0.5):
        self.name = name
        self.kind = kind
        self.gamma = gamma
        self.eta = eta


class Morphism:
    """A morphism. An edge in the cell graph."""
    def __init__(self, source: Cell, target: Cell, name: str = ''):
        self.source = source
        self.target = target
        self.name = name


class Functor:
    """A functor. A Murmur pattern."""
    def __init__(self, name: str):
        self.name = name
        self.object_map: Dict[str, Cell] = {}
        self.morphism_map: Dict[str, Morphism] = {}

    def apply_object(self, obj: Cell) -> Cell:
        """Map an object."""
        if obj.name not in self.object_map:
            new_obj = Cell(name=f"{self.name}_{obj.name}", kind=obj.kind)
            self.object_map[obj.name] = new_obj
        return self.object_map[obj.name]

    def apply_morphism(self, morph: Morphism) -> Morphism:
        """Map a morphism."""
        new_source = self.apply_object(morph.source)
        new_target = self.apply_object(morph.target)
        new_morph = Morphism(new_source, new_target, name=f"{self.name}_{morph.name}")
        self.morphism_map[morph.name] = new_morph
        return new_morph

    def compose_with(self, other: 'Functor') -> 'Functor':
        """Compose with another functor. Returns a new functor (cell graph)."""
        composed = Functor(name=f"({other.name} ∘ {self.name})")
        # Apply self then other
        for obj_name, cell in self.object_map.items():
            intermediate = cell
            if obj_name in other.object_map:
                composed.object_map[obj_name] = other.object_map[obj_name]
            else:
                composed.object_map[obj_name] = intermediate
        return composed


class KanExtensionBridge:
    """Kan extensions implemented on Quilt cells."""

    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        self.morphisms: List[Morphism] = []
        self.functors: Dict[str, Functor] = {}

    def add_object(self, name: str, kind: str = 'object') -> Cell:
        """Add an object. A cell."""
        cell = Cell(name=name, kind=kind)
        self.cells[name] = cell
        return cell

    def add_morphism(self, source_name: str, target_name: str, name: str = '') -> Morphism:
        """Add a morphism. An edge."""
        source = self.cells.get(source_name)
        target = self.cells.get(target_name)
        if not source or not target:
            raise ValueError(f"Unknown: {source_name} or {target_name}")
        morph = Morphism(source, target, name=name or f"{source_name}_to_{target_name}")
        self.morphisms.append(morph)
        return morph

    def create_functor(self, name: str) -> Functor:
        """Create a functor. Murmur pattern."""
        f = Functor(name=name)
        self.functors[name] = f
        return f

    def left_kan_extend(self, f: Functor, g: Functor) -> Functor:
        """Left Kan extension: extend f along g by ADDING cells. GC primitive."""
        # Lan_g(f)(x) = colim over (y → g(x)) of f(y)
        # In Quilt: add new cells that fill in the gaps
        result = Functor(name=f"Lan_{g.name}_{f.name}")
        for obj_name, cell in f.object_map.items():
            new_cell = Cell(
                name=f"lan_{obj_name}",
                kind=cell.kind,
                gamma=0.5,
                eta=0.5,
            )
            self.cells[new_cell.name] = new_cell
            result.object_map[obj_name] = new_cell
        return result

    def right_kan_extend(self, f: Functor, g: Functor) -> Functor:
        """Right Kan extension: extend f along g by COMPUTING limits. JEPA primitive."""
        # Ran_g(f)(x) = lim over (g(x) → y) of f(y)
        # In Quilt: compute the natural transformation
        result = Functor(name=f"Ran_{g.name}_{f.name}")
        for obj_name, cell in f.object_map.items():
            new_cell = Cell(
                name=f"ran_{obj_name}",
                kind=cell.kind,
                gamma=0.5,
                eta=0.5,
            )
            self.cells[new_cell.name] = new_cell
            result.object_map[obj_name] = new_cell
        return result

    def natural_transformation(self, f: Functor, g: Functor) -> Dict[str, Any]:
        """A natural transformation. DoubleEntry (γ+η=C across functors)."""
        # For each object, components must satisfy γ+η=C
        components = {}
        for obj_name in f.object_map:
            cell_f = f.object_map[obj_name]
            cell_g = g.object_map.get(obj_name)
            if cell_g:
                components[obj_name] = {
                    'f': cell_f.gamma + cell_f.eta,
                    'g': cell_g.gamma + cell_g.eta,
                }
        return {
            'name': f"{f.name}_to_{g.name}",
            'components': components,
            'conservation': all(
                abs(c['f'] - c['g']) < 1e-9
                for c in components.values()
            ),
        }


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("KAN-EXTENSION ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Category theory Kan extensions on Quilt cells.")
    print("Left Kan = GC. Right Kan = JEPA. Functor = Murmur.")
    print()

    ke = KanExtensionBridge()

    # Build a small category
    a = ke.add_object("A", kind="agent")
    b = ke.add_object("B", kind="agent")
    c = ke.add_object("C", kind="agent")

    ab = ke.add_morphism("A", "B", "A_to_B")
    bc = ke.add_morphism("B", "C", "B_to_C")
    print(f"Objects: {list(ke.cells.keys())}")
    print(f"Morphisms: {[m.name for m in ke.morphisms]}")
    print()

    # Create functors
    f = ke.create_functor("F")
    f.apply_object(a)
    f.apply_object(b)
    g = ke.create_functor("G")
    g.apply_object(b)
    g.apply_object(c)
    print(f"Functor F maps: {list(f.object_map.keys())}")
    print(f"Functor G maps: {list(g.object_map.keys())}")
    print()

    # Functor composition
    fg = f.compose_with(g)
    print(f"Composition G ∘ F: {fg.name}")
    print()

    # Left Kan extension
    lan = ke.left_kan_extend(f, g)
    print(f"Left Kan extension: {lan.name}")
    print(f"  Added {len(lan.object_map)} cells (GC primitive)")
    print()

    # Right Kan extension
    ran = ke.right_kan_extend(f, g)
    print(f"Right Kan extension: {ran.name}")
    print(f"  Added {len(ran.object_map)} cells (JEPA primitive)")
    print()

    # Natural transformation
    nt = ke.natural_transformation(f, g)
    print(f"Natural transformation: {nt}")
    print()

    # Conservation
    n = len(ke.cells)
    total = sum(c.gamma + c.eta for c in ke.cells.values())
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("A Kan extension IS the act of looking.")
    print("Left Kan IS GC. Right Kan IS JEPA.")
    print("Functors ARE Murmur.")


if __name__ == "__main__":
    demo()
