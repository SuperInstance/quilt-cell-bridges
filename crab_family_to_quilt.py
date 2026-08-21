"""
Crab Family to Quilt Bridge
===========================

This bridge translates the crab family substrate (crab-traps, hermit-crab, fiddler, blue-swimmer, ghost)
into a quilt pattern representation. Each crab type maps to a specific geometric tile with unique
color, shape, and orientation rules.

The substrate defines:
- crab-traps: 4-pointed star, red, 0° rotation
- hermit-crab: spiral, blue, 45° rotation
- fiddler: asymmetrical claw, green, 0° rotation
- blue-swimmer: fish-like, cyan, 90° rotation
- ghost: translucent oval, white, 0° rotation

The quilt is a 2D grid where each cell contains one tile. Quilt patterns are generated
by mapping crab types to tiles using a simple coordinate-based rule system.

This module provides:
- Tile definitions (class-based)
- Coordinate system (x, y, z) for hexagonal layout
- Mapping functions from crab types to quilt tiles
- Pattern generators (random, spiral, wave)
- Export to JSON format
- Validation and testing

Dependencies: Only stdlib (json, random, math, copy)
"""

import json
import random
import math
from typing import List, Dict, Tuple, Optional, Set, Any
from copy import deepcopy

# === PRIMITIVE TYPES ===

# Tile: represents a single quilt element
class Tile:
    """Represents a geometric tile with shape, color, and orientation."""
    
    def __init__(self, crab_type: str, x: int, y: int, rotation: float = 0.0):
        self.crab_type = crab_type  # one of: crab-traps, hermit-crab, fiddler, blue-swimmer, ghost
        self.x = x
        self.y = y
        self.rotation = rotation % 360.0  # normalize to [0, 360)
        
        # Define shape and color per crab type
        self.shape = {
            "crab-traps": "star",
            "hermit-crab": "spiral",
            "fiddler": "claw",
            "blue-swimmer": "fish",
            "ghost": "oval"
        }.get(crab_type, "unknown")
        
        self.color = {
            "crab-traps": "red",
            "hermit-crab": "blue",
            "fiddler": "green",
            "blue-swimmer": "cyan",
            "ghost": "white"
        }.get(crab_type, "gray")
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "crab_type": self.crab_type,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "shape": self.shape,
            "color": self.color
        }
    
    def __repr__(self):
        return f"Tile({self.crab_type}, ({self.x},{self.y}), {self.rotation}°)"

# Coordinate system: axial coordinates for hex grid
class HexCoord:
    """Axial coordinate system for hexagonal grid layout."""
    
    def __init__(self, q: int, r: int):
        self.q = q  # column
        self.r = r  # row
        self.s = -q - r  # implied third axis
    
    def neighbors(self) -> List['HexCoord']:
        """Return 6 adjacent hexes."""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [HexCoord(self.q + dq, self.r + dr) for dq, dr in directions]
    
    def distance_to(self, other: 'HexCoord') -> int:
        """Manhattan distance in hex grid."""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2
    
    def to_cartesian(self, size: float = 1.0) -> Tuple[float, float]:
        """Convert axial to Cartesian coordinates."""
        x = size * (self.q + self.r / 2.0)
        y = size * (math.sqrt(3) / 2.0) * self.r
        return (x, y)
    
    def __eq__(self, other):
        return isinstance(other, HexCoord) and self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __repr__(self):
        return f"HexCoord({self.q}, {self.r})"

# === BRIDGE CORE ===

class CrabFamilyToQuilt:
    """Bridge between crab family substrate and quilt pattern representation."""
    
    # Crab types and their default rotations
    DEFAULT_ROTATIONS = {
        "crab-traps": 0.0,
        "hermit-crab": 45.0,
        "fiddler": 0.0,
        "blue-swimmer": 90.0,
        "ghost": 0.0
    }
    
    # Pattern generators
    PATTERN_FACTORIES = {
        "random": "generate_random",
        "spiral": "generate_spiral",
        "wave": "generate_wave"
    }
    
    def __init__(self, width: int = 10, height: int = 10, size: float = 1.0):
        self.width = width
        self.height = height
        self.size = size
        self.tiles: Dict[HexCoord, Tile] = {}
        self._validate_dimensions()
    
    def _validate_dimensions(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive integers")
    
    def _get_initial_coord(self) -> HexCoord:
        """Return center hex coordinate."""
        return HexCoord(self.width // 2, self.height // 2)
    
    def _get_hex_coords(self) -> List[HexCoord]:
        """Generate all hex coordinates in grid."""
        coords = []
        for q in range(-self.width//2, self.width//2 + 1):
            for r in range(-self.height//2, self.height//2 + 1):
                if abs(q) + abs(r) <= max(self.width, self.height):
                    coords.append(HexCoord(q, r))
        return coords
    
    def generate_random(self, seed: Optional[int] = None) -> 'CrabFamilyToQuilt':
        """Generate a random quilt pattern."""
        if seed is not None:
            random.seed(seed)
        
        coords = self._get_hex_coords()
        random.shuffle(coords)
        
        for coord in coords:
            crab_type = random.choice(list(self.DEFAULT_ROTATIONS.keys()))
            rotation = self.DEFAULT_ROTATIONS[crab_type]
            tile = Tile(crab_type, coord.q, coord.r, rotation)
            self.tiles[coord] = tile
        
        return self
    
    def generate_spiral(self, seed: Optional[int] = None) -> 'CrabFamilyToQuilt':
        """Generate a spiral pattern from center outward."""
        if seed is not None:
            random.seed(seed)
        
        start = self._get_initial_coord()
        visited: Set[HexCoord] = set()
        queue: List[HexCoord] = [start]
        visited.add(start)
        
        while queue:
            current = queue.pop(0)
            crab_type = random.choice(list(self.DEFAULT_ROTATIONS.keys()))
            rotation = self.DEFAULT_ROTATIONS[crab_type]
            tile = Tile(crab_type, current.q, current.r, rotation)
            self.tiles[current] = tile
            
            # Add unvisited neighbors
            for neighbor in current.neighbors():
                if neighbor not in visited and self._is_within_bounds(neighbor):
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return self
    
    def generate_wave(self, seed: Optional[int] = None) -> 'CrabFamilyToQuilt':
        """Generate a wave-like pattern using row-based phase."""
        if seed is not None:
            random.seed(seed)
        
        for q in range(-self.width//2, self.width//2 + 1):
            for r in range(-self.height//2, self.height//2 + 1):
                coord = HexCoord(q, r)
                if not self._is_within_bounds(coord):
                    continue
                
                phase = (q + r) % 3
                crab_types = ["crab-traps", "hermit-crab", "fiddler"]
                crab_type = crab_types[phase]
                rotation = self.DEFAULT_ROTATIONS[crab_type]
                tile = Tile(crab_type, q, r, rotation)
                self.tiles[coord] = tile
        
        return self
    
    def _is_within_bounds(self, coord: HexCoord) -> bool:
        """Check if coordinate is within grid bounds."""
        return (-self.width//2 <= coord.q <= self.width//2 and
                -self.height//2 <= coord.r <= self.height//2)
    
    def get_tile(self, q: int, r: int) -> Optional[Tile]:
        """Get tile at axial coordinates."""
        coord = HexCoord(q, r)
        return self.tiles.get(coord)
    
    def set_tile(self, q: int, r: int, crab_type: str, rotation: float = None) -> 'CrabFamilyToQuilt':
        """Set a tile at axial coordinates."""
        if crab_type not in self.DEFAULT_ROTATIONS:
            raise ValueError(f"Invalid crab type: {crab_type}")
        
        if rotation is None:
            rotation = self.DEFAULT_ROTATIONS[crab_type]
        
        coord = HexCoord(q, r)
        tile = Tile(crab_type, q, r, rotation)
        self.tiles[coord] = tile
        return self
    
    def get_tiles(self) -> List[Tile]:
        """Return all tiles as list."""
        return list(self.tiles.values())
    
    def to_json(self) -> str:
        """Export quilt to JSON string."""
        data = {
            "width": self.width,
            "height": self.height,
            "size": self.size,
            "tiles": [tile.to_dict() for tile in self.get_tiles()]
        }
        return json.dumps(data, indent=2)
    
    def from_json(self, json_str: str) -> 'CrabFamilyToQuilt':
        """Import quilt from JSON string."""
        data = json.loads(json_str)
        
        self.width = data["width"]
        self.height = data["height"]
        self.size = data["size"]
        self.tiles = {}
        
        for tile_data in data["tiles"]:
            coord = HexCoord(tile_data["x"], tile_data["y"])
            tile = Tile(
                crab_type=tile_data["crab_type"],
                x=tile_data["x"],
                y=tile_data["y"],
                rotation=tile_data["rotation"]
            )
            self.tiles[coord] = tile
        
        return self
    
    def clone(self) -> 'CrabFamilyToQuilt':
        """Return a deep copy of the quilt."""
        new_quilt = CrabFamilyToQuilt(self.width, self.height, self.size)
        new_quilt.tiles = deepcopy(self.tiles)
        return new_quilt
    
    def count_crab_types(self) -> Dict[str, int]:
        """Count occurrences of each crab type."""
        count = {t: 0 for t in self.DEFAULT_ROTATIONS.keys()}
        for tile in self.get_tiles():
            count[tile.crab_type] += 1
        return count
    
    def get_neighbors(self, q: int, r: int) -> List[Tile]:
        """Get all tiles adjacent to given coordinates."""
        coord = HexCoord(q, r)
        neighbors = []
        for neighbor in coord.neighbors():
            if neighbor in self.tiles:
                neighbors.append(self.tiles[neighbor])
        return neighbors
    
    def get_connected_components(self) -> List[List[Tile]]:
        """Find connected regions of same crab type."""
        visited: Set[HexCoord] = set()
        components = []
        
        for coord in self.tiles:
            if coord in visited:
                continue
            
            component: List[Tile] = []
            queue = [coord]
            visited.add(coord)
            start_type = self.tiles[coord].crab_type
            
            while queue:
                current = queue.pop(0)
                tile = self.tiles[current]
                component.append(tile)
                
                for neighbor in current.neighbors():
                    if (neighbor not in visited and 
                        neighbor in self.tiles and 
                        self.tiles[neighbor].crab_type == start_type):
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            if component:
                components.append(component)
        
        return components
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get the bounding box (min_q, max_q, min_r, max_r) of filled tiles."""
        if not self.tiles:
            return (0, 0, 0, 0)
        
        q_coords = [c.q for c in self.tiles]
        r_coords = [c.r for c in self.tiles]
        return (min(q_coords), max(q_coords), min(r_coords), max(r_coords))


# === UTILITY FUNCTIONS ===

def create_quilt_from_pattern(width: int, height: int, pattern: str, seed: Optional[int] = None) -> CrabFamilyToQuilt:
    """Create a quilt using a specified pattern."""
    quilt = CrabFamilyToQuilt(width, height)
    
    if pattern == "random":
        return quilt.generate_random(seed)
    elif pattern == "spiral":
        return quilt.generate_spiral(seed)
    elif pattern == "wave":
        return quilt.generate_wave(seed)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")

def print_quilt_ascii(quilt: CrabFamilyToQuilt) -> None:
    """Print a simple ASCII representation of the quilt."""
    if not quilt.tiles:
        print("Empty quilt")
        return
    
    min_q, max_q, min_r, max_r = quilt.get_bounding_box()
    
    for r in range(max_r, min_r - 1, -1):
        line = " " * (max_q - min_q)  # leading spaces
        for q in range(min_q, max_q + 1):
            coord = HexCoord(q, r)
            tile = quilt.get_tile(q, r)
            if tile:
                symbol = tile.crab_type[0].upper()
                line += f" {symbol} "
            else:
                line += " . "
        print(line)


# === TESTS ===

def test_crab_family_to_quilt():
    """Test suite for CrabFamilyToQuilt bridge."""
    
    # Test 1: Basic initialization
    quilt = CrabFamilyToQuilt(5, 5)
    assert quilt.width == 5
    assert quilt.height == 5
    assert len(quilt.tiles) == 0
    
    # Test 2: Random pattern generation
    quilt_random = CrabFamilyToQuilt(3, 3).generate_random(seed=42)
    assert len(quilt_random.tiles) == 9
    assert all(t.crab_type in ["crab-traps", "hermit-crab", "fiddler", "blue-swimmer", "ghost"] 
               for t in quilt_random.get_tiles())
    
    # Test 3: Spiral pattern generation
    quilt_spiral = CrabFamilyToQuilt(3, 3).generate_spiral(seed=42)
    assert len(quilt_spiral.tiles) == 9
    
    # Test 4: Wave pattern generation
    quilt_wave = CrabFamilyToQuilt(3, 3).generate_wave(seed=42)
    assert len(quilt_wave.tiles) == 9
    counts = quilt_wave.count_crab_types()
    assert sum(counts.values()) == 9
    assert counts["crab-traps"] + counts["hermit-crab"] + counts["fiddler"] == 9
    
    # Test 5: Tile access and coordinate system
    coord = HexCoord(0, 0)
    tile = Tile("crab-traps", 0, 0, 0.0)
    quilt.tiles[coord] = tile
    assert quilt.get_tile(0, 0) == tile
    
    # Test 6: JSON serialization
    quilt_json = quilt_random.to_json()
    assert isinstance(quilt_json, str)
    assert "crab-traps" in quilt_json or "hermit-crab" in quilt_json
    
    # Test 7: JSON deserialization
    quilt_from_json = CrabFamilyToQuilt(3, 3).from_json(quilt_json)
    assert len(quilt_from_json.tiles) == 9
    tile1 = quilt_random.get_tile(0, 0)
    tile2 = quilt_from_json.get_tile(0, 0)
    assert tile1.crab_type == tile2.crab_type
    assert tile1.x == tile2.x
    assert tile1.y == tile2.y
    assert tile1.rotation == tile2.rotation
    
    # Test 8: Tile cloning
    quilt_clone = quilt_random.clone()
    assert len(quilt_clone.tiles) == 9
    assert quilt_clone.width == 3
    assert quilt_clone.height == 3
    
    # Test 9: Connected components
    # Create a small quilt with connected components
    quilt_comp = CrabFamilyToQuilt(2, 2)
    quilt_comp.set_tile(0, 0, "crab-traps")
    quilt_comp.set_tile(1, 0, "crab-traps")
    quilt_comp.set_tile(0, 1, "fiddler")
    quilt_comp.set_tile(1, 1, "fiddler")
    
    components = quilt_comp.get_connected_components()
    assert len(components) == 2
    assert len(components[0]) == 2  # crab-traps
    assert len(components[1]) == 2  # fiddler
    
    # Test 10: Bounding box
    min_q, max_q, min_r, max_r = quilt_comp.get_bounding_box()
    assert min_q == 0
    assert max_q == 1
    assert min_r == 0
    assert max_r == 1
    
    # Test 11: Neighbor retrieval
    neighbors = quilt_comp.get_neighbors(0, 0)
    assert len(neighbors) == 2  # right and down
    assert any(t.crab_type == "crab-traps" for t in neighbors)
    assert any(t.crab_type == "fiddler" for t in neighbors)
    
    # Test 12: Pattern factory
    quilt_factory = create_quilt_from_pattern(2, 2, "random", seed=123)
    assert len(quilt_factory.tiles) == 4
    assert quilt_factory.count_crab_types()["crab-traps"] > 0
    
    print("All tests passed!")


if __name__ == "__main__":
    # Run tests
    test_crab_family_to_quilt()
    
    # Example usage
    print("\n=== Example: Create and display a quilt ===")
    example = CrabFamilyToQuilt(5, 5).generate_spiral(seed=123)
    print("Generated quilt:")
    print_quilt_ascii(example)
    
    print("\nJSON representation:")
    print(example.to_json())
    
    print("\nCrab type counts:")
    counts = example.count_crab_types()
    for crab_type, count in sorted(counts.items()):
        print(f"  {crab_type}: {count}")
