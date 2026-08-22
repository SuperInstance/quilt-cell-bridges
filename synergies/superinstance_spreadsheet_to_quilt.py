import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math

class FormulaType(Enum):
    EVOLVE = "EVOLVE"
    BEST = "BEST"
    SPECIES = "SPECIES"
    ENTROPY = "ENTROPY"
    PARETO = "PARETO"
    CORRELATE = "CORRELATE"

@dataclass
class Cell:
    formula: str
    value: Any
    coordinates: Tuple[int, int]
    dependencies: List[Tuple[int, int]]

@dataclass
class EvolutionResult:
    best_solution: Dict[str, float]
    fitness_history: List[float]
    species_diversity: List[float]
    pareto_front: List[Dict[str, float]]

class SuperInstanceSpreadsheetBridge:
    def __init__(self):
        self.cells = {}
        self.formula_registry = {
            FormulaType.EVOLVE: self._handle_evolve,
            FormulaType.BEST: self._handle_best,
            FormulaType.SPECIES: self._handle_species,
            FormulaType.ENTROPY: self._handle_entropy,
            FormulaType.PARETO: self._handle_pareto,
            FormulaType.CORRELATE: self._handle_correlate
        }
        self.evolution_state = None
        
    def formula_to_quilt(self, formula_string: str) -> Dict[str, Any]:
        """
        Convert spreadsheet formula to Quilt-compatible data structure
        """
        formula_string = formula_string.strip().upper()
        
        if formula_string.startswith('='):
            formula_string = formula_string[1:]
            
        formula_parts = formula_string.split('(')
        if len(formula_parts) < 2:
            return {"type": "literal", "value": formula_string}
            
        formula_name = formula_parts[0]
        args_string = formula_parts[1].rstrip(')')
        args = [arg.strip() for arg in args_string.split(',')]
        
        try:
            formula_type = FormulaType(formula_name)
            handler = self.formula_registry[formula_type]
            return handler(args)
        except ValueError:
            return {"type": "unknown", "formula": formula_string}
    
    def _handle_evolve(self, args: List[str]) -> Dict[str, Any]:
        """Handle =EVOLVE(formula, generations, population_size)"""
        if len(args) < 3:
            raise ValueError("EVOLVE requires formula, generations, and population_size")
            
        return {
            "type": "evolution",
            "objective": args[0],
            "generations": int(args[1]),
            "population_size": int(args[2]),
            "parameters": args[3:] if len(args) > 3 else []
        }
    
    def _handle_best(self, args: List[str]) -> Dict[str, Any]:
        """Handle =BEST(solution_index)"""
        return {
            "type": "best_solution",
            "solution_index": int(args[0]) if args else 0
        }
    
    def _handle_species(self, args: List[str]) -> Dict[str, Any]:
        """Handle =SPECIES(generation, species_index)"""
        return {
            "type": "species_analysis",
            "generation": int(args[0]) if args else -1,
            "species_index": int(args[1]) if len(args) > 1 else -1
        }
    
    def _handle_entropy(self, args: List[str]) -> Dict[str, Any]:
        """Handle =ENTROPY(generation)"""
        return {
            "type": "entropy",
            "generation": int(args[0]) if args else -1
        }
    
    def _handle_pareto(self, args: List[str]) -> Dict[str, Any]:
        """Handle =PARETO(objective1, objective2, ...)"""
        return {
            "type": "pareto_front",
            "objectives": args
        }
    
    def _handle_correlate(self, args: List[str]) -> Dict[str, Any]:
        """Handle =CORRELATE(variable1, variable2)"""
        if len(args) < 2:
            raise ValueError("CORRELATE requires two variables")
        return {
            "type": "correlation",
            "variable1": args[0],
            "variable2": args[1]
        }
    
    def run_evolution(self, cells: Dict[Tuple[int, int], Cell], generations: int) -> EvolutionResult:
        """
        Run evolutionary algorithm based on spreadsheet formulas
        """
        self.cells = cells
        
        population_size = 100
        objective_formula = None
        
        for cell in cells.values():
            quilt_data = self.formula_to_quilt(cell.formula)
            if quilt_data.get('type') == 'evolution':
                population_size = quilt_data.get('population_size', 100)
                objective_formula = quilt_data.get('objective', 'fitness')
                break
        
        if objective_formula is None:
            raise ValueError("No EVOLVE formula found in cells")
        
        population = self._initialize_population(population_size)
        fitness_history = []
        species_diversity = []
        pareto_front = []
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual, objective_formula)
                fitness_scores.append(fitness)
            
            # Selection and reproduction
            selected = self._tournament_selection(population, fitness_scores)
            offspring = self._crossover_and_mutate(selected)
            population = offspring
            
            # Track metrics
            best_fitness = max(fitness_scores)
            fitness_history.append(best_fitness)
            species_diversity.append(self._calculate_species_diversity(population))
            
            if generation % 10 == 0:
                pareto_front.append(self._extract_pareto_front(population, fitness_scores))
        
        best_idx = np.argmax(fitness_scores)
        best_solution = population[best_idx]
        
        self.evolution_state = EvolutionResult(
            best_solution=best_solution,
            fitness_history=fitness_history,
            species_diversity=species_diversity,
            pareto_front=pareto_front
        )
        
        return self.evolution_state
    
    def _initialize_population(self, size: int) -> List[Dict[str, float]]:
        """Initialize random population"""
        population = []
        for _ in range(size):
            individual = {
                'x': np.random.uniform(-10, 10),
                'y': np.random.uniform(-10, 10),
                'z': np.random.uniform(-10, 10)
            }
            population.append(individual)
        return population
    
    def _evaluate_fitness(self, individual: Dict[str, float], formula: str) -> float:
        """Evaluate fitness using the objective formula"""
        # Simple implementation - in reality would parse and evaluate the formula
        x, y, z = individual.get('x', 0), individual.get('y', 0), individual.get('z', 0)
        
        if 'sphere' in formula.lower():
            return -(x**2 + y**2 + z**2)  # Negative for minimization
        elif 'rastrigin' in formula.lower():
            A = 10
            return -(A * 3 + x**2 - A * np.cos(2 * np.pi * x) + 
                    y**2 - A * np.cos(2 * np.pi * y) + 
                    z**2 - A * np.cos(2 * np.pi * z))
        else:  # Default sphere function
            return -(x**2 + y**2 + z**2)
    
    def _tournament_selection(self, population: List[Dict], fitness_scores: List[float], 
                            tournament_size: int = 3) -> List[Dict]:
        """Tournament selection for parent selection"""
        selected = []
        for _ in range(len(population)):
            contestants = np.random.choice(len(population), tournament_size, replace=False)
            winner_idx = contestants[np.argmax([fitness_scores[i] for i in contestants])]
            selected.append(population[winner_idx])
        return selected
    
    def _crossover_and_mutate(self, parents: List[Dict], crossover_rate: float = 0.8, 
                            mutation_rate: float = 0.1) -> List[Dict]:
        """Create offspring through crossover and mutation"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i + 1]
                
                if np.random.random() < crossover_rate:
                    # Single-point crossover
                    child1, child2 = {}, {}
                    keys = list(parent1.keys())
                    crossover_point = np.random.randint(1, len(keys))
                    
                    for j, key in enumerate(keys):
                        if j < crossover_point:
                            child1[key] = parent1[key]
                            child2[key] = parent2[key]
                        else:
                            child1[key] = parent2[key]
                            child2[key] = parent1[key]
                    
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parent1.copy(), parent2.copy()])
        
        # Mutation
        for child in offspring:
            for key in child:
                if np.random.random() < mutation_rate:
                    child[key] += np.random.normal(0, 0.5)
        
        return offspring
    
    def _calculate_species_diversity(self, population: List[Dict]) -> float:
        """Calculate species diversity using average distance"""
        if len(population) <= 1:
            return 0.0
        
        total_distance = 0
        count = 0
        
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                dist = math.sqrt(sum((population[i][k] - population[j][k])**2 
                                   for k in population[i].keys()))
                total_distance += dist
                count += 1
        
        return total_distance / count if count > 0 else 0.0
    
    def _extract_pareto_front(self, population: List[Dict], fitness_scores: List[float]) -> Dict[str, float]:
        """Extract Pareto front (simplified - single objective)"""
        best_idx = np.argmax(fitness_scores)
        return population[best_idx]

def round_trip_demo():
    """Demonstrate round-trip conversion and evolution"""
    bridge = SuperInstanceSpreadsheetBridge()
    
    # Create test cells with formulas
    cells = {
        (1, 1): Cell("=EVOLVE(sphere, 50, 100)", None, (1, 1), []),
        (1, 2): Cell("=BEST(0)", None, (1, 2), [(1, 1)]),
        (1, 3): Cell("=SPECIES(25, 0)", None, (1, 3), [(1, 1)]),
        (2, 1): Cell("=ENTROPY(10)", None, (2, 1), [(1, 1)]),
        (2, 2): Cell("=PARETO(f1, f2)", None, (2, 2), []),
        (2, 3): Cell("=CORRELATE(x, y)", None, (2, 3), [(1, 1)])
    }
    
    print("=== Formula to Quilt Conversion ===")
    for coord, cell in cells.items():
        quilt_data = bridge.formula_to_quilt(cell.formula)
        print(f"Cell {coord}: {cell.formula} -> {quilt_data}")
    
    print("\n=== Running Evolution ===")
    result = bridge.run_evolution(cells, generations=50)
    
    print(f"Best solution: {result.best_solution}")
    print(f"Final fitness: {result.fitness_history[-1]:.4f}")
    print(f"Species diversity trend: {result.species_diversity[0]:.2f} -> {result.species_diversity[-1]:.2f}")
    print(f"Pareto front size: {len(result.pareto_front)}")
    
    print("\n=== Round-trip Verification ===")
    # Verify we can convert back and forth
    test_formulas = [
        "=EVOLVE(rastrigin, 100, 200, mu=0.1)",
        "=BEST(5)",
        "=SPECIES(50, 2)",
        "=ENTROPY(25)",
        "=PARETO(cost, performance, reliability)",
        "=CORRELATE(temperature, efficiency)"
    ]
    
    for formula in test_formulas:
        quilt_data = bridge.formula_to_quilt(formula)
        print(f"Original: {formula}")
        print(f"Quilt: {quilt_data}")
        print()

if __name__ == "__main__":
    round_trip_demo()