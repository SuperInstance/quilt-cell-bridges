#!/usr/bin/env python3
"""
Convert ternary-spreadsheet to Quilt sheet format.
Creates a .qzt file with 27 ternary cells, formulas, and mutation operators.
"""

import json
import os
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
from collections import Counter

class TernaryValue(Enum):
    """Ternary values for the spreadsheet cells."""
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

@dataclass
class TernaryCell:
    """A single cell in the ternary spreadsheet."""
    value: TernaryValue
    fitness: float
    history: List[TernaryValue]
    generation: int
    formula: Optional[str] = None
    inputs: Optional[List[int]] = None

class TernarySpreadsheet:
    """Main class for the ternary spreadsheet to Quilt converter."""
    
    def __init__(self):
        self.cells: List[TernaryCell] = []
        self.formulas: Dict[str, Any] = {}
        self.mutation_operators = {
            'L': 'LS',  # L → LS (Penrose-like substitution)
            'S': 'L'    # S → L
        }
        self.primitive_8 = self._create_primitive_8()
        
    def _create_primitive_8(self) -> List[int]:
        """Create the 8-primitive cell as a ternary representation."""
        # 8 in ternary is 22 (2*3^1 + 2*3^0), but we use -1, 0, 1
        # So 8 = 1*3^2 + 0*3^1 + (-1)*3^0 = 10(-1) in balanced ternary
        return [1, 0, -1]
    
    def _generate_27_cells(self) -> List[TernaryCell]:
        """Generate 27 ternary cells (3^3 combinations)."""
        cells = []
        values = [-1, 0, 1]
        
        # Generate all 3^3 = 27 combinations
        for i in range(27):
            # Convert to balanced ternary representation
            n = i
            digits = []
            for _ in range(3):
                digits.append(n % 3 - 1)  # Map 0->-1, 1->0, 2->1
                n //= 3
            
            # Create cell with initial value
            value = TernaryValue(digits[0])
            history = [value]
            
            # Calculate fitness based on the ternary pattern
            fitness = self._calculate_fitness(digits)
            
            cell = TernaryCell(
                value=value,
                fitness=fitness,
                history=history,
                generation=0
            )
            cells.append(cell)
        
        return cells
    
    def _calculate_fitness(self, digits: List[int]) -> float:
        """Calculate fitness for a ternary pattern."""
        # Simple fitness: sum of absolute values, normalized
        return sum(abs(d) for d in digits) / len(digits)
    
    def _apply_mutation(self, cell: TernaryCell) -> TernaryCell:
        """Apply Penrose-like substitution mutation."""
        new_value = cell.value
        
        # Apply mutation operator based on current value
        if cell.value == TernaryValue.POSITIVE:  # L → LS
            # L (Positive) becomes LS (Positive then Neutral)
            new_value = TernaryValue.NEUTRAL
        elif cell.value == TernaryValue.NEGATIVE:  # S → L
            # S (Negative) becomes L (Positive)
            new_value = TernaryValue.POSITIVE
        
        # Update history and generation
        new_history = cell.history + [new_value]
        new_cell = TernaryCell(
            value=new_value,
            fitness=self._calculate_fitness([new_value.value]),
            history=new_history,
            generation=cell.generation + 1
        )
        return new_cell
    
    def _calculate_entropy(self, values: List[int]) -> float:
        """Calculate entropy of a list of ternary values."""
        if not values:
            return 0.0
        
        counter = Counter(values)
        total = len(values)
        entropy = 0.0
        
        for count in counter.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _calculate_evolution(self, cells: List[TernaryCell]) -> List[TernaryCell]:
        """Apply evolution to cells based on fitness."""
        # Sort by fitness and keep top performers
        sorted_cells = sorted(cells, key=lambda c: c.fitness, reverse=True)
        top_half = sorted_cells[:len(sorted_cells)//2]
        
        # Evolve the top half
        evolved = []
        for cell in top_half:
            evolved.append(self._apply_mutation(cell))
        
        # Fill remaining with mutated versions
        while len(evolved) < len(cells):
            source = evolved[len(evolved) % len(evolved)]
            evolved.append(self._apply_mutation(source))
        
        return evolved[:len(cells)]
    
    def _find_best(self, cells: List[TernaryCell]) -> TernaryCell:
        """Find the best cell based on fitness."""
        return max(cells, key=lambda c: c.fitness)
    
    def _find_species(self, cells: List[TernaryCell]) -> Dict[str, int]:
        """Count species (distinct values) in cells."""
        species_count = Counter(cell.value.value for cell in cells)
        return {
            'negative': species_count.get(-1, 0),
            'neutral': species_count.get(0, 0),
            'positive': species_count.get(1, 0)
        }
    
    def _exhaustive_search(self, cells: List[TernaryCell]) -> List[TernaryCell]:
        """Perform exhaustive search over all possible mutations."""
        results = []
        for cell in cells:
            # Try all possible mutations
            for _ in range(3):
                mutated = self._apply_mutation(cell)
                results.append(mutated)
        return results
    
    def build_quilt_sheet(self) -> Dict[str, Any]:
        """Build the complete Quilt sheet structure."""
        # Generate the 27 base cells
        self.cells = self._generate_27_cells()
        
        # Apply mutations to create evolved cells
        evolved_cells = []
        for cell in self.cells:
            evolved_cells.append(self._apply_mutation(cell))
        
        # Calculate formula results
        sum_result = sum(cell.value.value for cell in self.cells)
        avg_result = sum_result / len(self.cells)
        entropy_result = self._calculate_entropy([c.value.value for c in self.cells])
        best_cell = self._find_best(self.cells)
        species_result = self._find_species(self.cells)
        
        # Build the Quilt sheet structure
        quilt_sheet = {
            "schema_version": "1.0",
            "type": "ternary-spreadsheet-quilt",
            "metadata": {
                "source": "ternary-spreadsheet",
                "description": "Converted ternary spreadsheet to Quilt format",
                "cell_count": len(self.cells),
                "formula_count": 7,
                "mutation_operators": self.mutation_operators
            },
            "cells": [],
            "formulas": {},
            "mutation_rules": {
                "operators": self.mutation_operators,
                "description": "Penrose-like substitution: L→LS, S→L"
            },
            "primitive_8": {
                "ternary": self.primitive_8,
                "description": "8 as balanced ternary: 10(-1)"
            }
        }
        
        # Add the 27 cells
        for i, cell in enumerate(self.cells):
            cell_data = {
                "id": i,
                "value": cell.value.value,
                "value_label": cell.value.name,
                "fitness": cell.fitness,
                "history": [v.value for v in cell.history],
                "generation": cell.generation,
                "kind": cell.value.name
            }
            quilt_sheet["cells"].append(cell_data)
        
        # Add evolved cells
        quilt_sheet["evolved_cells"] = []
        for i, cell in enumerate(evolved_cells):
            evolved_data = {
                "source_cell": i,
                "value": cell.value.value,
                "value_label": cell.value.name,
                "fitness": cell.fitness,
                "history": [v.value for v in cell.history],
                "generation": cell.generation,
                "kind": cell.value.name
            }
            quilt_sheet["evolved_cells"].append(evolved_data)
        
        # Add formulas
        quilt_sheet["formulas"] = {
            "SUM": {
                "type": "aggregate",
                "result": sum_result,
                "description": "Sum of all cell values"
            },
            "AVG": {
                "type": "aggregate",
                "result": avg_result,
                "description": "Average of all cell values"
            },
            "ENTROPY": {
                "type": "information",
                "result": entropy_result,
                "description": "Entropy of value distribution"
            },
            "EVOLVE": {
                "type": "evolution",
                "result": [c.value.value for c in evolved_cells],
                "description": "Evolution through mutation"
            },
            "BEST": {
                "type": "optimization",
                "result": {
                    "cell_id": self.cells.index(best_cell),
                    "value": best_cell.value.value,
                    "fitness": best_cell.fitness
                },
                "description": "Best performing cell"
            },
            "SPECIES": {
                "type": "classification",
                "result": species_result,
                "description": "Species distribution"
            },
            "EXHAUSTIVE": {
                "type": "search",
                "result": self._exhaustive_search(self.cells)[:10],  # Sample of results
                "description": "Exhaustive search results"
            }
        }
        
        # Add cell kinds
        quilt_sheet["cell_kinds"] = {
            "Negative": {
                "value": -1,
                "color": "#ff0000",
                "description": "Negative ternary value"
            },
            "Neutral": {
                "value": 0,
                "color": "#cccccc",
                "description": "Neutral ternary value"
            },
            "Positive": {
                "value": 1,
                "color": "#00ff00",
                "description": "Positive ternary value"
            }
        }
        
        return quilt_sheet
    
    def save_to_file(self, filepath: str):
        """Save the Quilt sheet to a .qzt file."""
        quilt_sheet = self.build_quilt_sheet()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save as JSON with .qzt extension
        with open(filepath, 'w') as f:
            json.dump(quilt_sheet, f, indent=2, default=str)
        
        print(f"Quilt sheet saved to {filepath}")
        print(f"Total cells: {len(quilt_sheet['cells'])}")
        print(f"Formulas: {list(quilt_sheet['formulas'].keys())}")
        print(f"Mutation operators: {quilt_sheet['mutation_rules']['operators']}")

def main():
    """Main execution function."""
    # Create converter instance
    converter = TernarySpreadsheet()
    
    # Define output path
    output_path = "/workspace/superinstance-website/bridges/ternary-spreadsheet-quilt.qzt"
    
    # Build and save the Quilt sheet
    converter.save_to_file(output_path)
    
    # Print summary
    print("\n=== Conversion Summary ===")
    print("Successfully converted ternary-spreadsheet to Quilt format")
    print(f"Output: {output_path}")
    
    # Verify the file was created
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"File size: {file_size} bytes")
        
        # Load and verify
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        print(f"\nVerification:")
        print(f"  - Schema version: {data['schema_version']}")
        print(f"  - Cell count: {data['metadata']['cell_count']}")
        print(f"  - Formula count: {data['metadata']['formula_count']}")
        print(f"  - Primitive 8: {data['primitive_8']['ternary']}")
        print(f"  - Cell kinds: {list(data['cell_kinds'].keys())}")
    else:
        print(f"ERROR: File was not created at {output_path}")

if __name__ == "__main__":
    main()
