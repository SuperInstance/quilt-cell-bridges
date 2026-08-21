#!/usr/bin/env python3
"""
Bridge converter: othismos-reef knowledge graph -> Quilt sheet (.qzt)

Converts a knowledge graph (concepts as nodes, relationships as edges) into
a Quilt sheet format. Each concept becomes a cell, each relationship becomes
an edge. The output is a JSON-based .qzt file with the following structure:

{
  "format": "quilt-sheet",
  "version": "1.0",
  "metadata": {...},
  "cells": [...],
  "edges": [...]
}

Cells have:
  - id: unique identifier
  - label: human-readable name
  - category: one of entity, attribute, action, state, relation

Edges have:
  - source: source cell id
  - target: target cell id
  - type: one of is-a, has-a, causes, prevents, precedes, follows
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Categories and relationship types as specified
CATEGORIES = ["entity", "attribute", "action", "state", "relation"]
RELATIONSHIP_TYPES = ["is-a", "has-a", "causes", "prevents", "precedes", "follows"]

# Output path
OUTPUT_PATH = "/workspace/superinstance-website/bridges/othismos-reef-quilt.qzt"

# ---------------------------------------------------------------------------
# Sample data: 20 concepts and 30 relationships
# ---------------------------------------------------------------------------

# Each concept: (id, label, category)
CONCEPTS: List[Dict[str, str]] = [
    # Entities (5)
    {"id": "c01", "label": "Ocean", "category": "entity"},
    {"id": "c02", "label": "Coral Reef", "category": "entity"},
    {"id": "c03", "label": "Fish", "category": "entity"},
    {"id": "c04", "label": "Algae", "category": "entity"},
    {"id": "c05", "label": "Water", "category": "entity"},
    # Attributes (4)
    {"id": "c06", "label": "Salinity", "category": "attribute"},
    {"id": "c07", "label": "Temperature", "category": "attribute"},
    {"id": "c08", "label": "Depth", "category": "attribute"},
    {"id": "c09", "label": "Clarity", "category": "attribute"},
    # Actions (4)
    {"id": "c10", "label": "Photosynthesis", "category": "action"},
    {"id": "c11", "label": "Predation", "category": "action"},
    {"id": "c12", "label": "Symbiosis", "category": "action"},
    {"id": "c13", "label": "Migration", "category": "action"},
    # States (4)
    {"id": "c14", "label": "Healthy", "category": "state"},
    {"id": "c15", "label": "Bleached", "category": "state"},
    {"id": "c16", "label": "Overfished", "category": "state"},
    {"id": "c17", "label": "Nutrient-rich", "category": "state"},
    # Relations (3)
    {"id": "c18", "label": "Part of", "category": "relation"},
    {"id": "c19", "label": "Depends on", "category": "relation"},
    {"id": "c20", "label": "Threatens", "category": "relation"},
]

# Each relationship: (source_id, target_id, type)
# We'll create 30 edges covering all 6 relationship types (5 each)
RELATIONSHIPS: List[Dict[str, str]] = [
    # is-a (5)
    {"source": "c02", "target": "c01", "type": "is-a"},      # Coral Reef is-a Ocean feature
    {"source": "c03", "target": "c01", "type": "is-a"},      # Fish is-a Ocean inhabitant
    {"source": "c04", "target": "c01", "type": "is-a"},      # Algae is-a Ocean inhabitant
    {"source": "c05", "target": "c01", "type": "is-a"},      # Water is-a Ocean component
    {"source": "c14", "target": "c02", "type": "is-a"},      # Healthy is-a state of reef
    
    # has-a (5)
    {"source": "c02", "target": "c04", "type": "has-a"},     # Coral Reef has-a Algae
    {"source": "c02", "target": "c03", "type": "has-a"},     # Coral Reef has-a Fish
    {"source": "c01", "target": "c05", "type": "has-a"},     # Ocean has-a Water
    {"source": "c01", "target": "c06", "type": "has-a"},     # Ocean has-a Salinity
    {"source": "c01", "target": "c07", "type": "has-a"},     # Ocean has-a Temperature
    
    # causes (5)
    {"source": "c10", "target": "c17", "type": "causes"},    # Photosynthesis causes Nutrient-rich
    {"source": "c11", "target": "c16", "type": "causes"},    # Predation causes Overfished
    {"source": "c07", "target": "c15", "type": "causes"},    # Temperature causes Bleached
    {"source": "c08", "target": "c09", "type": "causes"},    # Depth causes Clarity
    {"source": "c12", "target": "c14", "type": "causes"},    # Symbiosis causes Healthy
    
    # prevents (5)
    {"source": "c12", "target": "c15", "type": "prevents"},  # Symbiosis prevents Bleached
    {"source": "c14", "target": "c16", "type": "prevents"},  # Healthy prevents Overfished
    {"source": "c09", "target": "c15", "type": "prevents"},  # Clarity prevents Bleached
    {"source": "c17", "target": "c15", "type": "prevents"},  # Nutrient-rich prevents Bleached
    {"source": "c13", "target": "c16", "type": "prevents"},  # Migration prevents Overfished
    
    # precedes (5)
    {"source": "c10", "target": "c17", "type": "precedes"},  # Photosynthesis precedes Nutrient-rich
    {"source": "c11", "target": "c16", "type": "precedes"},  # Predation precedes Overfished
    {"source": "c07", "target": "c15", "type": "precedes"},  # Temperature precedes Bleached
    {"source": "c08", "target": "c09", "type": "precedes"},  # Depth precedes Clarity
    {"source": "c13", "target": "c12", "type": "precedes"},  # Migration precedes Symbiosis
    
    # follows (5)
    {"source": "c17", "target": "c10", "type": "follows"},   # Nutrient-rich follows Photosynthesis
    {"source": "c16", "target": "c11", "type": "follows"},   # Overfished follows Predation
    {"source": "c15", "target": "c07", "type": "follows"},   # Bleached follows Temperature
    {"source": "c09", "target": "c08", "type": "follows"},   # Clarity follows Depth
    {"source": "c12", "target": "c13", "type": "follows"},   # Symbiosis follows Migration
]


def validate_data() -> None:
    """Validate the sample data meets requirements."""
    assert len(CONCEPTS) == 20, f"Expected 20 concepts, got {len(CONCEPTS)}"
    assert len(RELATIONSHIPS) == 30, f"Expected 30 relationships, got {len(RELATIONSHIPS)}"
    
    # Validate categories
    categories_used = {c["category"] for c in CONCEPTS}
    assert categories_used.issubset(set(CATEGORIES)), f"Invalid categories: {categories_used - set(CATEGORIES)}"
    
    # Validate relationship types
    types_used = {r["type"] for r in RELATIONSHIPS}
    assert types_used.issubset(set(RELATIONSHIP_TYPES)), f"Invalid relationship types: {types_used - set(RELATIONSHIP_TYPES)}"
    
    # Validate all referenced cells exist
    cell_ids = {c["id"] for c in CONCEPTS}
    for rel in RELATIONSHIPS:
        assert rel["source"] in cell_ids, f"Unknown source cell: {rel['source']}"
        assert rel["target"] in cell_ids, f"Unknown target cell: {rel['target']}"
    
    # Validate each relationship type appears at least once
    for rtype in RELATIONSHIP_TYPES:
        count = sum(1 for r in RELATIONSHIPS if r["type"] == rtype)
        assert count > 0, f"Relationship type '{rtype}' has no instances"


def build_quilt_sheet() -> Dict[str, Any]:
    """
    Build the Quilt sheet data structure.
    
    Returns:
        Dict containing the complete Quilt sheet
    """
    # Validate input data first
    validate_data()
    
    # Build the sheet
    sheet = {
        "format": "quilt-sheet",
        "version": "1.0",
        "metadata": {
            "title": "Othismos-Reef Knowledge Graph",
            "description": "Knowledge graph of coral reef ecosystem concepts and relationships",
            "source": "othismos-reef",
            "created": datetime.now(timezone.utc).isoformat(),
            "concept_count": len(CONCEPTS),
            "relationship_count": len(RELATIONSHIPS),
            "categories": CATEGORIES,
            "relationship_types": RELATIONSHIP_TYPES,
        },
        "cells": CONCEPTS,
        "edges": RELATIONSHIPS,
    }
    
    return sheet


def save_quilt_sheet(sheet: Dict[str, Any], output_path: str) -> None:
    """
    Save the Quilt sheet to a .qzt file.
    
    Args:
        sheet: The Quilt sheet data structure
        output_path: Path to save the file
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write with pretty formatting for readability
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sheet, f, indent=2, ensure_ascii=False)
    
    print(f"Quilt sheet saved to: {output_path}")
    print(f"  - {len(sheet['cells'])} cells")
    print(f"  - {len(sheet['edges'])} edges")


def main() -> None:
    """Main entry point."""
    print("Building othismos-reef Quilt sheet...")
    
    # Build the sheet
    sheet = build_quilt_sheet()
    
    # Save to file
    save_quilt_sheet(sheet, OUTPUT_PATH)
    
    # Print summary
    print("\nSummary:")
    print(f"  Categories: {', '.join(CATEGORIES)}")
    print(f"  Relationship types: {', '.join(RELATIONSHIP_TYPES)}")
    
    # Count relationships by type
    type_counts = {}
    for rel in sheet["edges"]:
        rtype = rel["type"]
        type_counts[rtype] = type_counts.get(rtype, 0) + 1
    print("\nRelationship type distribution:")
    for rtype in RELATIONSHIP_TYPES:
        print(f"  {rtype}: {type_counts.get(rtype, 0)}")
    
    # Count concepts by category
    cat_counts = {}
    for cell in sheet["cells"]:
        cat = cell["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print("\nConcept category distribution:")
    for cat in CATEGORIES:
        print(f"  {cat}: {cat_counts.get(cat, 0)}")


if __name__ == "__main__":
    main()
