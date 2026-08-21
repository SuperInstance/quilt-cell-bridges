#!/usr/bin/env python3
"""
Convert quilt-flow package to a Quilt sheet.

This script analyzes the quilt-flow dataflow engine primitives and generates
a Quilt sheet (.qzt) file that captures the cell graph, states, methods,
and transitions for each primitive type.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class QuiltFlowConverter:
    """Converts quilt-flow primitives to a Quilt sheet format."""
    
    def __init__(self):
        self.cells = []
        self.cell_graph = {
            "nodes": [],
            "edges": []
        }
        
    def create_source_cell(self) -> Dict[str, Any]:
        """Create a Source cell definition."""
        return {
            "id": "source",
            "type": "Source",
            "description": "A cell that produces values",
            "state": {
                "producing": "Currently producing values",
                "idle": "Not producing values",
                "error": "Error in production"
            },
            "methods": [
                {"name": "produce", "description": "Produce a value", "transition": "idle -> producing"},
                {"name": "stop", "description": "Stop producing", "transition": "producing -> idle"},
                {"name": "error", "description": "Handle production error", "transition": "producing -> error"}
            ],
            "transitions": [
                {"from": "idle", "to": "producing", "trigger": "produce"},
                {"from": "producing", "to": "idle", "trigger": "stop"},
                {"from": "producing", "to": "error", "trigger": "error"},
                {"from": "error", "to": "idle", "trigger": "reset"}
            ]
        }
    
    def create_sink_cell(self) -> Dict[str, Any]:
        """Create a Sink cell definition."""
        return {
            "id": "sink",
            "type": "Sink",
            "description": "A cell that consumes values",
            "state": {
                "consuming": "Currently consuming values",
                "idle": "Waiting for values",
                "error": "Error in consumption"
            },
            "methods": [
                {"name": "consume", "description": "Consume a value", "transition": "idle -> consuming"},
                {"name": "pause", "description": "Pause consumption", "transition": "consuming -> idle"},
                {"name": "error", "description": "Handle consumption error", "transition": "consuming -> error"}
            ],
            "transitions": [
                {"from": "idle", "to": "consuming", "trigger": "consume"},
                {"from": "consuming", "to": "idle", "trigger": "pause"},
                {"from": "consuming", "to": "error", "trigger": "error"},
                {"from": "error", "to": "idle", "trigger": "reset"}
            ]
        }
    
    def create_filter_cell(self) -> Dict[str, Any]:
        """Create a Filter cell definition."""
        return {
            "id": "filter",
            "type": "Filter",
            "description": "A cell that transforms values",
            "state": {
                "transforming": "Currently transforming values",
                "idle": "Waiting for values",
                "error": "Error in transformation"
            },
            "methods": [
                {"name": "transform", "description": "Transform a value", "transition": "idle -> transforming"},
                {"name": "pass_through", "description": "Pass value without transformation", "transition": "idle -> idle"},
                {"name": "error", "description": "Handle transformation error", "transition": "transforming -> error"}
            ],
            "transitions": [
                {"from": "idle", "to": "transforming", "trigger": "transform"},
                {"from": "transforming", "to": "idle", "trigger": "complete"},
                {"from": "transforming", "to": "error", "trigger": "error"},
                {"from": "error", "to": "idle", "trigger": "reset"}
            ]
        }
    
    def create_junction_cell(self) -> Dict[str, Any]:
        """Create a Junction cell definition."""
        return {
            "id": "junction",
            "type": "Junction",
            "description": "A cell that splits or merges values",
            "state": {
                "splitting": "Splitting values to multiple outputs",
                "merging": "Merging values from multiple inputs",
                "idle": "Waiting for values",
                "error": "Error in junction operation"
            },
            "methods": [
                {"name": "split", "description": "Split value to multiple outputs", "transition": "idle -> splitting"},
                {"name": "merge", "description": "Merge values from multiple inputs", "transition": "idle -> merging"},
                {"name": "error", "description": "Handle junction error", "transition": "splitting/merging -> error"}
            ],
            "transitions": [
                {"from": "idle", "to": "splitting", "trigger": "split"},
                {"from": "idle", "to": "merging", "trigger": "merge"},
                {"from": "splitting", "to": "idle", "trigger": "complete"},
                {"from": "merging", "to": "idle", "trigger": "complete"},
                {"from": "splitting", "to": "error", "trigger": "error"},
                {"from": "merging", "to": "error", "trigger": "error"},
                {"from": "error", "to": "idle", "trigger": "reset"}
            ]
        }
    
    def create_buffer_cell(self) -> Dict[str, Any]:
        """Create a Buffer cell definition."""
        return {
            "id": "buffer",
            "type": "Buffer",
            "description": "A cell that queues values",
            "state": {
                "buffering": "Currently buffering values",
                "empty": "Buffer is empty",
                "full": "Buffer is full",
                "error": "Error in buffering"
            },
            "methods": [
                {"name": "enqueue", "description": "Add value to buffer", "transition": "empty/buffering -> buffering"},
                {"name": "dequeue", "description": "Remove value from buffer", "transition": "buffering/full -> buffering"},
                {"name": "clear", "description": "Clear the buffer", "transition": "any -> empty"},
                {"name": "error", "description": "Handle buffer error", "transition": "any -> error"}
            ],
            "transitions": [
                {"from": "empty", "to": "buffering", "trigger": "enqueue"},
                {"from": "buffering", "to": "buffering", "trigger": "enqueue/dequeue"},
                {"from": "buffering", "to": "full", "trigger": "buffer_full"},
                {"from": "full", "to": "buffering", "trigger": "dequeue"},
                {"from": "any", "to": "empty", "trigger": "clear"},
                {"from": "any", "to": "error", "trigger": "error"},
                {"from": "error", "to": "empty", "trigger": "reset"}
            ]
        }
    
    def create_throttle_cell(self) -> Dict[str, Any]:
        """Create a Throttle cell definition."""
        return {
            "id": "throttle",
            "type": "Throttle",
            "description": "A cell that rate-limits values",
            "state": {
                "throttling": "Currently rate-limiting values",
                "idle": "Waiting for values",
                "limited": "Rate limit reached",
                "error": "Error in throttling"
            },
            "methods": [
                {"name": "process", "description": "Process a value within rate limit", "transition": "idle -> throttling"},
                {"name": "limit", "description": "Apply rate limit", "transition": "throttling -> limited"},
                {"name": "release", "description": "Release rate limit", "transition": "limited -> throttling"},
                {"name": "error", "description": "Handle throttle error", "transition": "any -> error"}
            ],
            "transitions": [
                {"from": "idle", "to": "throttling", "trigger": "process"},
                {"from": "throttling", "to": "limited", "trigger": "rate_limit_reached"},
                {"from": "limited", "to": "throttling", "trigger": "release"},
                {"from": "throttling", "to": "idle", "trigger": "complete"},
                {"from": "any", "to": "error", "trigger": "error"},
                {"from": "error", "to": "idle", "trigger": "reset"}
            ]
        }
    
    def build_cell_graph(self) -> None:
        """Build the cell graph with nodes and edges."""
        # Define the cell types and their connections
        cell_types = ["source", "filter", "junction", "buffer", "throttle", "sink"]
        
        # Add nodes to the graph
        for cell_type in cell_types:
            self.cell_graph["nodes"].append({
                "id": cell_type,
                "type": cell_type,
                "label": cell_type.capitalize()
            })
        
        # Define edges (data flow connections)
        edges = [
            ("source", "filter", "data_flow"),
            ("source", "buffer", "data_flow"),
            ("filter", "junction", "data_flow"),
            ("filter", "sink", "data_flow"),
            ("junction", "buffer", "data_flow"),
            ("junction", "throttle", "data_flow"),
            ("buffer", "throttle", "data_flow"),
            ("buffer", "sink", "data_flow"),
            ("throttle", "sink", "data_flow")
        ]
        
        for source, target, edge_type in edges:
            self.cell_graph["edges"].append({
                "source": source,
                "target": target,
                "type": edge_type,
                "label": f"{source} -> {target}"
            })
    
    def generate_quilt_sheet(self) -> Dict[str, Any]:
        """Generate the complete Quilt sheet structure."""
        # Build all cell definitions
        self.cells = [
            self.create_source_cell(),
            self.create_sink_cell(),
            self.create_filter_cell(),
            self.create_junction_cell(),
            self.create_buffer_cell(),
            self.create_throttle_cell()
        ]
        
        # Build the cell graph
        self.build_cell_graph()
        
        # Create the complete Quilt sheet
        quilt_sheet = {
            "metadata": {
                "format": "quilt-sheet",
                "version": "1.0",
                "generated": datetime.utcnow().isoformat() + "Z",
                "source": "quilt-flow",
                "description": "Quilt-flow dataflow engine primitives converted to Quilt sheet format"
            },
            "cells": self.cells,
            "graph": self.cell_graph,
            "connections": {
                "source_to_sink": "Data flows from sources through filters/junctions to sinks",
                "buffering": "Buffers provide queuing between cells",
                "throttling": "Throttles control rate of data flow"
            }
        }
        
        return quilt_sheet
    
    def save_to_file(self, output_path: str) -> None:
        """Save the Quilt sheet to a file."""
        quilt_sheet = self.generate_quilt_sheet()
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the Quilt sheet as JSON
        with open(output_path, 'w') as f:
            json.dump(quilt_sheet, f, indent=2)
        
        print(f"Quilt sheet saved to: {output_path}")
        print(f"Generated {len(self.cells)} cell definitions")
        print(f"Graph contains {len(self.cell_graph['nodes'])} nodes and {len(self.cell_graph['edges'])} edges")

def main():
    """Main entry point for the converter."""
    # Define output path
    output_path = "/workspace/superinstance-website/bridges/quilt-flow-quilt.qzt"
    
    # Create converter instance
    converter = QuiltFlowConverter()
    
    # Generate and save the Quilt sheet
    converter.save_to_file(output_path)
    
    # Print summary
    print("\nQuilt-flow to Quilt sheet conversion complete!")
    print("=" * 50)
    print("Primitives converted:")
    print("  - Source: Produces values")
    print("  - Sink: Consumes values")
    print("  - Filter: Transforms values")
    print("  - Junction: Splits/merges values")
    print("  - Buffer: Queues values")
    print("  - Throttle: Rate-limits values")
    print("=" * 50)

if __name__ == "__main__":
    main()
