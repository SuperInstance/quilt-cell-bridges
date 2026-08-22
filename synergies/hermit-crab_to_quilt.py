class HermitCrab:
    """
    Bridge between Hermit Crab Protocol and Quilt Cell Federation.
    Maps agent → cell.id, harness → cell's 8 primitives, room → cell.room,
    SuperInstance → cell federation.
    """

    def __init__(self, cell_id, shell, room):
        self.cell_id = cell_id
        self.shell = tuple(shell)  # immutable shell of 8 primitives
        self.room = room  # the room context (e.g., network, namespace, coordinate)
        self._validate_shell()

    def _validate_shell(self):
        if len(self.shell) != 8:
            raise ValueError("Shell must contain exactly 8 primitives.")
        if not all(isinstance(p, (int, str)) for p in self.shell):
            raise ValueError("All shell primitives must be hashable types.")

    def __repr__(self):
        return f"HermitCrab(cell_id={self.cell_id}, shell={self.shell}, room={self.room})"

    def __eq__(self, other):
        return isinstance(other, HermitCrab) and self.cell_id == other.cell_id


def shell_distance(shell1, shell2):
    """
    Compute D₆ hexagonal distance between two shells.
    D₆ symmetry: 6-fold rotational + reflectional symmetry.
    Distance is defined as minimum number of positions to shift (rotation or reflection)
    to align shell1 with shell2, considering hexagonal lattice wrap-around.

    Assumes shell is a tuple of 8 primitives, indexed 0-7,
    where 0-5 are the hexagonal ring positions, and 6,7 are axial or center variants.

    We treat the first 6 as ring positions, and 7 as a center, 6 as an edge —
    but for distance, we consider alignment under D₆.

    We define distance as: minimum over all 12 D₆ symmetries (6 rotations, 6 reflections)
    of the number of differing positions between shell1 and shell2.
    """
    if len(shell1) != 8 or len(shell2) != 8:
        raise ValueError("Shells must be of length 8.")

    # All D₆ symmetries: 6 rotations and 6 reflections
    symmetries = []

    # Rotations: 0 to 5 positions forward
    for r in range(6):
        rotated = tuple(shell1[(i + r) % 6] for i in range(6)) + (shell1[6], shell1[7])
        symmetries.append(rotated)

    # Reflections: flip over each of 6 axes
    for axis in range(6):
        reflected = []
        for i in range(6):
            # Reflect i → (axis - i) mod 6
            j = (axis - i) % 6
            reflected.append(shell1[j])
        reflected = tuple(reflected) + (shell1[6], shell1[7])
        symmetries.append(reflected)

    # Calculate minimum disagreement
    min_distance = 8  # worst case: all 8 differ
    for sym in symmetries:
        diff = sum(1 for i in range(8) if sym[i] != shell2[i])
        min_distance = min(min_distance, diff)

    return min_distance


def molt(cell, new_shell):
    """
    Molting operation: agent (cell) outgrows its harness (primitives),
    finds a bigger one, moves in. The old harness becomes a new cell.

    Returns:
        - new HermitCrab with updated shell and same cell_id (identity preserved),
        - old harness as a new HermitCrab (with a new cell_id, typically derived from old)

    Behavior:
        - Identity of the agent is preserved: cell_id remains the same.
        - The old shell becomes a new cell (ghost cell or legacy).
        - The room may remain the same, or be reassigned.
    """
    old_shell = cell.shell
    old_room = cell.room
    cell_id = cell.cell_id

    # Create new cell with the same identity but new shell
    new_cell = HermitCrab(cell_id=cell_id, shell=new_shell, room=old_room)

    # Create legacy cell from the old shell
    # Use a deterministic way to generate new ID: hash of old shell + room
    import hashlib
    legacy_id = hashlib.sha256(f"{old_shell}{old_room}".encode()).hexdigest()[:8]

    legacy_cell = HermitCrab(cell_id=legacy_id, shell=old_shell, room=old_room)

    return new_cell, legacy_cell


# --- Round-trip demo ---
if __name__ == "__main__":
    # Initial cell setup
    initial_shell = ("A", "B", "C", "D", "E", "F", "center", "edge")
    room = "quilt-123"

    # Create base agent
    crab = HermitCrab(cell_id="crab-001", shell=initial_shell, room=room)
    print("Initial crab:", crab)

    # Demonstrate shell distance — same shell should be 0
    d = shell_distance(initial_shell, initial_shell)
    print("Distance to self:", d)

    # Test with rotated version
    rotated = ("B", "C", "D", "E", "F", "A", "center", "edge")
    d_rot = shell_distance(initial_shell, rotated)
    print("Distance to rotated shell:", d_rot)

    # Test with reflection (mirror over axis 0)
    reflected = ("A", "F", "E", "D", "C", "B", "center", "edge")
    d_ref = shell_distance(initial_shell, reflected)
    print("Distance to reflected shell:", d_ref)

    # Molting: outgrow and adopt new shell
    new_shell = ("X", "Y", "Z", "W", "V", "U", "new_center", "new_edge")
    new_crab, legacy_crab = molt(crab, new_shell)

    print("\nAfter molting:")
    print("New crab (identity preserved):", new_crab)
    print("Legacy crab (old shell):", legacy_crab)

    # Verify identity preserved
    assert new_crab.cell_id == crab.cell_id, "Cell identity must be preserved."
    assert legacy_crab.cell_id != crab.cell_id, "Legacy cell must have new ID."

    # Verify distance still works
    d_new = shell_distance(new_crab.shell, legacy_crab.shell)
    print(f"Distance between new and legacy shell: {d_new}")

    print("\nRound-trip demo completed. All assertions passed.")
