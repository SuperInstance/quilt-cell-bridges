#!/usr/bin/env python3
"""
Spreadsheet Engine to Quilt Converter
Converts the spreadsheet-engine repository structure into a Quilt sheet format.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class QuiltSheetBuilder:
    """Builds a Quilt sheet from spreadsheet-engine concepts."""
    
    def __init__(self):
        self.sheet = {
            "metadata": {
                "name": "spreadsheet-engine",
                "version": "1.0.0",
                "description": "Multi-cell type spreadsheet engine with AI agents, training, simulation, and MIDI capabilities",
                "created": datetime.now().isoformat(),
                "author": "spreadsheet-engine",
                "license": "MIT"
            },
            "cell_types": [],
            "cells": [],
            "meta_cells": [],
            "formulas": [],
            "graphs": [],
            "connections": []
        }
        
        # Define the 7 cell types
        self.cell_types = [
            {"id": "value", "name": "Value", "description": "Plain data cells (numbers, text, booleans, ternary, vectors)"},
            {"id": "agent", "name": "Agent", "description": "AI agent with capabilities, compute budget (γ), memory budget (η)"},
            {"id": "training", "name": "Training", "description": "ML training job with epochs, loss, checkpoints"},
            {"id": "simulation", "name": "Simulation", "description": "Simulation with state vector, tick counter, max steps"},
            {"id": "a2a", "name": "A2A", "description": "Agent-to-agent endpoint"},
            {"id": "midi", "name": "MIDI", "description": "Sonifies cell values as MIDI events"},
            {"id": "formula", "name": "Formula", "description": "Computes over a range of input cells"}
        ]
        
        # Define formulas
        self.formulas = [
            {"id": "sum", "name": "SUM", "description": "Sum of a range of cells"},
            {"id": "average", "name": "AVERAGE", "description": "Average of a range of cells"},
            {"id": "evolve", "name": "EVOLVE", "description": "Evolutionary algorithm operation"},
            {"id": "species", "name": "SPECIES", "description": "Species classification operation"},
            {"id": "pareto", "name": "PARETO", "description": "Pareto optimization operation"},
            {"id": "entropy", "name": "ENTROPY", "description": "Entropy calculation operation"},
            {"id": "conserve", "name": "CONSERVE", "description": "Conservation law enforcement"}
        ]
    
    def add_cell_type(self, cell_type: Dict[str, Any]):
        """Add a cell type definition."""
        self.sheet["cell_types"].append(cell_type)
    
    def add_cell(self, cell: Dict[str, Any]):
        """Add a cell to the sheet."""
        self.sheet["cells"].append(cell)
    
    def add_meta_cell(self, meta_cell: Dict[str, Any]):
        """Add a meta-cell (conservation law)."""
        self.sheet["meta_cells"].append(meta_cell)
    
    def add_formula(self, formula: Dict[str, Any]):
        """Add a formula definition."""
        self.sheet["formulas"].append(formula)
    
    def add_graph(self, graph: Dict[str, Any]):
        """Add a graph structure (A2A bus)."""
        self.sheet["graphs"].append(graph)
    
    def add_connection(self, connection: Dict[str, Any]):
        """Add a connection between cells."""
        self.sheet["connections"].append(connection)
    
    def build_value_cells(self):
        """Create sample value cells."""
        value_cells = [
            {
                "id": "value_1",
                "type": "value",
                "name": "Temperature Reading",
                "data": {"value": 23.5, "unit": "celsius"},
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "value_2",
                "type": "value",
                "name": "User Name",
                "data": {"value": "Alice", "type": "text"},
                "position": {"x": 0, "y": 1}
            },
            {
                "id": "value_3",
                "type": "value",
                "name": "Active Flag",
                "data": {"value": True, "type": "boolean"},
                "position": {"x": 0, "y": 2}
            },
            {
                "id": "value_4",
                "type": "value",
                "name": "Status",
                "data": {"value": "pending", "type": "ternary", "options": ["pending", "active", "complete"]},
                "position": {"x": 0, "y": 3}
            },
            {
                "id": "value_5",
                "type": "value",
                "name": "Position Vector",
                "data": {"value": [1.0, 2.0, 3.0], "type": "vector", "dimensions": 3},
                "position": {"x": 0, "y": 4}
            },
            {
                "id": "value_6",
                "type": "value",
                "name": "Stock Price",
                "data": {"value": 150.25, "currency": "USD"},
                "position": {"x": 0, "y": 5}
            },
            {
                "id": "value_7",
                "type": "value",
                "name": "Sensor Array",
                "data": {"value": [0.1, 0.2, 0.3, 0.4], "type": "vector", "dimensions": 4},
                "position": {"x": 0, "y": 6}
            }
        ]
        for cell in value_cells:
            self.add_cell(cell)
    
    def build_agent_cells(self):
        """Create sample agent cells."""
        agent_cells = [
            {
                "id": "agent_1",
                "type": "agent",
                "name": "Research Agent",
                "data": {
                    "capabilities": ["research", "analysis", "summarization"],
                    "gamma": 0.7,  # compute budget
                    "eta": 0.3,    # memory budget
                    "model": "gpt-4"
                },
                "position": {"x": 1, "y": 0}
            },
            {
                "id": "agent_2",
                "type": "agent",
                "name": "Data Processing Agent",
                "data": {
                    "capabilities": ["data_cleaning", "transformation", "validation"],
                    "gamma": 0.5,
                    "eta": 0.5,
                    "model": "claude-3"
                },
                "position": {"x": 1, "y": 1}
            },
            {
                "id": "agent_3",
                "type": "agent",
                "name": "Creative Writer",
                "data": {
                    "capabilities": ["writing", "editing", "storytelling"],
                    "gamma": 0.3,
                    "eta": 0.7,
                    "model": "gpt-3.5"
                },
                "position": {"x": 1, "y": 2}
            },
            {
                "id": "agent_4",
                "type": "agent",
                "name": "Code Assistant",
                "data": {
                    "capabilities": ["code_generation", "debugging", "refactoring"],
                    "gamma": 0.8,
                    "eta": 0.2,
                    "model": "codellama"
                },
                "position": {"x": 1, "y": 3}
            },
            {
                "id": "agent_5",
                "type": "agent",
                "name": "Math Solver",
                "data": {
                    "capabilities": ["mathematics", "optimization", "statistics"],
                    "gamma": 0.6,
                    "eta": 0.4,
                    "model": "gpt-4"
                },
                "position": {"x": 1, "y": 4}
            },
            {
                "id": "agent_6",
                "type": "agent",
                "name": "Translation Agent",
                "data": {
                    "capabilities": ["translation", "localization", "language_detection"],
                    "gamma": 0.4,
                    "eta": 0.6,
                    "model": "nmt"
                },
                "position": {"x": 1, "y": 5}
            },
            {
                "id": "agent_7",
                "type": "agent",
                "name": "Analysis Agent",
                "data": {
                    "capabilities": ["sentiment_analysis", "trend_detection", "forecasting"],
                    "gamma": 0.75,
                    "eta": 0.25,
                    "model": "bert"
                },
                "position": {"x": 1, "y": 6}
            }
        ]
        for cell in agent_cells:
            self.add_cell(cell)
    
    def build_training_cells(self):
        """Create sample training cells."""
        training_cells = [
            {
                "id": "training_1",
                "type": "training",
                "name": "Image Classifier Training",
                "data": {
                    "epochs": 100,
                    "loss": 0.023,
                    "checkpoints": ["epoch_25", "epoch_50", "epoch_75", "epoch_100"],
                    "accuracy": 0.95,
                    "dataset": "cifar10"
                },
                "position": {"x": 2, "y": 0}
            },
            {
                "id": "training_2",
                "type": "training",
                "name": "NLP Model Training",
                "data": {
                    "epochs": 50,
                    "loss": 0.045,
                    "checkpoints": ["epoch_10", "epoch_20", "epoch_30", "epoch_40", "epoch_50"],
                    "accuracy": 0.88,
                    "dataset": "imdb"
                },
                "position": {"x": 2, "y": 1}
            },
            {
                "id": "training_3",
                "type": "training",
                "name": "Reinforcement Learning",
                "data": {
                    "epochs": 500,
                    "loss": 0.001,
                    "checkpoints": ["epoch_100", "epoch_200", "epoch_300", "epoch_400", "epoch_500"],
                    "reward": 850.5,
                    "environment": "cartpole"
                },
                "position": {"x": 2, "y": 2}
            },
            {
                "id": "training_4",
                "type": "training",
                "name": "GAN Training",
                "data": {
                    "epochs": 200,
                    "loss": 0.067,
                    "checkpoints": ["epoch_50", "epoch_100", "epoch_150", "epoch_200"],
                    "generator_loss": 0.03,
                    "discriminator_loss": 0.04
                },
                "position": {"x": 2, "y": 3}
            },
            {
                "id": "training_5",
                "type": "training",
                "name": "Transformer Fine-tuning",
                "data": {
                    "epochs": 10,
                    "loss": 0.012,
                    "checkpoints": ["epoch_2", "epoch_4", "epoch_6", "epoch_8", "epoch_10"],
                    "perplexity": 15.3,
                    "model": "bert-base"
                },
                "position": {"x": 2, "y": 4}
            },
            {
                "id": "training_6",
                "type": "training",
                "name": "Time Series Forecasting",
                "data": {
                    "epochs": 150,
                    "loss": 0.034,
                    "checkpoints": ["epoch_30", "epoch_60", "epoch_90", "epoch_120", "epoch_150"],
                    "mae": 0.02,
                    "model": "lstm"
                },
                "position": {"x": 2, "y": 5}
            },
            {
                "id": "training_7",
                "type": "training",
                "name": "Anomaly Detection",
                "data": {
                    "epochs": 80,
                    "loss": 0.018,
                    "checkpoints": ["epoch_20", "epoch_40", "epoch_60", "epoch_80"],
                    "precision": 0.97,
                    "recall": 0.93
                },
                "position": {"x": 2, "y": 6}
            }
        ]
        for cell in training_cells:
            self.add_cell(cell)
    
    def build_simulation_cells(self):
        """Create sample simulation cells."""
        simulation_cells = [
            {
                "id": "simulation_1",
                "type": "simulation",
                "name": "Particle Physics",
                "data": {
                    "state_vector": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "tick": 1000,
                    "max_steps": 10000,
                    "physics": "quantum"
                },
                "position": {"x": 3, "y": 0}
            },
            {
                "id": "simulation_2",
                "type": "simulation",
                "name": "Weather Model",
                "data": {
                    "state_vector": [25.5, 60.2, 1013.25, 45.0],
                    "tick": 500,
                    "max_steps": 5000,
                    "model": "WRF"
                },
                "position": {"x": 3, "y": 1}
            },
            {
                "id": "simulation_3",
                "type": "simulation",
                "name": "Traffic Flow",
                "data": {
                    "state_vector": [120, 45, 0.8, 60],
                    "tick": 200,
                    "max_steps": 2000,
                    "model": "cellular_automata"
                },
                "position": {"x": 3, "y": 2}
            },
            {
                "id": "simulation_4",
                "type": "simulation",
                "name": "Ecosystem Dynamics",
                "data": {
                    "state_vector": [1000, 500, 200, 50],
                    "tick": 300,
                    "max_steps": 3000,
                    "model": "predator_prey"
                },
                "position": {"x": 3, "y": 3}
            },
            {
                "id": "simulation_5",
                "type": "simulation",
                "name": "Financial Market",
                "data": {
                    "state_vector": [100.5, 98.2, 102.1, 99.8],
                    "tick": 1000,
                    "max_steps": 10000,
                    "model": "agent_based"
                },
                "position": {"x": 3, "y": 4}
            },
            {
                "id": "simulation_6",
                "type": "simulation",
                "name": "Molecular Dynamics",
                "data": {
                    "state_vector": [0.5, 0.3, 0.8, 0.2, 0.6, 0.4],
                    "tick": 1500,
                    "max_steps": 15000,
                    "model": "lennard_jones"
                },
                "position": {"x": 3, "y": 5}
            },
            {
                "id": "simulation_7",
                "type": "simulation",
                "name": "Network Simulation",
                "data": {
                    "state_vector": [100, 95, 98, 99],
                    "tick": 800,
                    "max_steps": 8000,
                    "model": "packet_switching"
                },
                "position": {"x": 3, "y": 6}
            }
        ]
        for cell in simulation_cells:
            self.add_cell(cell)
    
    def build_a2a_cells(self):
        """Create sample A2A cells."""
        a2a_cells = [
            {
                "id": "a2a_1",
                "type": "a2a",
                "name": "Research API",
                "data": {
                    "endpoint": "/api/research",
                    "protocol": "REST",
                    "rate_limit": 100,
                    "auth": "bearer_token"
                },
                "position": {"x": 4, "y": 0}
            },
            {
                "id": "a2a_2",
                "type": "a2a",
                "name": "Data Processing API",
                "data": {
                    "endpoint": "/api/process",
                    "protocol": "gRPC",
                    "rate_limit": 500,
                    "auth": "api_key"
                },
                "position": {"x": 4, "y": 1}
            },
            {
                "id": "a2a_3",
                "type": "a2a",
                "name": "Translation API",
                "data": {
                    "endpoint": "/api/translate",
                    "protocol": "REST",
                    "rate_limit": 50,
                    "auth": "oauth2"
                },
                "position": {"x": 4, "y": 2}
            },
            {
                "id": "a2a_4",
                "type": "a2a",
                "name": "Code Generation API",
                "data": {
                    "endpoint": "/api/codegen",
                    "protocol": "WebSocket",
                    "rate_limit": 200,
                    "auth": "jwt"
                },
                "position": {"x": 4, "y": 3}
            },
            {
                "id": "a2a_5",
                "type": "a2a",
                "name": "Analysis API",
                "data": {
                    "endpoint": "/api/analyze",
                    "protocol": "REST",
                    "rate_limit": 300,
                    "auth": "api_key"
                },
                "position": {"x": 4, "y": 4}
            },
            {
                "id": "a2a_6",
                "type": "a2a",
                "name": "Simulation API",
                "data": {
                    "endpoint": "/api/simulate",
                    "protocol": "gRPC",
                    "rate_limit": 100,
                    "auth": "service_account"
                },
                "position": {"x": 4, "y": 5}
            },
            {
                "id": "a2a_7",
                "type": "a2a",
                "name": "MIDI API",
                "data": {
                    "endpoint": "/api/midi",
                    "protocol": "WebSocket",
                    "rate_limit": 50,
                    "auth": "jwt"
                },
                "position": {"x": 4, "y": 6}
            }
        ]
        for cell in a2a_cells:
            self.add_cell(cell)
    
    def build_midi_cells(self):
        """Create sample MIDI cells."""
        midi_cells = [
            {
                "id": "midi_1",
                "type": "midi",
                "name": "Piano Melody",
                "data": {
                    "source_cell": "value_1",
                    "mapping": "linear",
                    "channel": 0,
                    "instrument": "piano",
                    "bpm": 120
                },
                "position": {"x": 5, "y": 0}
            },
            {
                "id": "midi_2",
                "type": "midi",
                "name": "Drum Pattern",
                "data": {
                    "source_cell": "value_2",
                    "mapping": "quantized",
                    "channel": 9,
                    "instrument": "drums",
                    "bpm": 140
                },
                "position": {"x": 5, "y": 1}
            },
            {
                "id": "midi_3",
                "type": "midi",
                "name": "Synth Arpeggio",
                "data": {
                    "source_cell": "value_3",
                    "mapping": "logarithmic",
                    "channel": 1,
                    "instrument": "synth",
                    "bpm": 100
                },
                "position": {"x": 5, "y": 2}
            },
            {
                "id": "midi_4",
                "type": "midi",
                "name": "Bass Line",
                "data": {
                    "source_cell": "value_4",
                    "mapping": "exponential",
                    "channel": 2,
                    "instrument": "bass",
                    "bpm": 110
                },
                "position": {"x": 5, "y": 3}
            },
            {
                "id": "midi_5",
                "type": "midi",
                "name": "String Ensemble",
                "data": {
                    "source_cell": "value_5",
                    "mapping": "harmonic",
                    "channel": 3,
                    "instrument": "strings",
                    "bpm": 90
                },
                "position": {"x": 5, "y": 4}
            },
            {
                "id": "midi_6",
                "type": "midi",
                "name": "Ambient Pad",
                "data": {
                    "source_cell": "value_6",
                    "mapping": "smooth",
                    "channel": 4,
                    "instrument": "pad",
                    "bpm": 80
                },
                "position": {"x": 5, "y": 5}
            },
            {
                "id": "midi_7",
                "type": "midi",
                "name": "Percussion Loop",
                "data": {
                    "source_cell": "value_7",
                    "mapping": "random",
                    "channel": 10,
                    "instrument": "percussion",
                    "bpm": 130
                },
                "position": {"x": 5, "y": 6}
            }
        ]
        for cell in midi_cells:
            self.add_cell(cell)
    
    def build_formula_cells(self):
        """Create formula cells."""
        formula_cells = [
            {
                "id": "formula_1",
                "type": "formula",
                "name": "Total Sum",
                "data": {
                    "function": "SUM",
                    "inputs": ["value_1", "value_6"],
                    "output": "sum_result"
                },
                "position": {"x": 6, "y": 0}
            },
            {
                "id": "formula_2",
                "type": "formula",
                "name": "Average Reading",
                "data": {
                    "function": "AVERAGE",
                    "inputs": ["value_1", "value_6", "value_7"],
                    "output": "avg_result"
                },
                "position": {"x": 6, "y": 1}
            },
            {
                "id": "formula_3",
                "type": "formula",
                "name": "Evolution Step",
                "data": {
                    "function": "EVOLVE",
                    "inputs": ["agent_1", "agent_2"],
                    "output": "evolved_agent"
                },
                "position": {"x": 6, "y": 2}
            },
            {
                "id": "formula_4",
                "type": "formula",
                "name": "Species Classification",
                "data": {
                    "function": "SPECIES",
                    "inputs": ["agent_3", "agent_4", "agent_5"],
                    "output": "species_result"
                },
                "position": {"x": 6, "y": 3}
            },
            {
                "id": "formula_5",
                "type": "formula",
                "name": "Pareto Optimization",
                "data": {
                    "function": "PARETO",
                    "inputs": ["agent_1", "agent_2", "agent_3"],
                    "output": "pareto_front"
                },
                "position": {"x": 6, "y": 4}
            },
            {
                "id": "formula_6",
                "type": "formula",
                "name": "Entropy Calculation",
                "data": {
                    "function": "ENTROPY",
                    "inputs": ["value_5", "value_7"],
                    "output": "entropy_value"
                },
                "position": {"x": 6, "y": 5}
            },
            {
                "id": "formula_7",
                "type": "formula",
                "name": "Conservation Check",
                "data": {
                    "function": "CONSERVE",
                    "inputs": ["agent_1", "agent_2", "agent_3"],
                    "output": "conservation_status"
                },
                "position": {"x": 6, "y": 6}
            }
        ]
        for cell in formula_cells:
            self.add_cell(cell)
    
    def build_meta_cells(self):
        """Create meta-cells for conservation law."""
        meta_cells = [
            {
                "id": "conservation_law",
                "type": "meta",
                "name": "Conservation Law: γ + η = budget",
                "description": "DoubleEntry primitive ensuring compute and memory budgets sum to total budget",
                "data": {
                    "equation": "γ + η = budget",
                    "constraint": "gamma + eta == budget",
                    "enforced": True,
                    "violations": 0
                },
                "position": {"x": 7, "y": 0}
            }
        ]
        for meta_cell in meta_cells:
            self.add_meta_cell(meta_cell)
    
    def build_a2a_bus_graph(self):
        """Create the A2A bus as a graph structure."""
        graph = {
            "id": "a2a_bus",
            "type": "graph",
            "name": "A2A Communication Bus",
            "description": "Agent-to-agent communication network",
            "nodes": [
                {"id": "agent_1", "type": "agent"},
                {"id": "agent_2", "type": "agent"},
                {"id": "agent_3", "type": "agent"},
                {"id": "agent_4", "type": "agent"},
                {"id": "agent_5", "type": "agent"},
                {"id": "agent_6", "type": "agent"},
                {"id": "agent_7", "type": "agent"},
                {"id": "a2a_1", "type": "a2a"},
                {"id": "a2a_2", "type": "a2a"},
                {"id": "a2a_3", "type": "a2a"},
                {"id": "a2a_4", "type": "a2a"},
                {"id": "a2a_5", "type": "a2a"},
                {"id": "a2a_6", "type": "a2a"},
                {"id": "a2a_7", "type": "a2a"}
            ],
            "edges": [
                {"from": "agent_1", "to": "a2a_1", "weight": 0.8},
                {"from": "agent_2", "to": "a2a_2", "weight": 0.6},
                {"from": "agent_3", "to": "a2a_3", "weight": 0.7},
                {"from": "agent_4", "to": "a2a_4", "weight": 0.9},
                {"from": "agent_5", "to": "a2a_5", "weight": 0.5},
                {"from": "agent_6", "to": "a2a_6", "weight": 0.4},
                {"from": "agent_7", "to": "a2a_7", "weight": 0.3},
                {"from": "a2a_1", "to": "a2a_2", "weight": 0.2},
                {"from": "a2a_2", "to": "a2a_3", "weight": 0.1},
                {"from": "a2a_3", "to": "a2a_4", "weight": 0.15},
                {"from": "a2a_4", "to": "a2a_5", "weight": 0.25},
                {"from": "a2a_5", "to": "a2a_6", "weight": 0.35},
                {"from": "a2a_6", "to": "a2a_7", "weight": 0.45},
                {"from": "a2a_7", "to": "a2a_1", "weight": 0.55}
            ]
        }
        self.add_graph(graph)
    
    def build_connections(self):
        """Create connections between cells."""
        connections = [
            # Value to MIDI connections
            {"from": "value_1", "to": "midi_1", "type": "sonification"},
            {"from": "value_2", "to": "midi_2", "type": "sonification"},
            {"from": "value_3", "to": "midi_3", "type": "sonification"},
            {"from": "value_4", "to": "midi_4", "type": "sonification"},
            {"from": "value_5", "to": "midi_5", "type": "sonification"},
            {"from": "value_6", "to": "midi_6", "type": "sonification"},
            {"from": "value_7", "to": "midi_7", "type": "sonification"},
            
            # Value to Formula connections
            {"from": "value_1", "to": "formula_1", "type": "input"},
            {"from": "value_6", "to": "formula_1", "type": "input"},
            {"from": "value_1", "to": "formula_2", "type": "input"},
            {"from": "value_6", "to": "formula_2", "type": "input"},
            {"from": "value_7", "to": "formula_2", "type": "input"},
            {"from": "value_5", "to": "formula_6", "type": "input"},
            {"from": "value_7", "to": "formula_6", "type": "input"},
            
            # Agent to Formula connections
            {"from": "agent_1", "to": "formula_3", "type": "input"},
            {"from": "agent_2", "to": "formula_3", "type": "input"},
            {"from": "agent_3", "to": "formula_4", "type": "input"},
            {"from": "agent_4", "to": "formula_4", "type": "input"},
            {"from": "agent_5", "to": "formula_4", "type": "input"},
            {"from": "agent_1", "to": "formula_5", "type": "input"},
            {"from": "agent_2", "to": "formula_5", "type": "input"},
            {"from": "agent_3", "to": "formula_5", "type": "input"},
            
            # Conservation law connections
            {"from": "agent_1", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_2", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_3", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_4", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_5", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_6", "to": "conservation_law", "type": "constraint"},
            {"from": "agent_7", "to": "conservation_law", "type": "constraint"},
            
            # Formula to Formula connections
            {"from": "formula_1", "to": "formula_2", "type": "dependency"},
            {"from": "formula_3", "to": "formula_4", "type": "dependency"},
            {"from": "formula_5", "to": "formula_7", "type": "dependency"}
        ]
        for connection in connections:
            self.add_connection(connection)
    
    def build(self) -> Dict[str, Any]:
        """Build the complete Quilt sheet."""
        # Add cell types
        for cell_type in self.cell_types:
            self.add_cell_type(cell_type)
        
        # Add formulas
        for formula in self.formulas:
            self.add_formula(formula)
        
        # Build all cell types
        self.build_value_cells()
        self.build_agent_cells()
        self.build_training_cells()
        self.build_simulation_cells()
        self.build_a2a_cells()
        self.build_midi_cells()
        self.build_formula_cells()
        
        # Build meta-cells
        self.build_meta_cells()
        
        # Build A2A bus graph
        self.build_a2a_bus_graph()
        
        # Build connections
        self.build_connections()
        
        return self.sheet

def main():
    """Main function to build and save the Quilt sheet."""
    # Create output directory if it doesn't exist
    output_dir = "/workspace/superinstance-website/bridges"
    os.makedirs(output_dir, exist_ok=True)
    
    # Build the Quilt sheet
    builder = QuiltSheetBuilder()
    quilt_sheet = builder.build()
    
    # Save to file
    output_path = os.path.join(output_dir, "spreadsheet-engine-quilt.qzt")
    with open(output_path, 'w') as f:
        json.dump(quilt_sheet, f, indent=2)
    
    print(f"Quilt sheet saved to: {output_path}")
    print(f"Total cells: {len(quilt_sheet['cells'])}")
    print(f"Cell types: {len(quilt_sheet['cell_types'])}")
    print(f"Meta-cells: {len(quilt_sheet['meta_cells'])}")
    print(f"Formulas: {len(quilt_sheet['formulas'])}")
    print(f"Graphs: {len(quilt_sheet['graphs'])}")
    print(f"Connections: {len(quilt_sheet['connections'])}")

if __name__ == "__main__":
    main()
