#!/usr/bin/env python3
"""
Temporal Heartbeat to Quilt Converter
Converts a temporal-heartbeat system (BPM clocks, deadlines, cron timers, watchdogs)
into a Quilt sheet with proper dependencies and structure.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

class TemporalHeartbeatToQuilt:
    """Converts temporal-heartbeat system to Quilt sheet format."""
    
    def __init__(self):
        self.sheet = {
            "version": "1.0",
            "type": "temporal-heartbeat",
            "metadata": {
                "created": datetime.utcnow().isoformat() + "Z",
                "description": "Temporal heartbeat system converted to Quilt sheet",
                "system_type": "temporal-heartbeat"
            },
            "cells": [],
            "edges": [],
            "layout": {
                "grid_size": [12, 8],
                "cell_spacing": 1.0
            }
        }
        
        # Track cell IDs for edge creation
        self.cell_ids = {}
        self.cell_counter = 0
        
    def add_cell(self, cell_type: str, name: str, properties: Dict[str, Any], 
                 position: List[int]) -> str:
        """Add a cell to the sheet and return its ID."""
        cell_id = f"cell_{self.cell_counter:04d}"
        self.cell_counter += 1
        
        cell = {
            "id": cell_id,
            "type": cell_type,
            "name": name,
            "properties": properties,
            "position": position,
            "state": {
                "status": "active",
                "last_heartbeat": None,
                "health": "unknown"
            }
        }
        
        self.sheet["cells"].append(cell)
        self.cell_ids[name] = cell_id
        return cell_id
    
    def add_edge(self, source: str, target: str, edge_type: str = "dependency",
                 properties: Dict[str, Any] = None) -> None:
        """Add an edge between two cells."""
        if source not in self.cell_ids or target not in self.cell_ids:
            raise ValueError(f"Source or target cell not found: {source} -> {target}")
        
        edge = {
            "id": f"edge_{len(self.sheet['edges']):04d}",
            "source": self.cell_ids[source],
            "target": self.cell_ids[target],
            "type": edge_type,
            "properties": properties or {}
        }
        self.sheet["edges"].append(edge)
    
    def build_bpm_clocks(self) -> None:
        """Create 6 BPM clock cells."""
        bpm_values = [60, 90, 120, 150, 180, 240]
        positions = [(0, i) for i in range(6)]
        
        for idx, bpm in enumerate(bpm_values):
            self.add_cell(
                "bpm_clock",
                f"BPM_{bpm}",
                {
                    "bpm": bpm,
                    "beat_interval_ms": 60000 / bpm,
                    "precision": "high",
                    "sync_source": "internal"
                },
                positions[idx]
            )
    
    def build_deadlines(self) -> None:
        """Create 12 deadline cells (one per hour)."""
        for hour in range(12):
            deadline_time = f"{hour:02d}:00:00"
            self.add_cell(
                "deadline",
                f"Deadline_{hour:02d}h",
                {
                    "hour": hour,
                    "deadline_time": deadline_time,
                    "timezone": "UTC",
                    "grace_period_seconds": 300,
                    "action": "check_completion"
                },
                [1, hour % 6]
            )
    
    def build_cron_timers(self) -> None:
        """Create 24 cron cells (one per hour, daily)."""
        for hour in range(24):
            cron_expression = f"0 {hour} * * *"
            self.add_cell(
                "cron_timer",
                f"Cron_{hour:02d}h",
                {
                    "hour": hour,
                    "cron_expression": cron_expression,
                    "schedule": f"Daily at {hour:02d}:00",
                    "timezone": "UTC",
                    "repeat": "daily"
                },
                [2, hour % 8]
            )
    
    def build_watchdogs(self) -> None:
        """Create 4 watchdog cells for heartbeat health checks."""
        watchdog_configs = [
            ("Watchdog_BPM", "bpm_clock", 60, "Monitor BPM clock health"),
            ("Watchdog_Deadline", "deadline", 300, "Monitor deadline compliance"),
            ("Watchdog_Cron", "cron_timer", 3600, "Monitor cron execution"),
            ("Watchdog_System", "system", 60, "Overall system health")
        ]
        
        for idx, (name, monitor_type, interval, desc) in enumerate(watchdog_configs):
            self.add_cell(
                "watchdog",
                name,
                {
                    "monitor_type": monitor_type,
                    "check_interval_seconds": interval,
                    "timeout_seconds": interval * 2,
                    "description": desc,
                    "alert_threshold": 3,
                    "recovery_action": "restart"
                },
                [3, idx]
            )
    
    def build_edges(self) -> None:
        """Create dependency edges between cells."""
        
        # BPM clocks feed into deadlines (each BPM clock monitors deadlines)
        bpm_cells = [f"BPM_{bpm}" for bpm in [60, 90, 120, 150, 180, 240]]
        deadline_cells = [f"Deadline_{hour:02d}h" for hour in range(12)]
        
        # Each BPM clock monitors 2 deadlines
        for i, bpm_cell in enumerate(bpm_cells):
            for j in range(2):
                deadline_idx = (i * 2 + j) % 12
                self.add_edge(
                    bpm_cell,
                    deadline_cells[deadline_idx],
                    "monitors",
                    {"monitoring_type": "deadline", "priority": "high"}
                )
        
        # Cron timers depend on BPM clocks for timing
        cron_cells = [f"Cron_{hour:02d}h" for hour in range(24)]
        for i, cron_cell in enumerate(cron_cells):
            bpm_idx = i % 6
            self.add_edge(
                bpm_cells[bpm_idx],
                cron_cell,
                "timing_source",
                {"sync_type": "bpm", "precision": "high"}
            )
        
        # Deadlines depend on cron timers (deadlines are checked after cron jobs)
        for i, deadline_cell in enumerate(deadline_cells):
            cron_idx = (i * 2) % 24
            self.add_edge(
                cron_cells[cron_idx],
                deadline_cell,
                "triggers_check",
                {"check_type": "deadline_compliance"}
            )
        
        # Watchdogs monitor their respective systems
        watchdog_edges = [
            ("Watchdog_BPM", bpm_cells, "monitors_heartbeat"),
            ("Watchdog_Deadline", deadline_cells, "monitors_compliance"),
            ("Watchdog_Cron", cron_cells, "monitors_execution"),
            ("Watchdog_System", bpm_cells + deadline_cells + cron_cells, "system_health")
        ]
        
        for watchdog, targets, edge_type in watchdog_edges:
            for target in targets:
                self.add_edge(
                    watchdog,
                    target,
                    edge_type,
                    {"check_interval": "continuous", "alert_on_failure": True}
                )
        
        # Cross-dependencies between watchdogs
        self.add_edge("Watchdog_BPM", "Watchdog_Deadline", "health_dependency",
                     {"description": "BPM health affects deadline monitoring"})
        self.add_edge("Watchdog_Deadline", "Watchdog_Cron", "health_dependency",
                     {"description": "Deadline compliance affects cron scheduling"})
        self.add_edge("Watchdog_Cron", "Watchdog_System", "health_dependency",
                     {"description": "Cron health affects overall system"})
    
    def generate_quilt_sheet(self) -> Dict[str, Any]:
        """Generate the complete Quilt sheet."""
        self.build_bpm_clocks()
        self.build_deadlines()
        self.build_cron_timers()
        self.build_watchdogs()
        self.build_edges()
        
        # Add summary statistics
        self.sheet["metadata"]["statistics"] = {
            "total_cells": len(self.sheet["cells"]),
            "total_edges": len(self.sheet["edges"]),
            "bpm_clocks": 6,
            "deadlines": 12,
            "cron_timers": 24,
            "watchdogs": 4
        }
        
        return self.sheet
    
    def save_to_file(self, filepath: str) -> None:
        """Save the Quilt sheet to a file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.sheet, f, indent=2)
        
        print(f"Quilt sheet saved to: {filepath}")
        print(f"Total cells: {self.sheet['metadata']['statistics']['total_cells']}")
        print(f"Total edges: {self.sheet['metadata']['statistics']['total_edges']}")

def main():
    """Main execution function."""
    converter = TemporalHeartbeatToQuilt()
    
    # Generate the Quilt sheet
    sheet = converter.generate_quilt_sheet()
    
    # Save to file
    output_path = "/workspace/superinstance-website/bridges/temporal-heartbeat-quilt.qzt"
    converter.save_to_file(output_path)
    
    # Print summary
    print("\n=== Temporal Heartbeat to Quilt Conversion Summary ===")
    print(f"BPM Clocks: {sheet['metadata']['statistics']['bpm_clocks']}")
    print(f"Deadlines: {sheet['metadata']['statistics']['deadlines']}")
    print(f"Cron Timers: {sheet['metadata']['statistics']['cron_timers']}")
    print(f"Watchdogs: {sheet['metadata']['statistics']['watchdogs']}")
    print(f"Total Cells: {sheet['metadata']['statistics']['total_cells']}")
    print(f"Total Edges: {sheet['metadata']['statistics']['total_edges']}")
    print("\nCell Types:")
    
    # Count cells by type
    cell_types = {}
    for cell in sheet['cells']:
        cell_type = cell['type']
        cell_types[cell_type] = cell_types.get(cell_type, 0) + 1
    
    for cell_type, count in cell_types.items():
        print(f"  - {cell_type}: {count}")
    
    print("\nEdge Types:")
    edge_types = {}
    for edge in sheet['edges']:
        edge_type = edge['type']
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    for edge_type, count in edge_types.items():
        print(f"  - {edge_type}: {count}")

if __name__ == "__main__":
    main()
