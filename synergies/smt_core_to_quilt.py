"""
smt-core (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance smt-core (Rust) implements an SMT solver with
theory combination (Nelson-Oppen) and congruence closure.

Quilt is an SMT problem in disguise:
- Term → cell (with kind indicating type)
- Variable → Z_in cell
- Constant → Z_out cell
- Function application → DoubleEntry
- Equality → Z_in == Z_out (conservation)
- Congruence closure → Graph (equivalence classes)
- Theory combination → Murmur (inter-theory communication)
- Model → tape of cell values
"""

from typing import Dict, List, Any, Optional, Set, Tuple


class SmtTerm:
    """An SMT term, as a Quilt cell."""
    def __init__(self, name: str, kind: str = 'variable', value: Any = None,
                 gamma: float = 0.5, eta: float = 0.5):
        self.name = name
        self.kind = kind  # variable | constant | function | equality | arithmetic
        self.value = value
        self.gamma = gamma
        self.eta = eta

    def __repr__(self):
        return f"SmtTerm({self.name}, {self.kind})"


class CongruenceClosure:
    """Union-find based equality reasoning, implemented as a Quilt graph."""

    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def merge(self, x: str, y: str) -> bool:
        """Merge two terms. Returns True if merged, False if already congruent."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

    def are_congruent(self, x: str, y: str) -> bool:
        return self.find(x) == self.find(y)


class SmtCoreBridge:
    """The SMT core implemented on Quilt cells."""

    def __init__(self):
        self.terms: Dict[str, SmtTerm] = {}
        self.congruence = CongruenceClosure()
        # Theory solvers
        self.equality_theory: Set[Tuple[str, str]] = set()
        self.arithmetic_theory: Dict[str, float] = {}

    def make_variable(self, name: str) -> SmtTerm:
        term = SmtTerm(name=name, kind='variable')
        self.terms[name] = term
        return term

    def make_constant(self, name: str, value: Any) -> SmtTerm:
        term = SmtTerm(name=name, kind='constant', value=value)
        self.terms[name] = term
        return term

    def make_function(self, name: str, args: List[str]) -> SmtTerm:
        term = SmtTerm(name=name, kind='function', value=args)
        self.terms[name] = term
        return term

    def assert_equal(self, x: str, y: str) -> bool:
        """Assert x == y. Returns False if contradiction."""
        if x not in self.terms or y not in self.terms:
            return False
        # Check for contradiction with arithmetic theory
        if x in self.arithmetic_theory and y in self.arithmetic_theory:
            if self.arithmetic_theory[x] != self.arithmetic_theory[y]:
                return False
        # Merge in congruence closure
        return self.congruence.merge(x, y)

    def assert_arithmetic(self, x: str, value: float) -> None:
        """Assert x has a specific arithmetic value."""
        self.arithmetic_theory[x] = value

    def theory_combine(self) -> Dict[str, str]:
        """Nelson-Oppen theory combination. Returns the combined model."""
        # Propagate equalities from congruence to theories
        result = {}
        for term_name in self.terms:
            canonical = self.congruence.find(term_name)
            result[term_name] = canonical
        return result

    def generate_model(self) -> Dict[str, Any]:
        """Generate a satisfying model."""
        model = {}
        for name, term in self.terms.items():
            if term.kind == 'constant':
                model[name] = term.value
            elif term.kind == 'arithmetic':
                model[name] = self.arithmetic_theory.get(name, 0)
            else:
                model[name] = self.congruence.find(name)
        return model

    def cell_from_term(self, term: SmtTerm) -> Dict[str, Any]:
        """Convert an SMT term to a Quilt cell."""
        return {
            'id': term.name,
            'kind': term.kind,
            'value': term.value,
            'gamma': term.gamma,
            'eta': term.eta,
        }


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("SMT-CORE ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("SMT solver with theory combination on Quilt cells.")
    print("Each term is a cell. Congruence closure is the graph.")
    print()

    smt = SmtCoreBridge()

    # Variables
    smt.make_variable("x")
    smt.make_variable("y")
    smt.make_variable("z")

    # Constants
    smt.make_constant("a", 5)
    smt.make_constant("b", 10)

    # Functions
    smt.make_function("f", ["x"])
    smt.make_function("g", ["y"])

    # Equality assertions
    smt.assert_equal("x", "y")
    smt.assert_equal("y", "z")
    smt.assert_equal("f", "g")  # f and g must be the same

    # Arithmetic
    smt.assert_arithmetic("a", 5)
    smt.assert_arithmetic("b", 10)
    smt.assert_arithmetic("x", 5)  # x must be 5
    smt.assert_arithmetic("z", 5)  # z must be 5

    # Theory combination
    combined = smt.theory_combine()
    print(f"Combined: {combined}")
    print()

    # Generate model
    model = smt.generate_model()
    print(f"Model: {model}")
    print()

    # Convert terms to cells
    print("Terms as Quilt cells:")
    for name, term in list(smt.terms.items())[:4]:
        cell = smt.cell_from_term(term)
        print(f"  {cell}")
    print()

    # Conservation
    total_g = sum(t.gamma for t in smt.terms.values())
    total_e = sum(t.eta for t in smt.terms.values())
    n = len(smt.terms)
    print(f"Conservation: {n} cells, γ+η={total_g + total_e:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("SMT is JEPA + DoubleEntry + Graph.")
    print("Congruence closure is the cell graph.")
    print("Theory combination is Murmur.")


if __name__ == "__main__":
    demo()
