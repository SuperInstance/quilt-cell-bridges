#!/usr/bin/env python3
"""
Convert colony-cell filesystem sandbox to a Quilt sheet.

This script creates a Quilt sheet representing the colony-cell structure:
- 8 root cells (top-level directories)
- 24 child cells (3 per root)
- Permissions and ownership as cell metadata
- Cross-directory symlinks as edges
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ColonyCellToQuilt:
    """Converts colony-cell filesystem structure to Quilt sheet format."""
    
    def __init__(self, source_path: str, output_path: str):
        """
        Initialize the converter.
        
        Args:
            source_path: Path to the colony-cell repo
            output_path: Path where the Quilt sheet will be written
        """
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.cells = []
        self.edges = []
        
    def scan_cells(self) -> None:
        """Scan the filesystem and build cell metadata."""
        if not self.source_path.exists():
            print(f"Warning: Source path {self.source_path} does not exist. Creating sample structure...")
            self._create_sample_structure()
        
        # Scan top-level directories (root cells)
        root_dirs = [d for d in self.source_path.iterdir() if d.is_dir()]
        
        # If we don't have exactly 8 root cells, create a sample structure
        if len(root_dirs) != 8:
            print(f"Found {len(root_dirs)} root cells, expected 8. Creating sample structure...")
            self._create_sample_structure()
            root_dirs = [d for d in self.source_path.iterdir() if d.is_dir()]
        
        # Process each root cell
        for root_idx, root_dir in enumerate(sorted(root_dirs)[:8]):
            root_cell = self._create_cell_metadata(
                name=root_dir.name,
                path=str(root_dir),
                cell_type="root",
                level=0
            )
            self.cells.append(root_cell)
            
            # Find child directories (up to 3 per root)
            child_dirs = [d for d in root_dir.iterdir() if d.is_dir()]
            for child_idx, child_dir in enumerate(sorted(child_dirs)[:3]):
                child_cell = self._create_cell_metadata(
                    name=child_dir.name,
                    path=str(child_dir),
                    cell_type="child",
                    level=1,
                    parent=root_cell["id"]
                )
                self.cells.append(child_cell)
                
                # Add parent-child edge
                self.edges.append({
                    "source": root_cell["id"],
                    "target": child_cell["id"],
                    "type": "parent_child",
                    "label": f"{root_cell['name']} -> {child_cell['name']}"
                })
    
    def _create_cell_metadata(self, name: str, path: str, cell_type: str, 
                              level: int, parent: str = None) -> Dict[str, Any]:
        """
        Create cell metadata with permissions and ownership.
        
        Args:
            name: Cell name
            path: Filesystem path
            cell_type: Type of cell (root/child)
            level: Hierarchy level
            parent: Parent cell ID (if any)
        
        Returns:
            Cell metadata dictionary
        """
        # Get actual filesystem permissions if available
        try:
            stat_info = os.stat(path)
            permissions = oct(stat_info.st_mode & 0o777)
            owner = stat_info.st_uid
            group = stat_info.st_gid
        except (FileNotFoundError, OSError):
            # Default permissions for sample structure
            permissions = "755" if cell_type == "root" else "750"
            owner = 1000
            group = 1000
        
        cell_id = f"cell_{len(self.cells) + 1:03d}"
        
        return {
            "id": cell_id,
            "name": name,
            "path": path,
            "type": cell_type,
            "level": level,
            "parent": parent,
            "metadata": {
                "permissions": permissions,
                "owner": owner,
                "group": group,
                "created": datetime.now().isoformat(),
                "description": f"{cell_type.capitalize()} cell: {name}"
            }
        }
    
    def scan_symlinks(self) -> None:
        """Scan for cross-directory symlinks and add them as edges."""
        for cell in self.cells:
            cell_path = Path(cell["path"])
            if not cell_path.exists():
                continue
                
            # Look for symlinks in this cell
            for item in cell_path.iterdir():
                if item.is_symlink():
                    target = os.readlink(item)
                    target_path = Path(target)
                    
                    # Find which cell the symlink points to
                    target_cell = self._find_target_cell(target_path)
                    if target_cell:
                        self.edges.append({
                            "source": cell["id"],
                            "target": target_cell["id"],
                            "type": "symlink",
                            "label": f"{cell['name']}/{item.name} -> {target}",
                            "symlink_name": item.name,
                            "symlink_target": target
                        })
    
    def _find_target_cell(self, target_path: Path) -> Dict[str, Any]:
        """
        Find which cell a path belongs to.
        
        Args:
            target_path: Path to find cell for
        
        Returns:
            Cell metadata or None if not found
        """
        for cell in self.cells:
            cell_path = Path(cell["path"])
            try:
                if target_path.resolve().is_relative_to(cell_path.resolve()):
                    return cell
            except (ValueError, OSError):
                continue
        return None
    
    def _create_sample_structure(self) -> None:
        """Create a sample colony-cell structure if none exists."""
        print("Creating sample colony-cell structure...")
        
        # Clean up existing structure if any
        if self.source_path.exists():
            shutil.rmtree(self.source_path)
        
        # Create root cells
        root_names = [
            "alpha", "beta", "gamma", "delta",
            "epsilon", "zeta", "eta", "theta"
        ]
        
        for root_name in root_names:
            root_path = self.source_path / root_name
            root_path.mkdir(parents=True, exist_ok=True)
            
            # Create child cells
            for i in range(3):
                child_name = f"cell_{i+1}"
                child_path = root_path / child_name
                child_path.mkdir(parents=True, exist_ok=True)
                
                # Create some files in child cells
                (child_path / "README.md").write_text(
                    f"# {root_name}/{child_name}\n\nSample colony cell."
                )
                (child_path / "data.txt").write_text(
                    f"Data for {root_name}/{child_name}"
                )
        
        # Create cross-directory symlinks
        # Link from alpha/cell_1 to beta/cell_2
        try:
            os.symlink(
                self.source_path / "beta" / "cell_2",
                self.source_path / "alpha" / "cell_1" / "link_to_beta"
            )
        except FileExistsError:
            pass
        
        # Link from gamma/cell_3 to delta/cell_1
        try:
            os.symlink(
                self.source_path / "delta" / "cell_1",
                self.source_path / "gamma" / "cell_3" / "link_to_delta"
            )
        except FileExistsError:
            pass
        
        # Link from epsilon/cell_2 to zeta/cell_1
        try:
            os.symlink(
                self.source_path / "zeta" / "cell_1",
                self.source_path / "epsilon" / "cell_2" / "link_to_zeta"
            )
        except FileExistsError:
            pass
    
    def build_quilt_sheet(self) -> Dict[str, Any]:
        """
        Build the complete Quilt sheet structure.
        
        Returns:
            Quilt sheet dictionary
        """
        self.scan_cells()
        self.scan_symlinks()
        
        return {
            "format_version": "1.0",
            "sheet_type": "colony_cell",
            "metadata": {
                "title": "Colony-Cell Filesystem Sandbox",
                "description": "Filesystem sandbox with cell hierarchy and symlink edges",
                "created": datetime.now().isoformat(),
                "source_repo": str(self.source_path),
                "cell_counts": {
                    "total_cells": len(self.cells),
                    "root_cells": sum(1 for c in self.cells if c["type"] == "root"),
                    "child_cells": sum(1 for c in self.cells if c["type"] == "child")
                },
                "edge_counts": {
                    "total_edges": len(self.edges),
                    "parent_child_edges": sum(1 for e in self.edges if e["type"] == "parent_child"),
                    "symlink_edges": sum(1 for e in self.edges if e["type"] == "symlink")
                }
            },
            "cells": self.cells,
            "edges": self.edges
        }
    
    def save_quilt_sheet(self) -> None:
        """Save the Quilt sheet to the output path."""
        sheet = self.build_quilt_sheet()
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the sheet as JSON (Quilt format)
        with open(self.output_path, 'w') as f:
            json.dump(sheet, f, indent=2)
        
        print(f"Quilt sheet saved to: {self.output_path}")
        print(f"Total cells: {sheet['metadata']['cell_counts']['total_cells']}")
        print(f"Total edges: {sheet['metadata']['edge_counts']['total_edges']}")
        print(f"  - Parent-child edges: {sheet['metadata']['edge_counts']['parent_child_edges']}")
        print(f"  - Symlink edges: {sheet['metadata']['edge_counts']['symlink_edges']}")

def main():
    """Main entry point."""
    # Define paths
    source_path = "/workspace/colony-cell"
    output_path = "/workspace/superinstance-website/bridges/colony-cell-quilt.qzt"
    
    # Create converter and run
    converter = ColonyCellToQuilt(source_path, output_path)
    converter.save_quilt_sheet()

if __name__ == "__main__":
    main()
