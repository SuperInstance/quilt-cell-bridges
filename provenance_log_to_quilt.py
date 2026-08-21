#!/usr/bin/env python3
"""
Convert provenance-log repo to a Quilt sheet.

This script reads provenance-log entries and creates a Quilt sheet (.qzt)
that visualizes the hash-chained structure of the log.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any

class ProvenanceLogConverter:
    """Converts provenance-log data to Quilt sheet format."""
    
    def __init__(self):
        self.entries = []
        self.quilt_data = {
            "metadata": {
                "format_version": "1.0",
                "description": "Hash-chained provenance log as Quilt sheet",
                "created": datetime.now().isoformat(),
                "chain_type": "hash-linked"
            },
            "cells": [],
            "connections": []
        }
    
    def generate_sample_entries(self, count: int = 8) -> List[Dict[str, Any]]:
        """Generate sample provenance log entries for demonstration."""
        entries = []
        prev_hash = "0" * 64  # Genesis block hash
        
        for i in range(count):
            timestamp = datetime.now().isoformat()
            value = f"Provenance event {i+1}: Data transformation step"
            
            # Create entry data
            entry_data = {
                "timestamp": timestamp,
                "value": value,
                "prev_hash": prev_hash
            }
            
            # Calculate this hash (simplified for demo)
            hash_input = f"{timestamp}{value}{prev_hash}".encode()
            this_hash = hashlib.sha256(hash_input).hexdigest()
            
            # Generate a mock signature (in real implementation, this would be a real signature)
            signature = f"sig_{this_hash[:16]}"
            
            entry = {
                "timestamp": timestamp,
                "value": value,
                "prev_hash": prev_hash,
                "this_hash": this_hash,
                "signature": signature
            }
            
            entries.append(entry)
            prev_hash = this_hash
            
        return entries
    
    def load_entries(self, log_file: str = None) -> List[Dict[str, Any]]:
        """Load provenance log entries from file or generate samples."""
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
        else:
            print("No log file found, generating sample entries...")
            return self.generate_sample_entries()
    
    def create_quilt_cells(self, entries: List[Dict[str, Any]]) -> None:
        """Create Quilt cells from provenance log entries."""
        for i, entry in enumerate(entries):
            cell = {
                "id": f"cell_{i}",
                "type": "provenance_entry",
                "position": {
                    "x": i * 200,  # Horizontal layout
                    "y": 100
                },
                "content": {
                    "timestamp": entry["timestamp"],
                    "value": entry["value"],
                    "prev_hash": entry["prev_hash"][:16] + "...",  # Truncated for display
                    "this_hash": entry["this_hash"][:16] + "...",  # Truncated for display
                    "signature": entry["signature"][:20] + "..."
                },
                "style": {
                    "background": "#f0f8ff",  # Light blue background
                    "border": "2px solid #4682b4",
                    "border_radius": "8px",
                    "padding": "10px"
                }
            }
            self.quilt_data["cells"].append(cell)
    
    def create_quilt_connections(self, entries: List[Dict[str, Any]]) -> None:
        """Create connections between cells to show the hash chain."""
        for i in range(len(entries) - 1):
            connection = {
                "from": f"cell_{i}",
                "to": f"cell_{i+1}",
                "type": "hash_chain",
                "label": f"hash: {entries[i+1]['prev_hash'][:8]}...",
                "style": {
                    "stroke": "#4682b4",
                    "stroke_width": 2,
                    "arrow": "forward"
                }
            }
            self.quilt_data["connections"].append(connection)
    
    def validate_chain(self, entries: List[Dict[str, Any]]) -> bool:
        """Validate the hash chain integrity."""
        for i in range(1, len(entries)):
            if entries[i]["prev_hash"] != entries[i-1]["this_hash"]:
                print(f"Chain validation failed at entry {i}")
                return False
        print("Chain validation successful")
        return True
    
    def convert(self, input_file: str = None, output_file: str = None) -> bool:
        """Main conversion method."""
        # Set default output path
        if output_file is None:
            output_file = "/workspace/superinstance-website/bridges/provenance-log-quilt.qzt"
        
        # Load entries
        self.entries = self.load_entries(input_file)
        
        # Validate the chain
        if not self.validate_chain(self.entries):
            print("Warning: Chain validation failed, but continuing...")
        
        # Create Quilt structure
        self.create_quilt_cells(self.entries)
        self.create_quilt_connections(self.entries)
        
        # Add summary statistics
        self.quilt_data["metadata"]["entry_count"] = len(self.entries)
        self.quilt_data["metadata"]["chain_valid"] = self.validate_chain(self.entries)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                json.dump(self.quilt_data, f, indent=2)
            print(f"Successfully created Quilt sheet at: {output_file}")
            print(f"Total entries: {len(self.entries)}")
            print(f"Total cells: {len(self.quilt_data['cells'])}")
            print(f"Total connections: {len(self.quilt_data['connections'])}")
            return True
        except Exception as e:
            print(f"Error writing Quilt file: {e}")
            return False

def main():
    """Main execution function."""
    converter = ProvenanceLogConverter()
    
    # Check for existing provenance log file
    log_file = "/workspace/provenance-log/entries.json"
    
    # Convert and generate Quilt sheet
    success = converter.convert(
        input_file=log_file if os.path.exists(log_file) else None,
        output_file="/workspace/superinstance-website/bridges/provenance-log-quilt.qzt"
    )
    
    if success:
        print("\nQuilt sheet generation complete!")
        print("The sheet shows:")
        print("  - Each provenance entry as a cell")
        print("  - Hash chain connections between consecutive entries")
        print("  - Full metadata including timestamps and signatures")
    else:
        print("Failed to generate Quilt sheet")

if __name__ == "__main__":
    main()
