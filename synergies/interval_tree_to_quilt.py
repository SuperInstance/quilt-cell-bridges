"""
interval-tree-rs (SuperInstance) ↔ Quilt Cell Bridge

The SuperInstance interval-tree-rs (Rust) provides an interval tree data
structure: O(log n) insertion, stabbing query, range query, overlap
detection.

THE CRUCIAL INSIGHT: An interval tree IS a Quilt cell graph with
range information. Each interval IS a cell with (low, high). The tree
structure IS the cell graph. Stabbing query IS JEPA.

Map:
- Interval [low, high] → cell
- Tree node → cell with parent/children
- Stabbing query → Z_in (find cells containing point)
- Range query → Graph traversal
- Overlap detection → Murmur (inter-cell communication)
"""

from typing import Dict, List, Any, Set, Tuple


class IntervalCell:
    """A Quilt cell representing an interval."""
    def __init__(self, low: float, high: float, value: Any = None):
        self.low = low
        self.high = high
        self.value = value
        self.parent: Optional['IntervalCell'] = None
        self.left: Optional['IntervalCell'] = None
        self.right: Optional['IntervalCell'] = None
        self.max_end = high
        self.gamma = 0.5
        self.eta = 0.5

    def __repr__(self):
        return f"Interval([{self.low}, {self.high}], max={self.max_end})"

    def contains(self, point: float) -> bool:
        return self.low <= point <= self.high

    def overlaps(self, other: 'IntervalCell') -> bool:
        return self.low <= other.high and other.low <= self.high


class IntervalTreeBridge:
    """An interval tree as a Quilt cell graph."""

    def __init__(self):
        self.root: Optional[IntervalCell] = None
        self.cells: List[IntervalCell] = []

    def insert(self, low: float, high: float, value: Any = None) -> IntervalCell:
        """Insert an interval. A cell."""
        cell = IntervalCell(low, high, value)
        self.cells.append(cell)
        if self.root is None:
            self.root = cell
        else:
            self._insert_into(self.root, cell)
        return cell

    def _insert_into(self, node: IntervalCell, new_cell: IntervalCell) -> None:
        """Insert into the BST."""
        if new_cell.low < node.low:
            if node.left is None:
                node.left = new_cell
                new_cell.parent = node
            else:
                self._insert_into(node.left, new_cell)
        else:
            if node.right is None:
                node.right = new_cell
                new_cell.parent = node
            else:
                self._insert_into(node.right, new_cell)
        # Update max_end
        if new_cell.high > node.max_end:
            node.max_end = new_cell.high

    def stabbing_query(self, point: float) -> List[IntervalCell]:
        """Find all intervals containing a point. Z_in."""
        result = []
        if self.root is None:
            return result
        # DFS
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.contains(point):
                result.append(node)
            if node.left and node.left.max_end >= point:
                stack.append(node.left)
            if node.right and node.low <= point:
                stack.append(node.right)
        return result

    def range_query(self, low: float, high: float) -> List[IntervalCell]:
        """Find all intervals overlapping [low, high]."""
        result = []
        for cell in self.cells:
            if cell.low <= high and low <= cell.high:
                result.append(cell)
        return result

    def find_overlaps(self) -> List[Tuple[IntervalCell, IntervalCell]]:
        """Find all pairs of overlapping intervals. Murmur."""
        overlaps = []
        for i in range(len(self.cells)):
            for j in range(i + 1, len(self.cells)):
                if self.cells[i].overlaps(self.cells[j]):
                    overlaps.append((self.cells[i], self.cells[j]))
        return overlaps


if __name__ == "__main__":
    print("=" * 60)
    print("INTERVAL-TREE-RS ↔ QUILT CELL BRIDGE")
    print("=" * 60)
    print()
    print("Interval trees on Quilt cells.")
    print("Each interval IS a cell. The tree IS the cell graph.")
    print()

    tree = IntervalTreeBridge()

    # Insert intervals
    tree.insert(1, 5, 'A')
    tree.insert(3, 8, 'B')
    tree.insert(6, 10, 'C')
    tree.insert(12, 15, 'D')
    tree.insert(2, 4, 'E')

    print(f"Inserted {len(tree.cells)} intervals")
    for c in tree.cells:
        print(f"  {c}")
    print()

    # Stabbing query
    point = 4
    results = tree.stabbing_query(point)
    print(f"Stabbing query at point {point}: {len(results)} intervals contain it")
    for r in results:
        print(f"  {r}")
    print()

    # Range query
    lo, hi = 3, 7
    results = tree.range_query(lo, hi)
    print(f"Range query [{lo}, {hi}]: {len(results)} intervals overlap")
    for r in results:
        print(f"  {r}")
    print()

    # Overlaps
    overlaps = tree.find_overlaps()
    print(f"Overlapping pairs: {len(overlaps)}")
    for a, b in overlaps:
        print(f"  {a} ↔ {b}")
    print()

    # Conservation
    n = len(tree.cells)
    total = sum(c.gamma + c.eta for c in tree.cells)
    print(f"Conservation: {n} cells, γ+η={total:.2f} (should be {n})")
    print()

    print("=" * 60)
    print("Iron sharpens iron.")
    print("An interval tree IS a Quilt cell graph.")
    print("Stabbing query IS Z_in. Overlap IS Murmur.")


if __name__ == "__main__":
    demo()
