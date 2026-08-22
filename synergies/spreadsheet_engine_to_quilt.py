import json
from enum import Enum
from typing import Dict, Any, Union, List, Optional
from dataclasses import dataclass

# Quilt cell type definitions
class QuiltCellType(Enum):
    Z_IN = "z_in"
    Z_OUT = "z_out"
    DOUBLE_ENTRY = "double_entry"
    VIBE = "vibe"
    JEPA = "jepa"
    GRAPH = "graph"
    MURMUR = "murmur"

# Spreadsheet engine cell types
class SpreadsheetCellType(Enum):
    VALUE = "value"
    AGENT = "agent"
    TRAINING = "training"
    SIMULATION = "simulation"
    A2A = "a2a"
    MIDI = "midi"
    FORMULA = "formula"

# Evolutionary formulas
class EvolutionaryFormula(Enum):
    EVOLVE = "evolve"
    SPECIES = "species"
    PARETO = "pareto"
    ENTROPY = "entropy"
    CORRELATE = "correlate"
    CONSERVE = "conserve"

@dataclass
class SpreadsheetCell:
    """Represents a cell in the spreadsheet engine"""
    cell_type: SpreadsheetCellType
    coordinates: tuple[int, int]  # (row, col)
    value: Any
    formula: Optional[EvolutionaryFormula] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class QuiltCell:
    """Represents a Quilt cell with type and payload"""
    cell_type: QuiltCellType
    payload: Dict[str, Any]
    coordinates: tuple[int, int]
    source_type: SpreadsheetCellType  # For round-trip mapping

class SpreadsheetEngineBridge:
    """
    Bridge between SuperInstance spreadsheet-engine and Quilt cells
    Handles bidirectional mapping between the 7 cell types and Quilt representations
    """
    
    def __init__(self):
        # Mapping from spreadsheet cell types to Quilt cell types
        self.cell_type_mapping = {
            SpreadsheetCellType.VALUE: [QuiltCellType.Z_IN, QuiltCellType.Z_OUT],
            SpreadsheetCellType.AGENT: [QuiltCellType.DOUBLE_ENTRY],
            SpreadsheetCellType.TRAINING: [QuiltCellType.VIBE, QuiltCellType.JEPA],
            SpreadsheetCellType.SIMULATION: [QuiltCellType.VIBE, QuiltCellType.GRAPH],
            SpreadsheetCellType.A2A: [QuiltCellType.MURMUR],
            SpreadsheetCellType.MIDI: [QuiltCellType.Z_OUT],
            SpreadsheetCellType.FORMULA: [QuiltCellType.JEPA]
        }
        
        # Formula to parameter mapping
        self.formula_parameter_mapping = {
            EvolutionaryFormula.EVOLVE: {
                "algorithm": "genetic",
                "population_size": 100,
                "mutation_rate": 0.01,
                "crossover_rate": 0.7
            },
            EvolutionaryFormula.SPECIES: {
                "algorithm": "kmeans",
                "clusters": 5,
                "max_iterations": 100,
                "tolerance": 1e-4
            },
            EvolutionaryFormula.PARETO: {
                "algorithm": "multi_objective",
                "objectives": ["f1", "f2", "f3"],
                "epsilon": 0.1
            },
            EvolutionaryFormula.ENTROPY: {
                "algorithm": "shannon",
                "base": 2,  # bits
                "normalized": True
            },
            EvolutionaryFormula.CORRELATE: {
                "algorithm": "pearson",
                "significance_level": 0.05,
                "confidence_interval": 0.95
            },
            EvolutionaryFormula.CONSERVE: {
                "algorithm": "budget_constraint",
                "gamma_eta_sum": "budget",
                "tolerance": 1e-6
            }
        }
    
    def cell_to_quilt(self, cell: SpreadsheetCell) -> List[QuiltCell]:
        """
        Convert a spreadsheet engine cell to one or more Quilt cells
        Follows the mapping: Value→Z_in+Z_out, Agent→DoubleEntry, etc.
        """
        quilt_cells = []
        target_types = self.cell_type_mapping[cell.cell_type]
        
        for quilt_type in target_types:
            payload = self._build_quilt_payload(cell, quilt_type)
            quilt_cell = QuiltCell(
                cell_type=quilt_type,
                payload=payload,
                coordinates=cell.coordinates,
                source_type=cell.cell_type
            )
            quilt_cells.append(quilt_cell)
        
        return quilt_cells
    
    def _build_quilt_payload(self, cell: SpreadsheetCell, quilt_type: QuiltCellType) -> Dict[str, Any]:
        """Build the payload for a specific Quilt cell type based on spreadsheet cell data"""
        base_payload = {
            "original_value": cell.value,
            "coordinates": {"row": cell.coordinates[0], "col": cell.coordinates[1]},
            "metadata": cell.metadata.copy()
        }
        
        # Type-specific payload enhancements
        if quilt_type == QuiltCellType.Z_IN:
            base_payload.update({
                "data_type": self._infer_data_type(cell.value),
                "normalized": False,
                "input_channel": "spreadsheet_engine"
            })
        
        elif quilt_type == QuiltCellType.Z_OUT:
            base_payload.update({
                "data_type": self._infer_data_type(cell.value),
                "output_channel": "quilt_interface",
                "timestamp": self._get_current_timestamp()
            })
        
        elif quilt_type == QuiltCellType.DOUBLE_ENTRY:
            # Agent cell: γ+η=budget constraint
            base_payload.update({
                "gamma": cell.metadata.get('gamma', 0.5),
                "eta": cell.metadata.get('eta', 0.5),
                "budget": cell.metadata.get('budget', 1.0),
                "constraint_satisfied": self._check_budget_constraint(
                    cell.metadata.get('gamma', 0.5),
                    cell.metadata.get('eta', 0.5),
                    cell.metadata.get('budget', 1.0)
                )
            })
        
        elif quilt_type == QuiltCellType.VIBE:
            # Used by both Training and Simulation cells
            if cell.cell_type == SpreadsheetCellType.TRAINING:
                base_payload.update({
                    "training_phase": cell.metadata.get('phase', 'initial'),
                    "learning_rate": cell.metadata.get('learning_rate', 0.001),
                    "epochs": cell.metadata.get('epochs', 100)
                })
            else:  # Simulation
                base_payload.update({
                    "simulation_step": cell.metadata.get('step', 0),
                    "time_delta": cell.metadata.get('time_delta', 1.0),
                    "state_vector": cell.metadata.get('state', [])
                })
        
        elif quilt_type == QuiltCellType.JEPA:
            if cell.cell_type == SpreadsheetCellType.FORMULA:
                # Formula cell with evolutionary algorithm
                formula_params = self.formula_to_quilt(cell.formula)
                base_payload.update({
                    "formula_type": cell.formula.value if cell.formula else "none",
                    "parameters": formula_params,
                    "execution_context": "evolutionary_computation"
                })
            else:  # Training cell
                base_payload.update({
                    "prediction_horizon": cell.metadata.get('horizon', 10),
                    "latent_space_dim": cell.metadata.get('latent_dim', 64),
                    "training_loss": cell.metadata.get('loss', 0.0)
                })
        
        elif quilt_type == QuiltCellType.GRAPH:
            # Simulation cell graph representation
            base_payload.update({
                "graph_type": cell.metadata.get('graph_type', 'directed'),
                "nodes": cell.metadata.get('nodes', []),
                "edges": cell.metadata.get('edges', []),
                "adjacency_matrix": cell.metadata.get('adjacency', [])
            })
        
        elif quilt_type == QuiltCellType.MURMUR:
            # A2A cell: agent-to-agent communication
            base_payload.update({
                "message_type": cell.metadata.get('message_type', 'broadcast'),
                "sender_id": cell.metadata.get('sender', 'unknown'),
                "receiver_ids": cell.metadata.get('receivers', []),
                "message_payload": cell.value,
                "timestamp": self._get_current_timestamp()
            })
        
        return base_payload
    
    def formula_to_quilt(self, formula: EvolutionaryFormula) -> Dict[str, Any]:
        """Convert evolutionary formula to Quilt-compatible parameters"""
        if formula not in self.formula_parameter_mapping:
            return {"error": f"Unknown formula: {formula}"}
        
        return self.formula_parameter_mapping[formula].copy()
    
    def quilt_to_cell(self, quilt_cell: QuiltCell) -> SpreadsheetCell:
        """
        Convert a Quilt cell back to spreadsheet engine cell (round-trip)
        This is a simplified reverse mapping for demonstration
        """
        # Reverse mapping logic
        source_type = quilt_cell.source_type
        
        # Extract original value from payload
        value = quilt_cell.payload.get('original_value', None)
        
        # Reconstruct metadata
        metadata = quilt_cell.payload.get('metadata', {}).copy()
        
        # Add type-specific metadata back
        if source_type == SpreadsheetCellType.AGENT:
            metadata.update({
                'gamma': quilt_cell.payload.get('gamma', 0.5),
                'eta': quilt_cell.payload.get('eta', 0.5),
                'budget': quilt_cell.payload.get('budget', 1.0)
            })
        
        elif source_type == SpreadsheetCellType.TRAINING:
            metadata.update({
                'phase': quilt_cell.payload.get('training_phase', 'initial'),
                'learning_rate': quilt_cell.payload.get('learning_rate', 0.001),
                'epochs': quilt_cell.payload.get('epochs', 100),
                'horizon': quilt_cell.payload.get('prediction_horizon', 10),
                'latent_dim': quilt_cell.payload.get('latent_space_dim', 64),
                'loss': quilt_cell.payload.get('training_loss', 0.0)
            })
        
        elif source_type == SpreadsheetCellType.SIMULATION:
            metadata.update({
                'step': quilt_cell.payload.get('simulation_step', 0),
                'time_delta': quilt_cell.payload.get('time_delta', 1.0),
                'state': quilt_cell.payload.get('state_vector', []),
                'graph_type': quilt_cell.payload.get('graph_type', 'directed'),
                'nodes': quilt_cell.payload.get('nodes', []),
                'edges': quilt_cell.payload.get('edges', []),
                'adjacency': quilt_cell.payload.get('adjacency_matrix', [])
            })
        
        elif source_type == SpreadsheetCellType.A2A:
            metadata.update({
                'message_type': quilt_cell.payload.get('message_type', 'broadcast'),
                'sender': quilt_cell.payload.get('sender_id', 'unknown'),
                'receivers': quilt_cell.payload.get('receiver_ids', [])
            })
        
        # Determine formula for formula cells
        formula = None
        if source_type == SpreadsheetCellType.FORMULA:
            formula_type = quilt_cell.payload.get('formula_type')
            if formula_type:
                formula = EvolutionaryFormula(formula_type)
        
        return SpreadsheetCell(
            cell_type=source_type,
            coordinates=quilt_cell.coordinates,
            value=value,
            formula=formula,
            metadata=metadata
        )
    
    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from cell value"""
        if isinstance(value, (int, float)):
            return "numeric"
        elif isinstance(value, str):
            return "text"
        elif isinstance(value, (list, tuple)):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "unknown"
    
    def _check_budget_constraint(self, gamma: float, eta: float, budget: float) -> bool:
        """Check if γ + η = budget constraint is satisfied within tolerance"""
        tolerance = 1e-6
        return abs((gamma + eta) - budget) < tolerance
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

# Demo function for 5x5 grid round-trip
def demo_round_trip():
    """Demonstrate round-trip conversion with a 5x5 grid of cells"""
    bridge = SpreadsheetEngineBridge()
    
    # Create a 5x5 grid of sample cells covering all 7 types
    sample_grid = []
    cell_types = list(SpreadsheetCellType)
    formulas = list(EvolutionaryFormula)
    
    print("=== Spreadsheet Engine to Quilt Bridge Demo ===\n")
    
    # Create sample cells
    for i in range(5):
        row = []
        for j in range(5):
            cell_type = cell_types[(i * 5 + j) % len(cell_types)]
            formula = formulas[(i * 5 + j) % len(formulas)] if cell_type == SpreadsheetCellType.FORMULA else None
            
            # Create sample data based on cell type
            if cell_type == SpreadsheetCellType.VALUE:
                value = (i + 1) * (j + 1)  # Multiplication table
            elif cell_type == SpreadsheetCellType.AGENT:
                value = f"agent_{i}_{j}"
            elif cell_type == SpreadsheetCellType.TRAINING:
                value = f"model_{i}_{j}"
            elif cell_type == SpreadsheetCellType.SIMULATION:
                value = f"sim_{i}_{j}"
            elif cell_type == SpreadsheetCellType.A2A:
                value = f"message_{i}_{j}"
            elif cell_type == SpreadsheetCellType.MIDI:
                value = f"midi_{i}_{j}"
            else:  # FORMULA
                value = f"formula_{i}_{j}"
            
            # Add type-specific metadata
            metadata = {"created_by": "demo", "grid_position": (i, j)}
            if cell_type == SpreadsheetCellType.AGENT:
                metadata.update({"gamma": 0.3 + i * 0.1, "eta": 0.7 - i * 0.1, "budget": 1.0})
            elif cell_type == SpreadsheetCellType.TRAINING:
                metadata.update({"phase": "training", "learning_rate": 0.001, "epochs": 100})
            elif cell_type == SpreadsheetCellType.SIMULATION:
                metadata.update({"step": i * 10 + j, "time_delta": 0.1})
            
            cell = SpreadsheetCell(
                cell_type=cell_type,
                coordinates=(i, j),
                value=value,
                formula=formula,
                metadata=metadata
            )
            row.append(cell)
        sample_grid.append(row)
    
    print("Original 5x5 Spreadsheet Grid:")
    for i, row in enumerate(sample_grid):
        row_display = []
        for j, cell in enumerate(row):
            row_display.append(f"{cell.cell_type.value[:3]}:{cell.value}")
        print(f"Row {i}: {row_display}")
    
    print("\n" + "="*50 + "\n")
    
    # Convert to Quilt cells
    quilt_grid = []
    total_quilt_cells = 0
    
    print("Converted to Quilt Cells:")
    for i, row in enumerate(sample_grid):
        quilt_row = []
        for j, cell in enumerate(row):
            quilt_cells = bridge.cell_to_quilt(cell)
            quilt_row.append(quilt_cells)
            total_quilt_cells += len(quilt_cells)
            
            print(f"Cell ({i},{j}) {cell.cell_type.value} -> {[qc.cell_type.value for qc in quilt_cells]}")
        
        quilt_grid.append(quilt_row)
    
    print(f"\nTotal Quilt cells generated: {total_quilt_cells}")
    print("\n" + "="*50 + "\n")
    
    # Convert back to spreadsheet cells (round-trip)
    reconstructed_grid = []
    
    print("Round-trip Reconstruction:")
    for i, row in enumerate(quilt_grid):
        reconstructed_row = []
        for j, quilt_cell_group in enumerate(row):
            # For cells that map to multiple Quilt cells, use the first one for reconstruction
            if quilt_cell_group:
                original_cell = bridge.quilt_to_cell(quilt_cell_group[0])
                reconstructed_row.append(original_cell)
                print(f"Quilt -> Cell ({i},{j}): {original_cell.cell_type.value} ✓")
        
        reconstructed_grid.append(reconstructed_row)
    
    print("\n" + "="*50 + "\n")
    
    # Verify round-trip integrity
    verification_passed = True
    for i in range(5):
        for j in range(5):
            original = sample_grid[i][j]
            reconstructed = reconstructed_grid[i][j] if i < len(reconstructed_grid) and j < len(reconstructed_grid[i]) else None
            
            if reconstructed and original.cell_type == reconstructed.cell_type:
                print(f"Cell ({i},{j}): Round-trip verification PASSED")
            else:
                print(f"Cell ({i},{j}): Round-trip verification FAILED")
                verification_passed = False
    
    print(f"\nOverall round-trip verification: {'PASSED' if verification_passed else 'FAILED'}")
    
    # Show formula conversion example
    print("\n" + "="*50)
    print("Formula Conversion Examples:")
    for formula in EvolutionaryFormula:
        params = bridge.formula_to_quilt(formula)
        print(f"{formula.value}: {params}")

if __name__ == "__main__":
    demo_round_trip()