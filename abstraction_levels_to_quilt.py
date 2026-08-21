#!/usr/bin/env python3
"""
abstraction_levels_to_quilt.py — Bridge the 8 levels of Quilt to cells.

Each level is a cell. The same 8 primitives, 7 substrates, 9 dials,
conservation law, and watch oscillation apply at every level. What
changes is the grain.
"""
import json
from pathlib import Path

LEVELS = [
    (0, "cell", "8 primitives, 7 substrates, 9 dials, conservation law, watch", 
     ["Spawn", "Observe", "Mutate", "Send", "Receive", "Move", "Resize", "Kill"]),
    (1, "sheet", "graph of cells, β₁ topology, edges (murmur, depends_on, cites)",
     ["Spawn", "Send", "Receive", "Observe"]),
    (2, "agent", "sheet that watches itself, persona ↔ context",
     ["Spawn", "Observe", "Mutate", "JEPA", "Send", "Receive", "Murmur", "GC"]),
    (3, "harness", "agent + custom runtime, tool-bound oscillation",
     ["Spawn", "Observe", "Mutate", "Send", "Receive", "Murmur", "GC", "Resize"]),
    (4, "fleet", "network of harnesses, charter ↔ each boat's log",
     ["Spawn", "Send", "Receive", "Murmur", "GC", "Observe"]),
    (5, "ecosystem", "fleet + trunk links, API surface ↔ each service",
     ["Spawn", "Send", "Receive", "Murmur", "Resize", "Move", "Observe"]),
    (6, "infrastructure", "substrate of ecosystem, topology ↔ each node",
     ["Observe", "Mutate", "Resize", "Move", "Send", "Receive"]),
    (7, "system", "the system as a cell, purpose ↔ each contributor",
     ["Spawn", "Observe", "Mutate", "Send", "Receive", "Murmur", "GC", "Resize", "Move", "Kill"]),
]

CONSERVATION = {
    0: ("cell's output", "cell's drift", "cell's allocation"),
    1: ("sheet's structure", "sheet's incoherence", "sheet's nodes"),
    2: ("agent's actions", "agent's forgetting", "agent's trace"),
    3: ("harness's tools", "harness's overhead", "harness's API quota"),
    4: ("fleet's coordination", "fleet's gossip", "fleet's bandwidth"),
    5: ("ecosystem's services", "ecosystem's idle", "ecosystem's bill"),
    6: ("infra's provisioning", "infra's waste", "infra's capacity"),
    7: ("system's creation", "system's entropy", "system's lifetime"),
}

WATCH = {
    0: "tick (one primitive fires)",
    1: "β₁ changes as cells connect",
    2: "persona ↔ context",
    3: "tool-bound oscillation",
    4: "charter ↔ each boat's log",
    5: "API surface ↔ each service",
    6: "topology ↔ each node",
    7: "purpose ↔ each contributor",
}

EXAMPLES = {
    0: "number, string, formula, primitive value",
    1: "formula sheet, state machine, knowledge graph, CRDT",
    2: "Quilt cell, AI agent, person, service, daemon",
    3: "cog, hermes, vessel, openai, claude, copaw",
    4: "fleet of fishing boats, swarm of drones, cluster of services",
    5: "multi-cloud agent network, enterprise microservices",
    6: "GPU clusters, KV stores, cloud accounts, on-prem servers",
    7: "Quilt itself, as a cell that watches the cells",
}


def make_level_cell(level, name, desc, primitives):
    gamma, eta, budget = CONSERVATION[level]
    return {
        "id": f"level_{level}",
        "kind": "cell",
        "form": {"name": f"L{level}_{name.title()}"},
        "description": desc,
        "level": level,
        "name": name,
        "primitives": primitives,
        "z_in": {"input": f"inputs at {name} level"},
        "z_out": {"output": f"outputs at {name} level"},
        "jepa": {"predict": f"{name} surprise", "observe": "actual"},
        "double_entry": {"gamma": 0.5, "eta": 0.5, "verified": True},
        "vibe": {"position": level, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {"gossip_to": [f"level_{i}" for i in range(8) if i != level], "gossip_from": []},
        "graph": {"children": [f"level_{i}" for i in range(level)], "parents": [f"level_{i}" for i in range(level+1, 8)]},
        "openers": [
            {"name": "zoom_in", "args": [], "returns": "Cell"},
            {"name": "zoom_out", "args": [], "returns": "Cell"},
            {"name": "list_children", "args": [], "returns": "List<Cell>"},
        ],
        "substrate": {
            "address": f"/levels/{level}",
            "scale": 0,
            "room": f"L{level}Room",
            "protocol": "Level",
            "form": name,
            "state": "active"
        },
        "conservation": {
            "gamma_meaning": gamma,
            "eta_meaning": eta,
            "budget_meaning": budget
        },
        "watch": WATCH[level],
        "example": EXAMPLES[level],
        "tags": ["level", f"L{level}", name, "quilt-fractal"]
    }


def make_meta_cells():
    return [
        {
            "id": "fractal_meta",
            "kind": "cell",
            "form": {"name": "FractalMeta"},
            "description": "The Quilt cell is universal across 8 abstraction levels. Same model, different grain. The system is fractal.",
            "primitives": ["Observe"] * 8,
            "z_in": {"levels": list(range(8))},
            "z_out": {"proof": "cell is universal"},
            "jepa": {"predict": "fractal", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
            "gc": {"phase": "fractal"},
            "murmur": {},
            "graph": {"children": [f"level_{i}" for i in range(8)]},
            "openers": [
                {"name": "zoom", "args": ["int"], "returns": "Cell"},
                {"name": "list_levels", "args": [], "returns": "List<Cell>"},
            ],
            "tags": ["meta", "fractal"]
        }
    ]


def build_qzt():
    cells = []
    for level, name, desc, prims in LEVELS:
        cells.append(make_level_cell(level, name, desc, prims))
    cells.extend(make_meta_cells())
    # Edges: each level gossips with all others
    edges = []
    for i in range(8):
        for j in range(8):
            if i != j:
                edges.append({
                    "from": f"level_{i}",
                    "to": f"level_{j}",
                    "kind": "gossip",
                    "weight": 1.0 / (abs(i - j) + 1),  # closer levels have stronger gossip
                    "tag": f"L{i}-L{j}"
                })
    return {
        "version": "1.0",
        "kind": "quilt-zip-target",
        "name": "abstraction-levels-to-quilt",
        "description": "Bridge mapping the 8 abstraction levels of Quilt to cells. The cell is universal at every scale. The system is fractal.",
        "cells": cells,
        "edges": edges,
        "external_refs": [
            {"kind": "paper", "name": "Emergent Abstractions in Quilt", "file": "paper_33_emergent_abstractions.md"}
        ],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "levels": 8
        },
        "tags": ["abstraction-levels", "fractal", "emergent", "quilt"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/abstraction_levels_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
