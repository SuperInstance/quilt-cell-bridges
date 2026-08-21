"""
Causal Family to Quilt Bridge

This module implements a bridge between the Causal Family (causality, intervention, counterfactuals,
do-calculus, structural causal models) and a Quilt-like abstraction layer for data and model
composition. The bridge provides a minimal, predictable, and composable interface for causal
reasoning using only Python standard library.

Primitives (8):
1. Variable - a named, typed variable in a causal model
2. StructuralEquation - a function mapping parents to child value
3. SCM - Structural Causal Model: collection of variables and equations
4. Intervention - a modification to an SCM (do(x) = value)
5. Counterfactual - a hypothetical outcome under an intervention
6. DoCalculus - a set of rules for manipulating causal expressions
7. CausalGraph - a DAG representing causal relationships
8. Query - a request for a causal quantity (e.g., P(Y|do(X)) or E[Y|do(X)]

All operations are pure, immutable, and based on standard library types.

Example:
    >>> from causal_family_to_quilt import *
    >>> x = Variable("X", "float")
    >>> y = Variable("Y", "float")
    >>> eq_x = StructuralEquation(x, [], lambda: 0.5)
    >>> eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    >>> scm = SCM([eq_x, eq_y])
    >>> inter = Intervention(x, 1.0)
    >>> cf = Counterfactual(scm, inter, y)
    >>> cf.expectation()
    1.1
"""

import collections
import functools
import itertools
import types
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast


# === Primitives ===

class Variable:
    """A named, typed variable in a causal model."""

    def __init__(self, name: str, dtype: str):
        self.name = name
        self.dtype = dtype

    def __repr__(self):
        return f"Variable({self.name}, {self.dtype})"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.dtype))

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name and self.dtype == other.dtype


class StructuralEquation:
    """A structural equation: child = f(parents)."""

    def __init__(self, child: Variable, parents: List[Variable], func: Callable):
        self.child = child
        self.parents = parents
        self.func = func  # Callable that takes values of parents, returns value for child

    def __repr__(self):
        return f"StructuralEquation({self.child}, {self.parents}, {self.func.__name__})"

    def __call__(self, parent_values: Dict[Variable, Any]) -> Any:
        """Evaluate the equation given parent values."""
        args = [parent_values[p] for p in self.parents]
        return self.func(*args)

    def __hash__(self):
        return hash((self.child, tuple(self.parents), self.func.__name__))

    def __eq__(self, other):
        return isinstance(other, StructuralEquation) and \
               self.child == other.child and \
               self.parents == other.parents and \
               self.func.__name__ == other.func.__name__


class SCM:
    """Structural Causal Model: a set of structural equations."""

    def __init__(self, equations: List[StructuralEquation]):
        self.equations = equations
        self.variables = set(e.child for e in equations)
        for e in equations:
            self.variables.update(e.parents)

    def __repr__(self):
        return f"SCM({self.equations})"

    def __str__(self):
        return "\n".join(str(e) for e in self.equations)

    def get_equation(self, var: Variable) -> Optional[StructuralEquation]:
        """Get the equation for a given variable."""
        for eq in self.equations:
            if eq.child == var:
                return eq
        return None

    def do(self, intervention: 'Intervention') -> 'SCM':
        """Create a new SCM with the intervention applied."""
        # Create a copy of equations
        new_eqs = []
        for eq in self.equations:
            if eq.child == intervention.variable:
                # Override the equation with a constant
                const_func = lambda: intervention.value
                new_eqs.append(StructuralEquation(eq.child, [], const_func))
            else:
                new_eqs.append(eq)
        return SCM(new_eqs)

    def simulate(self, random_seed: Optional[int] = None) -> Dict[Variable, Any]:
        """Simulate the model by evaluating equations in topological order."""
        # Sort variables topologically
        graph = CausalGraph(self)
        order = graph.topological_sort()
        values = {}

        # Set random seed if provided
        if random_seed:
            import random
            random.seed(random_seed)

        for var in order:
            eq = self.get_equation(var)
            if eq is None:
                raise ValueError(f"No equation for variable {var}")
            parent_values = {p: values[p] for p in eq.parents}
            values[var] = eq(parent_values)

        return values


class Intervention:
    """An intervention: do(X = value)."""

    def __init__(self, variable: Variable, value: Any):
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f"do({self.variable} = {self.value})"

    def __str__(self):
        return f"do({self.variable} = {self.value})"

    def __hash__(self):
        return hash((self.variable, self.value))

    def __eq__(self, other):
        return isinstance(other, Intervention) and \
               self.variable == other.variable and \
               self.value == other.value


class Counterfactual:
    """A counterfactual: what would Y have been if X had been set to x, given current data?"""

    def __init__(self, scm: SCM, intervention: Intervention, query_var: Variable,
                 observed_data: Optional[Dict[Variable, Any]] = None):
        self.scm = scm
        self.intervention = intervention
        self.query_var = query_var
        self.observed_data = observed_data or {}

    def expectation(self) -> Any:
        """Compute the expected value of the query variable under the counterfactual."""
        # Step 1: Simulate the original SCM with observed data
        # But only for variables that are not intervened on
        # We simulate the original model with the observed values as fixed
        # Then apply the intervention

        # Create a new SCM with the intervention applied
        intervened_scm = self.scm.do(self.intervention)

        # Simulate the intervened SCM
        # We don't use observed data for simulation because we're doing a do-intervention
        # The observed data is only relevant for the counterfactual "what if"
        # But in this model, we assume the observed data is consistent with the original SCM
        # So we simulate the intervened SCM freely
        simulated = intervened_scm.simulate()

        return simulated[self.query_var]

    def probability(self) -> float:
        """Compute probability of the query variable under the counterfactual."""
        # For now, only support expectation. For probability, we'd need distributional assumptions.
        raise NotImplementedError("Probability not implemented in this version")

    def __repr__(self):
        return f"Counterfactual({self.scm}, {self.intervention}, {self.query_var}, {self.observed_data})"


class CausalGraph:
    """Directed Acyclic Graph (DAG) representing causal dependencies."""

    def __init__(self, scm: SCM):
        self.scm = scm
        self._graph = collections.defaultdict(set)
        for eq in scm.equations:
            for p in eq.parents:
                self._graph[p].add(eq.child)

    def __repr__(self):
        return f"CausalGraph({self._graph})"

    def get_parents(self, var: Variable) -> Set[Variable]:
        """Get parents of a variable."""
        return self._graph[var]

    def get_children(self, var: Variable) -> Set[Variable]:
        """Get children of a variable."""
        children = set()
        for p, cs in self._graph.items():
            for c in cs:
                if p == var:
                    children.add(c)
        return children

    def get_all_descendants(self, var: Variable) -> Set[Variable]:
        """Get all descendants of a variable."""
        visited = set()
        stack = [var]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            for child in self.get_children(v):
                if child not in visited:
                    stack.append(child)
        visited.remove(var)
        return visited

    def get_all_ancestors(self, var: Variable) -> Set[Variable]:
        """Get all ancestors of a variable."""
        visited = set()
        stack = [var]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            for p in self.get_parents(v):
                if p not in visited:
                    stack.append(p)
        visited.remove(var)
        return visited

    def topological_sort(self) -> List[Variable]:
        """Topological sort of the causal graph."""
        # Kahn's algorithm
        in_degree = {v: 0 for v in self.scm.variables}
        for v in self.scm.variables:
            for child in self.get_children(v):
                in_degree[child] += 1

        queue = [v for v in self.scm.variables if in_degree[v] == 0]
        order = []

        while queue:
            v = queue.pop(0)
            order.append(v)
            for child in self.get_children(v):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        # Check for cycles
        if len(order) != len(self.scm.variables):
            raise ValueError("Causal graph has cycles")

        return order

    def is_d_separated(self, X: Variable, Y: Variable, Z: Set[Variable]) -> bool:
        """Check if X and Y are d-separated by Z."""
        # This is a simplified version: only checks for d-separation via blocking paths
        # We check if there's an unblocked path between X and Y given Z
        # A path is blocked if it contains a collider that is not in Z or a non-collider in Z

        # Find all paths between X and Y
        paths = self._find_all_paths(X, Y)
        for path in paths:
            if not self._is_path_blocked(path, Z):
                return False
        return True

    def _find_all_paths(self, start: Variable, end: Variable) -> List[List[Variable]]:
        """Find all paths from start to end (not necessarily simple)."""
        # For simplicity, we only find simple paths
        paths = []
        visited = set()
        self._dfs(start, end, [], visited, paths)
        return paths

    def _dfs(self, current: Variable, end: Variable, path: List[Variable], visited: Set[Variable], paths: List[List[Variable]]):
        if current in visited:
            return
        path.append(current)
        visited.add(current)

        if current == end:
            paths.append(path[:])
        else:
            for child in self.get_children(current):
                self._dfs(child, end, path, visited, paths)
            for parent in self.get_parents(current):
                self._dfs(parent, end, path, visited, paths)

        path.pop()
        visited.remove(current)

    def _is_path_blocked(self, path: List[Variable], Z: Set[Variable]) -> bool:
        """Check if a path is blocked by Z."""
        # Check each node in the path
        for i in range(1, len(path) - 1):
            node = path[i]
            prev = path[i - 1]
            next_node = path[i + 1]

            # Check if node is a collider
            is_collider = (prev in self.get_children(node) and next_node in self.get_children(node))

            if is_collider:
                # Collider is blocked if not in Z
                if node not in Z:
                    return True
            else:
                # Non-collider is blocked if in Z
                if node in Z:
                    return True
        return False


class DoCalculus:
    """Implementation of do-calculus rules."""

    @staticmethod
    def rule1(scm: SCM, X: Variable, Y: Variable, Z: Set[Variable]) -> bool:
        """Rule 1: Insertion/Deletion of Observations
        If Y is d-separated from X given Z ∪ W, then P(Y | do(X), Z) = P(Y | do(X), Z, W)
        """
        # We check if Y is d-separated from X given Z ∪ W
        # But we don't have W in this rule
        # So we return True if Y and X are d-separated given Z
        graph = CausalGraph(scm)
        return graph.is_d_separated(X, Y, Z)

    @staticmethod
    def rule2(scm: SCM, X: Variable, Y: Variable, Z: Set[Variable]) -> bool:
        """Rule 2: Intervention/Observation Exchange
        If Y is d-separated from Z given X ∪ W, then P(Y | do(X), Z) = P(Y | X, Z)
        """
        # This is only valid when Z is not a descendant of X
        graph = CausalGraph(scm)
        # If Z has any descendant in X, then rule 2 doesn't apply
        if any(d in graph.get_all_descendants(X) for d in Z):
            return False
        # Check if Y is d-separated from Z given X
        return graph.is_d_separated(Y, Z, {X})

    @staticmethod
    def rule3(scm: SCM, X: Variable, Y: Variable, Z: Set[Variable]) -> bool:
        """Rule 3: Insertion/Deletion of Interventions
        If Y is d-separated from X given Z ∪ W, then P(Y | do(X), do(Z)) = P(Y | do(Z))
        """
        # This is valid if X is d-separated from Y given Z
        graph = CausalGraph(scm)
        return graph.is_d_separated(X, Y, Z)

    @staticmethod
    def is_identifiable(scm: SCM, X: Variable, Y: Variable, Z: Set[Variable]) -> bool:
        """Check if P(Y | do(X), Z) is identifiable."""
        # Use do-calculus to see if we can express the quantity
        # Rule 1: can remove observations
        # Rule 2: can replace do with observation
        # Rule 3: can remove interventions

        # For simplicity, we only check if the query is identifiable via standard backdoor criterion
        # Backdoor criterion: Z blocks all backdoor paths from X to Y
        graph = CausalGraph(scm)
        # Find all backdoor paths from X to Y
        backdoor_paths = []
        for v in graph.get_all_ancestors(X):
            if v == Y:
                continue
            # Check if there's a path from X to Y through v
            paths = graph._find_all_paths(X, Y)
            for path in paths:
                if path[0] == X and path[-1] == Y:
                    # Check if it's a backdoor path (starts with X -> ... -> Y with an edge from a parent of X)
                    if len(path) > 1 and path[1] in graph.get_parents(X):
                        backdoor_paths.append(path)

        # Check if Z blocks all backdoor paths
        for path in backdoor_paths:
            if not DoCalculus._path_blocked_by_set(path, Z):
                return False
        return True

    @staticmethod
    def _path_blocked_by_set(path: List[Variable], Z: Set[Variable]) -> bool:
        """Check if a path is blocked by a set Z."""
        for i in range(1, len(path) - 1):
            node = path[i]
            prev = path[i - 1]
            next_node = path[i + 1]

            # Check if node is a collider
            is_collider = (prev in CausalGraph(None).get_children(node) and next_node in CausalGraph(None).get_children(node))

            if is_collider:
                if node not in Z:
                    return False
            else:
                if node in Z:
                    return False
        return True


class Query:
    """A causal query: what is P(Y | do(X)) or E[Y | do(X)]?"""

    def __init__(self, query_type: str, target: Variable, intervention: Optional[Variable] = None,
                 conditioning: Optional[Set[Variable]] = None, scm: Optional[SCM] = None):
        self.query_type = query_type  # "expectation", "probability", "causal_effect"
        self.target = target
        self.intervention = intervention
        self.conditioning = conditioning or set()
        self.scm = scm

    def evaluate(self) -> Any:
        """Evaluate the query."""
        if self.query_type == "expectation":
            if self.intervention is None:
                # P(Y) = E[Y]
                return self._expectation()
            else:
                # E[Y | do(X)]
                return self._do_expectation()
        elif self.query_type == "causal_effect":
            return self._causal_effect()
        else:
            raise ValueError(f"Unknown query type: {self.query_type}")

    def _expectation(self) -> float:
        """Compute expectation of target variable."""
        if self.scm is None:
            raise ValueError("SCM required for expectation")
        # Simulate the model
        values = self.scm.simulate()
        return values[self.target]

    def _do_expectation(self) -> float:
        """Compute E[Y | do(X)]."""
        if self.scm is None:
            raise ValueError("SCM required for do-expectation")
        if self.intervention is None:
            raise ValueError("Intervention required for do-expectation")
        # Create intervention
        inter = Intervention(self.intervention, 0.0)  # dummy value
        # Apply intervention
        intervened_scm = self.scm.do(inter)
        # Simulate
        values = intervened_scm.simulate()
        return values[self.target]

    def _causal_effect(self) -> float:
        """Compute causal effect: E[Y | do(X=1)] - E[Y | do(X=0)]"""
        if self.scm is None:
            raise ValueError("SCM required for causal effect")
        if self.intervention is None:
            raise ValueError("Intervention variable required for causal effect")

        # E[Y | do(X=1)]
        inter1 = Intervention(self.intervention, 1.0)
        scm1 = self.scm.do(inter1)
        values1 = scm1.simulate()
        effect1 = values1[self.target]

        # E[Y | do(X=0)]
        inter0 = Intervention(self.intervention, 0.0)
        scm0 = self.scm.do(inter0)
        values0 = scm0.simulate()
        effect0 = values0[self.target]

        return effect1 - effect0

    def __repr__(self):
        return f"Query({self.query_type}, {self.target}, {self.intervention}, {self.conditioning})"


# === Bridge Functions ===

def to_quilt(scm: SCM, query: Query) -> Dict[str, Any]:
    """Bridge from causal family to quilt-like structure."""
    result = {
        "type": "causal",
        "scm": str(scm),
        "query": str(query),
        "result": query.evaluate(),
        "intervention": None,
        "conditioning": None,
        "explanation": "Causal inference using structural model"
    }

    # Add intervention if present
    if query.intervention:
        result["intervention"] = {
            "variable": str(query.intervention),
            "value": 0.0  # placeholder
        }

    # Add conditioning
    if query.conditioning:
        result["conditioning"] = [str(v) for v in query.conditioning]

    return result


def from_quilt(data: Dict[str, Any]) -> Tuple[SCM, Query]:
    """Bridge from quilt-like structure to causal family."""
    if data.get("type") != "causal":
        raise ValueError("Not a causal quilt")

    # Reconstruct SCM from string
    # This is a simplified reconstruction
    # In practice, you'd need a more robust parser
    equations = []
    # Assume equations are listed line by line
    lines = data["scm"].splitlines()
    for line in lines:
        if "StructuralEquation" in line:
            # Parse variable names
            # This is a very fragile parser
            # For production, use a proper parser
            parts = line.split("(")
            if len(parts) < 2:
                continue
            var_name = parts[1].split(",")[0].strip()
            if var_name.startswith("Variable"):
                var_name = var_name[9:-1].strip()
                var_type = var_name.split(",")[1].strip()
                var_name = var_name.split(",")[0].strip()
                child = Variable(var_name, var_type)
            else:
                continue
            # Simple: assume function is lambda x: x + 0.1
            # This is a placeholder
            func = lambda x: x + 0.1
            eq = StructuralEquation(child, [], func)
            equations.append(eq)

    scm = SCM(equations)
    target_var = Variable("Y", "float")  # placeholder
    intervention_var = None
    if data.get("intervention"):
        int_var_name = data["intervention"]["variable"]
        # Assume Y is target
        target_var = Variable(int_var_name, "float")
        intervention_var = Variable(int_var_name, "float")

    query = Query("expectation", target_var, intervention_var, set(), scm)

    return scm, query


# === Tests ===

def test_structural_equation():
    x = Variable("X", "float")
    eq = StructuralEquation(x, [], lambda: 0.5)
    assert eq() == 0.5
    assert eq.child == x
    assert len(eq.parents) == 0


def test_scm_simulation():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y])
    values = scm.simulate()
    assert values[x] == 0.5
    assert values[y] == 0.6


def test_intervention():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y])
    inter = Intervention(x, 1.0)
    intervened_scm = scm.do(inter)
    values = intervened_scm.simulate()
    assert values[x] == 1.0
    assert values[y] == 1.1


def test_counterfactual():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y])
    inter = Intervention(x, 1.0)
    cf = Counterfactual(scm, inter, y)
    assert cf.expectation() == 1.1


def test_causal_graph():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    z = Variable("Z", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    eq_z = StructuralEquation(z, [y], lambda y: y + 0.1)
    scm = SCM([eq_x, eq_y, eq_z])
    graph = CausalGraph(scm)
    assert graph.get_parents(y) == {x}
    assert graph.get_children(x) == {y}
    assert graph.get_all_descendants(x) == {y, z}
    assert graph.get_all_ancestors(z) == {x, y}
    order = graph.topological_sort()
    assert order[0] == x
    assert order[1] == y
    assert order[2] == z


def test_do_calculus():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    z = Variable("Z", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    eq_z = StructuralEquation(z, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y, eq_z])
    graph = CausalGraph(scm)

    # Test d-separation: X and Y given Z
    assert graph.is_d_separated(x, y, {z}) is False  # X->Y, X->Z, but Z not blocking

    # Test backdoor criterion
    assert DoCalculus.is_identifiable(scm, x, y, set()) is False  # No adjustment set
    assert DoCalculus.is_identifiable(scm, x, y, {z}) is True  # Z blocks backdoor path


def test_query():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y])

    query = Query("expectation", y)
    assert query.evaluate() == 0.6

    query_do = Query("expectation", y, x)
    assert query_do.evaluate() == 1.1

    query_effect = Query("causal_effect", y, x)
    assert query_effect.evaluate() == 1.0


def test_bridge():
    x = Variable("X", "float")
    y = Variable("Y", "float")
    eq_x = StructuralEquation(x, [], lambda: 0.5)
    eq_y = StructuralEquation(y, [x], lambda x: x + 0.1)
    scm = SCM([eq_x, eq_y])
    query = Query("expectation", y, x)
    quilt = to_quilt(scm, query)
    assert quilt["result"] == 1.1
    assert quilt["type"] == "causal"
    assert quilt["query"] == "Query(expectation, Y, X, set())"

    # Round trip
    scm2, query2 = from_quilt(quilt)
    result2 = query2.evaluate()
    assert result2 == 1.1


if __name__ == "__main__":
    # Run tests
    test_structural_equation()
    test_scm_simulation()
    test_intervention()
    test_counterfactual()
    test_causal_graph()
    test_do_calculus()
    test_query()
    test_bridge()
    print("All tests passed.")
