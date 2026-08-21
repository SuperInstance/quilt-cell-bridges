#!/usr/bin/env python3
"""
character_family_to_quilt.py — Bridge the character family to Quilt.

The character family IS the persona substrate of Quilt. A cell at level
2 (agent) needs a persona. The character family provides:
- character: persona, traits, attributes
- character-arc: narrative progression
- character-class: archetype, class system
- character-build: construction system
- character-encounter: combat/social mechanics
- character-library: reusable characters
- character-sheet: stats, equipment
- character-skill-trees: progression trees
"""
import json
from pathlib import Path

CHARACTER_REPOS = [
    ("character", "Core character type. Persona, traits, attributes. The 'who' of a cell.", "typescript", "persona"),
    ("character-arc", "Narrative progression. How a character changes over time.", "typescript", "arc"),
    ("character-build", "Construction system. How to build a character from parts.", "typescript", "build"),
    ("character-class", "Archetype, class system. Wizard, warrior, rogue as cell kinds.", "typescript", "class"),
    ("character-encounter", "Combat/social mechanics. Encounters between cells.", "typescript", "encounter"),
    ("character-library", "Reusable characters. The cell's character database.", "typescript", "library"),
    ("character-sheet", "Stats, equipment, attributes. The cell's state.", "typescript", "sheet"),
    ("character-skill-trees", "Progression trees. How cells grow.", "typescript", "skill-trees"),
]


def make_cell(name, desc, lang, slug):
    if "arc" in name or "build" in name:
        primitives = ["Spawn", "Observe", "Mutate", "GC"]
    elif "class" in name or "library" in name:
        primitives = ["Spawn", "Observe"]
    elif "encounter" in name:
        primitives = ["Spawn", "Observe", "Send", "Receive", "Mutate"]
    elif "sheet" in name or "skill-trees" in name:
        primitives = ["Observe", "Mutate"]
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"char_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "persona, traits, stats"},
        "z_out": {"output": "character state, progression, encounter result"},
        "jepa": {"predict": "character evolution", "observe": "actual"},
        "double_entry": {"gamma": 0.4, "eta": 0.6},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "developing"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "play", "args": ["Character"], "returns": "Role"},
        ],
        "substrate": {
            "address": f"/character/{name}",
            "scale": 1,
            "room": "CharacterRoom",
            "protocol": "Persona",
            "form": name,
            "state": "ready"
        },
        "tags": ["character", "persona", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "character_family_meta",
            "kind": "cell",
            "form": {"name": "CharacterFamilyMeta"},
            "description": "The character family IS the persona substrate of Quilt. 8 repos for the cell's 'who' — persona, arc, build, class, encounter, library, sheet, skill-trees.",
            "primitives": ["Observe"] * 8,
            "z_in": {"family": "character", "size": 8},
            "z_out": {"proof": "cell has a persona"},
            "tags": ["meta", "character", "persona"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in CHARACTER_REPOS:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in CHARACTER_REPOS:
        for n2, _, _, _ in CHARACTER_REPOS:
            if n1 != n2:
                edges.append({"from": f"char_{n1.replace('-', '_')}", "to": f"char_{n2.replace('-', '_')}", "kind": "char-gossip", "weight": 0.5})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "character-family-to-quilt",
        "description": "Bridge mapping 8 character repos to Quilt. The persona substrate: who the cell is.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "character-*"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(CHARACTER_REPOS)},
        "tags": ["character", "persona", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/character_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote character: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
