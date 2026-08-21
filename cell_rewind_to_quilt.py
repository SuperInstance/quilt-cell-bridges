#!/usr/bin/env python3
"""
Cell Rewind to Quilt Mapper
Maps the Time-Travel DAW (cell-rewind.html) to a Quilt sheet structure.
Creates a .qzt file with all cells and connections.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class QuiltCell:
    """Represents a single cell in the Quilt sheet."""
    
    def __init__(self, cell_id: str, cell_type: str, name: str, description: str = ""):
        self.cell_id = cell_id
        self.cell_type = cell_type
        self.name = name
        self.description = description
        self.properties: Dict[str, Any] = {}
        self.connections: List[str] = []
    
    def add_property(self, key: str, value: Any):
        """Add a property to the cell."""
        self.properties[key] = value
    
    def add_connection(self, target_cell_id: str, connection_type: str = "data"):
        """Add a connection to another cell."""
        self.connections.append({
            "target": target_cell_id,
            "type": connection_type
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cell to dictionary format."""
        return {
            "id": self.cell_id,
            "type": self.cell_type,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "connections": self.connections
        }

class QuiltSheet:
    """Represents the complete Quilt sheet structure."""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.created_at = datetime.now().isoformat()
        self.cells: Dict[str, QuiltCell] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_cell(self, cell: QuiltCell):
        """Add a cell to the sheet."""
        self.cells[cell.cell_id] = cell
    
    def get_cell(self, cell_id: str) -> QuiltCell:
        """Get a cell by ID."""
        return self.cells.get(cell_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire sheet to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "cells": [cell.to_dict() for cell in self.cells.values()]
        }
    
    def save(self, filepath: str):
        """Save the sheet to a .qzt file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Quilt sheet saved to: {filepath}")

def create_model_cells(sheet: QuiltSheet):
    """Create cells for the 4 LLM models."""
    models = [
        ("model_glm53", "GLM-5.3", "Latest GLM model with advanced reasoning"),
        ("model_glm5", "GLM-5", "GLM-5 model for general tasks"),
        ("model_kimi", "Kimi K3", "Kimi K3 model with specialized capabilities"),
        ("model_deepseek", "DeepSeek V3", "DeepSeek V3 model for deep analysis")
    ]
    
    for model_id, name, desc in models:
        cell = QuiltCell(model_id, "model", name, desc)
        cell.add_property("provider", name.split()[0] if " " in name else name)
        cell.add_property("version", name.split()[-1] if " " in name else "latest")
        cell.add_property("status", "active")
        cell.add_property("capabilities", ["text_generation", "code_generation", "analysis"])
        sheet.add_cell(cell)

def create_keyboard_cells(sheet: QuiltSheet):
    """Create cells for keyboard shortcuts."""
    shortcuts = [
        ("key_space", "Space", "Play/Pause timeline", "play_pause"),
        ("key_b", "B", "Bookmark current position", "bookmark"),
        ("key_r", "R", "Rewind to previous bookmark", "rewind"),
        ("key_g", "G", "Regenerate current event", "regenerate"),
        ("key_1", "1", "Switch to DAW view", "view_daw"),
        ("key_2", "2", "Switch to Front (theater) view", "view_front"),
        ("key_3", "3", "Switch to Top (spatial) view", "view_top")
    ]
    
    for key_id, key_name, desc, action in shortcuts:
        cell = QuiltCell(key_id, "keyboard", f"Key {key_name}", desc)
        cell.add_property("key", key_name)
        cell.add_property("action", action)
        cell.add_property("category", "shortcut")
        sheet.add_cell(cell)

def create_view_cells(sheet: QuiltSheet):
    """Create cells for the 3 views."""
    views = [
        ("view_daw", "DAW View", "Main timeline view with tracks and events"),
        ("view_front", "Front (Theater)", "Theater-style presentation view"),
        ("view_top", "Top (Spatial)", "Spatial/top-down view of the composition")
    ]
    
    for view_id, name, desc in views:
        cell = QuiltCell(view_id, "view", name, desc)
        cell.add_property("view_type", view_id.split("_")[1])
        cell.add_property("is_active", False)
        cell.add_property("render_mode", "canvas")
        sheet.add_cell(cell)

def create_operation_cells(sheet: QuiltSheet):
    """Create cells for operations."""
    operations = [
        ("op_bookmark", "Bookmark", "Save current position as bookmark"),
        ("op_rewind", "Rewind", "Jump back to previous bookmark"),
        ("op_regenerate", "Regenerate", "Regenerate current event with selected model"),
        ("op_cascade", "Cascade Preview", "Preview cascading changes across timeline")
    ]
    
    for op_id, name, desc in operations:
        cell = QuiltCell(op_id, "operation", name, desc)
        cell.add_property("operation_type", op_id.split("_")[1])
        cell.add_property("is_async", True)
        cell.add_property("undoable", True)
        sheet.add_cell(cell)

def create_audio_cells(sheet: QuiltSheet):
    """Create cells for audio input/output."""
    # STT Input cell
    stt_cell = QuiltCell("audio_stt", "audio_input", "STT Voice Input", 
                        "Live speech-to-text for voice commands")
    stt_cell.add_property("input_type", "microphone")
    stt_cell.add_property("processing", "real_time")
    stt_cell.add_property("language", "en")
    stt_cell.add_property("commands_enabled", True)
    sheet.add_cell(stt_cell)
    
    # TTS Output cell
    tts_cell = QuiltCell("audio_tts", "audio_output", "TTS Voice Output",
                        "Text-to-speech for audio feedback")
    tts_cell.add_property("output_type", "speaker")
    tts_cell.add_property("voice", "default")
    tts_cell.add_property("rate", 1.0)
    tts_cell.add_property("pitch", 1.0)
    sheet.add_cell(tts_cell)

def create_connections(sheet: QuiltSheet):
    """Create all connections between cells."""
    
    # Connect keyboard shortcuts to operations
    keyboard_to_operation = {
        "key_space": "op_bookmark",  # Space also acts as bookmark in some contexts
        "key_b": "op_bookmark",
        "key_r": "op_rewind",
        "key_g": "op_regenerate"
    }
    
    for key_id, op_id in keyboard_to_operation.items():
        key_cell = sheet.get_cell(key_id)
        if key_cell:
            key_cell.add_connection(op_id, "trigger")
    
    # Connect keyboard shortcuts to views
    keyboard_to_view = {
        "key_1": "view_daw",
        "key_2": "view_front",
        "key_3": "view_top"
    }
    
    for key_id, view_id in keyboard_to_view.items():
        key_cell = sheet.get_cell(key_id)
        if key_cell:
            key_cell.add_connection(view_id, "switch_view")
    
    # Connect models to operations (models can be used for regeneration)
    model_ids = ["model_glm53", "model_glm5", "model_kimi", "model_deepseek"]
    for model_id in model_ids:
        model_cell = sheet.get_cell(model_id)
        if model_cell:
            model_cell.add_connection("op_regenerate", "model_used")
            model_cell.add_connection("op_cascade", "model_used")
    
    # Connect operations to views (operations affect views)
    op_to_view = {
        "op_bookmark": ["view_daw", "view_front", "view_top"],
        "op_rewind": ["view_daw", "view_front", "view_top"],
        "op_regenerate": ["view_daw", "view_front", "view_top"],
        "op_cascade": ["view_daw", "view_front", "view_top"]
    }
    
    for op_id, view_ids in op_to_view.items():
        op_cell = sheet.get_cell(op_id)
        if op_cell:
            for view_id in view_ids:
                op_cell.add_connection(view_id, "updates")
    
    # Connect audio cells
    stt_cell = sheet.get_cell("audio_stt")
    if stt_cell:
        # STT connects to operations for voice commands
        stt_cell.add_connection("op_bookmark", "voice_command")
        stt_cell.add_connection("op_rewind", "voice_command")
        stt_cell.add_connection("op_regenerate", "voice_command")
        stt_cell.add_connection("op_cascade", "voice_command")
        # STT connects to views for view switching
        stt_cell.add_connection("view_daw", "voice_command")
        stt_cell.add_connection("view_front", "voice_command")
        stt_cell.add_connection("view_top", "voice_command")
    
    tts_cell = sheet.get_cell("audio_tts")
    if tts_cell:
        # Operations connect to TTS for audio feedback
        for op_id in ["op_bookmark", "op_rewind", "op_regenerate", "op_cascade"]:
            op_cell = sheet.get_cell(op_id)
            if op_cell:
                op_cell.add_connection("audio_tts", "audio_feedback")
        
        # Views connect to TTS for audio descriptions
        for view_id in ["view_daw", "view_front", "view_top"]:
            view_cell = sheet.get_cell(view_id)
            if view_cell:
                view_cell.add_connection("audio_tts", "audio_description")

def add_sheet_metadata(sheet: QuiltSheet):
    """Add metadata about the source system."""
    sheet.metadata = {
        "source": "cell-rewind.html",
        "source_type": "Time-Travel DAW",
        "description": "Mapping of Time-Travel DAW to Quilt sheet",
        "features": [
            "multi_model_system",
            "bookmark_rewind",
            "cascade_preview",
            "per_event_regeneration",
            "multiple_views",
            "voice_commands",
            "audio_feedback"
        ],
        "models": ["GLM-5.3", "GLM-5", "Kimi K3", "DeepSeek V3"],
        "views": ["DAW", "Front (Theater)", "Top (Spatial)"],
        "keyboard_shortcuts": {
            "space": "play",
            "b": "bookmark",
            "r": "rewind",
            "g": "regenerate",
            "1": "DAW view",
            "2": "Front view",
            "3": "Top view"
        }
    }

def main():
    """Main function to build and save the Quilt sheet."""
    print("Building Time-Travel DAW Quilt sheet...")
    
    # Create the sheet
    sheet = QuiltSheet("Time-Travel DAW Quilt", version="1.0")
    
    # Add all cell types
    print("Creating model cells...")
    create_model_cells(sheet)
    
    print("Creating keyboard cells...")
    create_keyboard_cells(sheet)
    
    print("Creating view cells...")
    create_view_cells(sheet)
    
    print("Creating operation cells...")
    create_operation_cells(sheet)
    
    print("Creating audio cells...")
    create_audio_cells(sheet)
    
    print("Creating connections...")
    create_connections(sheet)
    
    print("Adding metadata...")
    add_sheet_metadata(sheet)
    
    # Save the sheet
    output_path = "/workspace/superinstance-website/bridges/cell-rewind-quilt.qzt"
    sheet.save(output_path)
    
    # Print summary
    print(f"\nQuilt sheet created successfully!")
    print(f"Total cells: {len(sheet.cells)}")
    print(f"Cell types: {len(set(cell.cell_type for cell in sheet.cells.values()))}")
    
    # Print cell summary
    print("\nCell summary:")
    for cell_id, cell in sheet.cells.items():
        print(f"  - {cell_id}: {cell.name} ({cell.cell_type})")
    
    print(f"\nOutput file: {output_path}")

if __name__ == "__main__":
    main()
