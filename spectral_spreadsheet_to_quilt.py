#!/usr/bin/env python3
"""
Spectral Spreadsheet to Quilt Converter
Converts spectral-spreadsheet concepts into a Quilt sheet (.qzt format)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import uuid
from datetime import datetime, timezone

class SpectralQuiltConverter:
    """Converts spectral spreadsheet data to Quilt sheet format."""
    
    def __init__(self):
        self.cells = []
        self.formulas = []
        self.color_mappings = []
        self.graph_families = []
        
    def create_cell(self, cell_id: str, kind: str, value: Any, formula: str = None, 
                   metadata: Dict = None) -> Dict:
        """Create a single cell in the Quilt sheet."""
        cell = {
            "id": cell_id,
            "kind": kind,
            "value": value,
            "formula": formula,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return cell
    
    def create_number_cell(self, cell_id: str, value: float, description: str = "") -> Dict:
        """Create a numeric cell."""
        return self.create_cell(
            cell_id=cell_id,
            kind="number",
            value=value,
            metadata={"description": description}
        )
    
    def create_graph_cell(self, cell_id: str, adjacency_matrix: List[List[int]], 
                         description: str = "") -> Dict:
        """Create a graph cell with adjacency matrix."""
        return self.create_cell(
            cell_id=cell_id,
            kind="graph",
            value=adjacency_matrix,
            metadata={"description": description, "nodes": len(adjacency_matrix)}
        )
    
    def create_eigenvalue_cell(self, cell_id: str, eigenvalue: float, 
                              matrix_ref: str, description: str = "") -> Dict:
        """Create an eigenvalue cell."""
        return self.create_cell(
            cell_id=cell_id,
            kind="eigenvalue",
            value=eigenvalue,
            formula="=EIGVAL",
            metadata={
                "description": description,
                "matrix_ref": matrix_ref
            }
        )
    
    def create_cr_cell(self, cell_id: str, cr_value: float, 
                      graph_ref: str, description: str = "") -> Dict:
        """Create a Cheeger Ratio (CR) cell."""
        return self.create_cell(
            cell_id=cell_id,
            kind="CR",
            value=cr_value,
            formula="=CR",
            metadata={
                "description": description,
                "graph_ref": graph_ref,
                "color": self.get_cr_color(cr_value)
            }
        )
    
    def get_cr_color(self, cr_value: float) -> str:
        """Map CR value to a color (visual mapping)."""
        # Color scale: green (good) to red (bad)
        if cr_value < 0.3:
            return "#00FF00"  # Green - good connectivity
        elif cr_value < 0.6:
            return "#FFFF00"  # Yellow - moderate
        elif cr_value < 0.8:
            return "#FFA500"  # Orange - poor
        else:
            return "#FF0000"  # Red - very poor
    
    def create_formula(self, name: str, description: str, 
                      implementation: str, parameters: List[str]) -> Dict:
        """Create a formula definition."""
        return {
            "name": name,
            "description": description,
            "implementation": implementation,
            "parameters": parameters,
            "category": "spectral"
        }
    
    def create_color_mapping(self, name: str, value_range: tuple, 
                            color: str, description: str) -> Dict:
        """Create a color mapping for visual representation."""
        return {
            "name": name,
            "min_value": value_range[0],
            "max_value": value_range[1],
            "color": color,
            "description": description
        }
    
    def create_graph_family(self, name: str, description: str, 
                           spectral_properties: Dict, examples: List[str]) -> Dict:
        """Create a graph family definition."""
        return {
            "name": name,
            "description": description,
            "spectral_properties": spectral_properties,
            "examples": examples
        }
    
    def build_sample_data(self):
        """Build the sample spectral spreadsheet data."""
        
        # Sample graphs (adjacency matrices)
        # Path graph P4
        path_p4 = [
            [0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0]
        ]
        
        # Cycle graph C4
        cycle_c4 = [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0]
        ]
        
        # Complete graph K4
        complete_k4 = [
            [0, 1, 1, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 0]
        ]
        
        # Star graph S4
        star_s4 = [
            [0, 1, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0]
        ]
        
        # Create cells
        # 1. Number cells (basic spectral values)
        self.cells.append(self.create_number_cell(
            "cell_001", 2.0, "Spectral radius of P4"
        ))
        self.cells.append(self.create_number_cell(
            "cell_002", 4.0, "Number of vertices in K4"
        ))
        
        # 2. Graph cells
        self.cells.append(self.create_graph_cell(
            "cell_003", path_p4, "Path graph P4"
        ))
        self.cells.append(self.create_graph_cell(
            "cell_004", cycle_c4, "Cycle graph C4"
        ))
        self.cells.append(self.create_graph_cell(
            "cell_005", complete_k4, "Complete graph K4"
        ))
        self.cells.append(self.create_graph_cell(
            "cell_006", star_s4, "Star graph S4"
        ))
        
        # 3. Eigenvalue cells
        self.cells.append(self.create_eigenvalue_cell(
            "cell_007", 2.0, "cell_003", "Largest eigenvalue of P4"
        ))
        self.cells.append(self.create_eigenvalue_cell(
            "cell_008", 2.0, "cell_004", "Largest eigenvalue of C4"
        ))
        self.cells.append(self.create_eigenvalue_cell(
            "cell_009", 3.0, "cell_005", "Largest eigenvalue of K4"
        ))
        
        # 4. CR cells
        self.cells.append(self.create_cr_cell(
            "cell_010", 0.5, "cell_003", "Cheeger ratio of P4"
        ))
        self.cells.append(self.create_cr_cell(
            "cell_011", 0.25, "cell_004", "Cheeger ratio of C4"
        ))
        self.cells.append(self.create_cr_cell(
            "cell_012", 0.75, "cell_005", "Cheeger ratio of K4"
        ))
        self.cells.append(self.create_cr_cell(
            "cell_013", 0.6, "cell_006", "Cheeger ratio of S4"
        ))
        
        # Create formulas
        self.formulas = [
            self.create_formula(
                "=EIGVAL", 
                "Compute the largest eigenvalue of a graph's adjacency matrix",
                "lambda_max(A) where A is the adjacency matrix",
                ["matrix_ref"]
            ),
            self.create_formula(
                "=CR", 
                "Compute the Cheeger Ratio (isoperimetric number)",
                "min(|∂S|/|S|) for all subsets S of vertices",
                ["graph_ref"]
            ),
            self.create_formula(
                "=FIEDLER", 
                "Compute the Fiedler vector (second smallest eigenvector of Laplacian)",
                "eigenvector corresponding to second smallest eigenvalue of L",
                ["graph_ref"]
            ),
            self.create_formula(
                "=SPECTRAL_GAP", 
                "Compute the spectral gap (difference between largest eigenvalues)",
                "lambda_1 - lambda_2",
                ["matrix_ref"]
            ),
            self.create_formula(
                "=ADJ_MATRIX", 
                "Get the adjacency matrix of a graph",
                "A[i][j] = 1 if vertices i and j are adjacent, else 0",
                ["graph_ref"]
            ),
            self.create_formula(
                "=DEGREE", 
                "Compute the degree matrix of a graph",
                "D[i][i] = degree of vertex i",
                ["graph_ref"]
            )
        ]
        
        # Create color mappings for CR
        self.color_mappings = [
            self.create_color_mapping(
                "CR_GOOD", (0.0, 0.3), "#00FF00", 
                "Good connectivity (low CR)"
            ),
            self.create_color_mapping(
                "CR_MODERATE", (0.3, 0.6), "#FFFF00", 
                "Moderate connectivity"
            ),
            self.create_color_mapping(
                "CR_POOR", (0.6, 0.8), "#FFA500", 
                "Poor connectivity"
            ),
            self.create_color_mapping(
                "CR_BAD", (0.8, 1.0), "#FF0000", 
                "Bad connectivity (high CR)"
            )
        ]
        
        # Create graph families
        self.graph_families = [
            self.create_graph_family(
                "Path Graphs",
                "Simple paths with n vertices",
                {
                    "eigenvalues": "2*cos(k*pi/(n+1)) for k=1,...,n",
                    "spectral_gap": "2 - 2*cos(pi/(n+1))",
                    "cr": "~2/(n+1) for large n"
                },
                ["P3", "P4", "P5"]
            ),
            self.create_graph_family(
                "Cycle Graphs",
                "Cycles with n vertices",
                {
                    "eigenvalues": "2*cos(2*pi*k/n) for k=0,...,n-1",
                    "spectral_gap": "2 - 2*cos(2*pi/n)",
                    "cr": "2/n"
                },
                ["C3", "C4", "C5"]
            ),
            self.create_graph_family(
                "Complete Graphs",
                "Fully connected graphs with n vertices",
                {
                    "eigenvalues": "n-1 (once), -1 (n-1 times)",
                    "spectral_gap": "n",
                    "cr": "~1/n"
                },
                ["K3", "K4", "K5"]
            ),
            self.create_graph_family(
                "Star Graphs",
                "Central vertex connected to all others",
                {
                    "eigenvalues": "sqrt(n-1), -sqrt(n-1), 0 (n-2 times)",
                    "spectral_gap": "1",
                    "cr": "1/sqrt(n-1)"
                },
                ["S3", "S4", "S5"]
            )
        ]
    
    def to_quilt_format(self) -> Dict:
        """Convert all data to Quilt sheet format."""
        return {
            "schema_version": "1.0",
            "type": "spectral_spreadsheet",
            "title": "Spectral Spreadsheet Quilt",
            "description": "Browser-based spreadsheet with spectral graph theory computations",
            "created": datetime.now(timezone.utc).isoformat(),
            "cells": self.cells,
            "formulas": self.formulas,
            "color_mappings": self.color_mappings,
            "graph_families": self.graph_families,
            "features": {
                "cell_kinds": ["number", "graph", "eigenvalue", "CR"],
                "formula_count": len(self.formulas),
                "cell_count": len(self.cells),
                "visual_mappings": ["CR color coding"],
                "graph_family_connections": True
            }
        }
    
    def save(self, output_path: str):
        """Save the Quilt sheet to a file."""
        data = self.to_quilt_format()
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON (Quilt format)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Quilt sheet saved to: {output_path}")
        print(f"  - Cells: {len(self.cells)}")
        print(f"  - Formulas: {len(self.formulas)}")
        print(f"  - Color mappings: {len(self.color_mappings)}")
        print(f"  - Graph families: {len(self.graph_families)}")

def main():
    """Main execution function."""
    converter = SpectralQuiltConverter()
    
    # Build sample data
    converter.build_sample_data()
    
    # Define output path
    output_path = "/workspace/superinstance-website/bridges/spectral-spreadsheet-quilt.qzt"
    
    # Save the Quilt sheet
    converter.save(output_path)
    
    # Print summary
    print("\n=== Spectral Spreadsheet to Quilt Conversion Complete ===")
    print("Features included:")
    print("  - 10+ sample cells with spectral values")
    print("  - 4 cell kinds: number, graph, eigenvalue, CR")
    print("  - 6 formulas: =EIGVAL, =CR, =FIEDLER, =SPECTRAL_GAP, =ADJ_MATRIX, =DEGREE")
    print("  - CR coloring as visual mapping")
    print("  - Spectral graph family connections")

if __name__ == "__main__":
    main()
