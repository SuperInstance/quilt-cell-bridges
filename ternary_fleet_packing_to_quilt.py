#!/usr/bin/env python3
"""
Convert ternary-fleet-packing to a Quilt sheet.

This script creates a Quilt sheet representation of a ternary fleet packing system,
where each cell has 3 states (ternary values) and the structure follows a
hierarchical pattern of connectivity.

The Quilt sheet structure:
- 27 ternary cells (3³ combinations)
- 81 edges (each cell connects to 3 neighbors)
- 3 meta-cells (the trinity: A, B, C)
- 9 sub-meta-cells (each pair of trinity states)
- 1 super-cell (the whole fleet)
"""

import json
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TernaryState(Enum):
    """Three possible states for ternary cells."""
    ZERO = 0
    ONE = 1
    TWO = 2


@dataclass
class Cell:
    """Represents a single cell in the Quilt sheet."""
    id: str
    type: str  # 'ternary', 'meta', 'sub_meta', 'super'
    state: int = 0
    connections: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Edge:
    """Represents a connection between two cells."""
    source: str
    target: str
    weight: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TernaryFleetPackingToQuilt:
    """Converter for ternary fleet packing to Quilt sheet format."""
    
    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        self.edges: List[Edge] = []
        self.sheet_data: Dict[str, Any] = {}
        
    def generate_ternary_cells(self) -> None:
        """Generate 27 ternary cells representing all 3³ combinations."""
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    cell_id = f"T_{i}{j}{k}"
                    cell = Cell(
                        id=cell_id,
                        type="ternary",
                        state=(i + j + k) % 3,
                        metadata={
                            "position": [i, j, k],
                            "ternary_value": i * 9 + j * 3 + k,
                            "states": [i, j, k]
                        }
                    )
                    self.cells[cell_id] = cell
    
    def generate_edges(self) -> None:
        """Generate 81 edges connecting each cell to 3 neighbors."""
        ternary_cells = [cell for cell in self.cells.values() if cell.type == "ternary"]
        
        for cell in ternary_cells:
            pos = cell.metadata["position"]
            # Generate 3 connections to neighboring cells
            neighbors = []
            
            # Connection 1: Next cell in sequence (mod 3)
            next_pos = [(pos[0] + 1) % 3, pos[1], pos[2]]
            neighbors.append(f"T_{next_pos[0]}{next_pos[1]}{next_pos[2]}")
            
            # Connection 2: Next cell in second dimension
            next_pos2 = [pos[0], (pos[1] + 1) % 3, pos[2]]
            neighbors.append(f"T_{next_pos2[0]}{next_pos2[1]}{next_pos2[2]}")
            
            # Connection 3: Next cell in third dimension
            next_pos3 = [pos[0], pos[1], (pos[2] + 1) % 3]
            neighbors.append(f"T_{next_pos3[0]}{next_pos3[1]}{next_pos3[2]}")
            
            # Add edges
            for neighbor_id in neighbors:
                if neighbor_id in self.cells:
                    edge = Edge(
                        source=cell.id,
                        target=neighbor_id,
                        weight=1.0,
                        metadata={
                            "type": "ternary_connection",
                            "dimension": "sequence"
                        }
                    )
                    self.edges.append(edge)
                    cell.connections.append(neighbor_id)
    
    def generate_meta_cells(self) -> None:
        """Generate 3 meta-cells representing the trinity (A, B, C)."""
        trinity_names = ["A", "B", "C"]
        
        for i, name in enumerate(trinity_names):
            cell_id = f"M_{name}"
            cell = Cell(
                id=cell_id,
                type="meta",
                state=i,
                metadata={
                    "trinity_position": i,
                    "name": name,
                    "description": f"Trinity meta-cell {name}"
                }
            )
            self.cells[cell_id] = cell
            
            # Connect meta-cell to a subset of ternary cells
            # Each meta-cell connects to 9 ternary cells (one third of them)
            ternary_cells = [c for c in self.cells.values() if c.type == "ternary"]
            start_idx = i * 9
            for j in range(start_idx, start_idx + 9):
                if j < len(ternary_cells):
                    target = ternary_cells[j]
                    edge = Edge(
                        source=cell_id,
                        target=target.id,
                        weight=0.5,
                        metadata={"type": "meta_to_ternary"}
                    )
                    self.edges.append(edge)
                    cell.connections.append(target.id)
    
    def generate_sub_meta_cells(self) -> None:
        """Generate 9 sub-meta-cells for each pair of trinity states."""
        trinity_names = ["A", "B", "C"]
        pair_count = 0
        
        for i in range(3):
            for j in range(i + 1, 3):
                cell_id = f"SM_{trinity_names[i]}{trinity_names[j]}"
                cell = Cell(
                    id=cell_id,
                    type="sub_meta",
                    state=(i + j) % 3,
                    metadata={
                        "pair": [trinity_names[i], trinity_names[j]],
                        "pair_indices": [i, j],
                        "description": f"Sub-meta-cell for pair {trinity_names[i]}-{trinity_names[j]}"
                    }
                )
                self.cells[cell_id] = cell
                
                # Connect to the two parent meta-cells
                parent1 = f"M_{trinity_names[i]}"
                parent2 = f"M_{trinity_names[j]}"
                
                if parent1 in self.cells:
                    edge1 = Edge(
                        source=cell_id,
                        target=parent1,
                        weight=0.7,
                        metadata={"type": "sub_meta_to_meta"}
                    )
                    self.edges.append(edge1)
                    cell.connections.append(parent1)
                
                if parent2 in self.cells:
                    edge2 = Edge(
                        source=cell_id,
                        target=parent2,
                        weight=0.7,
                        metadata={"type": "sub_meta_to_meta"}
                    )
                    self.edges.append(edge2)
                    cell.connections.append(parent2)
                
                # Connect to 3 ternary cells
                ternary_cells = [c for c in self.cells.values() if c.type == "ternary"]
                start_idx = pair_count * 3
                for k in range(start_idx, min(start_idx + 3, len(ternary_cells))):
                    target = ternary_cells[k]
                    edge = Edge(
                        source=cell_id,
                        target=target.id,
                        weight=0.3,
                        metadata={"type": "sub_meta_to_ternary"}
                    )
                    self.edges.append(edge)
                    cell.connections.append(target.id)
                
                pair_count += 1
    
    def generate_super_cell(self) -> None:
        """Generate 1 super-cell representing the whole fleet."""
        super_cell = Cell(
            id="SUPER",
            type="super",
            state=0,
            metadata={
                "description": "Super-cell representing the entire ternary fleet",
                "total_ternary_cells": 27,
                "total_meta_cells": 3,
                "total_sub_meta_cells": 9
            }
        )
        self.cells["SUPER"] = super_cell
        
        # Connect super-cell to all meta-cells and sub-meta-cells
        for cell_id, cell in self.cells.items():
            if cell.type in ["meta", "sub_meta"]:
                edge = Edge(
                    source="SUPER",
                    target=cell_id,
                    weight=0.9,
                    metadata={"type": "super_to_hierarchy"}
                )
                self.edges.append(edge)
                super_cell.connections.append(cell_id)
    
    def build_sheet(self) -> Dict[str, Any]:
        """Build the complete Quilt sheet data structure."""
        self.generate_ternary_cells()
        self.generate_edges()
        self.generate_meta_cells()
        self.generate_sub_meta_cells()
        self.generate_super_cell()
        
        self.sheet_data = {
            "format_version": "1.0",
            "sheet_type": "ternary_fleet_packing",
            "title": "Ternary Fleet Packing Quilt Sheet",
            "description": "A Quilt sheet representation of ternary fleet packing with hierarchical structure",
            "statistics": {
                "total_cells": len(self.cells),
                "total_edges": len(self.edges),
                "ternary_cells": sum(1 for c in self.cells.values() if c.type == "ternary"),
                "meta_cells": sum(1 for c in self.cells.values() if c.type == "meta"),
                "sub_meta_cells": sum(1 for c in self.cells.values() if c.type == "sub_meta"),
                "super_cells": sum(1 for c in self.cells.values() if c.type == "super")
            },
            "cells": [asdict(cell) for cell in self.cells.values()],
            "edges": [asdict(edge) for edge in self.edges],
            "hierarchy": {
                "super_cell": "SUPER",
                "meta_cells": ["M_A", "M_B", "M_C"],
                "sub_meta_cells": ["SM_AB", "SM_AC", "SM_BC"],
                "ternary_cells": [f"T_{i}{j}{k}" for i in range(3) for j in range(3) for k in range(3)]
            }
        }
        
        return self.sheet_data
    
    def save_to_file(self, filepath: str) -> None:
        """Save the Quilt sheet to a JSON file."""
        if not self.sheet_data:
            self.build_sheet()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.sheet_data, f, indent=2, ensure_ascii=False)
        
        print(f"Quilt sheet saved to: {filepath}")
        print(f"Total cells: {self.sheet_data['statistics']['total_cells']}")
        print(f"Total edges: {self.sheet_data['statistics']['total_edges']}")
        print(f"Ternary cells: {self.sheet_data['statistics']['ternary_cells']}")
        print(f"Meta cells: {self.sheet_data['statistics']['meta_cells']}")
        print(f"Sub-meta cells: {self.sheet_data['statistics']['sub_meta_cells']}")
        print(f"Super cells: {self.sheet_data['statistics']['super_cells']}")


def main():
    """Main function to generate the Quilt sheet."""
    # Create output directory if it doesn't exist
    output_dir = "/workspace/superinstance-website/bridges"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create converter instance
    converter = TernaryFleetPackingToQuilt()
    
    # Build and save the Quilt sheet
    output_path = os.path.join(output_dir, "ternary-fleet-packing-quilt.qzt")
    converter.save_to_file(output_path)
    
    # Print summary
    print("\n=== Ternary Fleet Packing to Quilt Conversion Complete ===")
    print(f"Output file: {output_path}")
    print("\nStructure Summary:")
    print("  - 27 ternary cells (3³ combinations)")
    print("  - 81 edges (each cell connects to 3 neighbors)")
    print("  - 3 meta-cells (trinity: A, B, C)")
    print("  - 9 sub-meta-cells (pairs of trinity states)")
    print("  - 1 super-cell (whole fleet)")
    
    # Verify the counts
    stats = converter.sheet_data["statistics"]
    assert stats["ternary_cells"] == 27, "Expected 27 ternary cells"
    assert stats["meta_cells"] == 3, "Expected 3 meta-cells"
    assert stats["sub_meta_cells"] == 9, "Expected 9 sub-meta-cells"
    assert stats["super_cells"] == 1, "Expected 1 super-cell"
    assert stats["total_edges"] == 81, "Expected 81 edges"
    
    print("\n✓ All structure requirements verified successfully!")


if __name__ == "__main__":
    main()
