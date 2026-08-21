#!/usr/bin/env python3
"""
protocols_to_quilt.py — Bridge the protocols family to Quilt.

The protocols family IS the communication substrate:
- a2a: 6 repos for agent-to-agent protocol
- a2ui: 5 repos for agent-to-UI protocol
- baton: 5 repos for baton protocol (orchestration)
- api: 5 repos for API tools
"""
import json
from pathlib import Path

A2A = [
    ("a2a-adapter", "Adapter for A2A protocol. The cell speaks A2A.", "typescript", "adapter"),
    ("a2a-constraint-protocol", "Constraint-based A2A. Cells negotiate constraints.", "typescript", "constraint"),
    ("a2a-future", "Future A2A. The cell's communication evolution.", "typescript", "future"),
    ("a2a-protocol", "Core A2A protocol. The cell's standard speak.", "typescript", "protocol"),
    ("a2a-r-protocol", "R variant of A2A. Statistical A2A.", "r", "r-protocol"),
    ("a2a-signal-chain", "Signal chain A2A. Chain of signals between cells.", "typescript", "signal-chain"),
]

A2UI = [
    ("a2ui", "Agent-to-UI. The cell renders to humans.", "typescript", "core"),
    ("a2ui-cave-wall", "Cave-wall style A2UI. Prehistoric, raw.", "typescript", "cave-wall"),
    ("a2ui-components", "A2UI component library. The cell's UI primitives.", "typescript", "components"),
    ("a2ui-protocol", "A2UI protocol. The cell's standard render.", "typescript", "protocol"),
    ("a2ui-render", "A2UI renderer. The cell's render engine.", "typescript", "render"),
]

BATON = [
    ("baton-ai", "AI Baton. Pass the baton between cells.", "typescript", "ai"),
    ("baton-orchestrator", "Orchestrator baton. The cell's baton master.", "typescript", "orchestrator"),
    ("baton-protocol", "Baton protocol. The cell's standard handoff.", "typescript", "protocol"),
    ("baton-router", "Baton router. Where the baton goes next.", "typescript", "router"),
    ("baton-skill", "Baton skill. The cell's baton capabilities.", "typescript", "skill"),
]

API_TOOLS = [
    ("api-doc-generator", "Generate API docs from cell definitions.", "typescript", "doc-gen"),
    ("api-gateway", "API gateway. The cell's front door.", "typescript", "gateway"),
    ("api-playground", "API playground. Test the cell's APIs.", "typescript", "playground"),
    ("api-versioner", "Version the cell's APIs.", "typescript", "versioner"),
]


def make_cell(name, desc, lang, slug):
    if "a2a" in name:
        primitives = ["Spawn", "Send", "Receive", "Murmur"]
    elif "a2ui" in name:
        primitives = ["Spawn", "Send", "Mutate", "Observe"]
    elif "baton" in name:
        primitives = ["Spawn", "Send", "Receive", "Move"]
    elif "api" in name:
        primitives = ["Spawn", "Send", "Receive", "Observe"]
    else:
        primitives = ["Spawn", "Observe"]
    return {
        "id": f"proto_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "protocol message"},
        "z_out": {"output": "protocol response, UI render, baton handoff"},
        "jepa": {"predict": "next protocol step", "observe": "actual"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "speak", "args": ["Message"], "returns": "Response"},
        ],
        "substrate": {
            "address": f"/protocols/{name}",
            "scale": 0,
            "room": "ProtocolRoom",
            "protocol": name,
            "form": name,
            "state": "ready"
        },
        "tags": ["protocols", "a2a", "a2ui", "baton", "api", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "protocols_meta",
            "kind": "cell",
            "form": {"name": "ProtocolsMeta"},
            "description": "The protocols family IS the communication substrate. 21 repos: 6 A2A, 5 A2UI, 5 Baton, 5 API tools. The cell speaks, renders, hands off, and serves.",
            "primitives": ["Observe"] * 21,
            "z_in": {"family": "protocols", "size": 21},
            "z_out": {"proof": "cell has standard communication"},
            "tags": ["meta", "protocols", "communication"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in A2A + A2UI + BATON + API_TOOLS:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in A2A + A2UI + BATON + API_TOOLS:
        for n2, _, _, _ in A2A + A2UI + BATON + API_TOOLS:
            if n1 != n2:
                edges.append({"from": f"proto_{n1.replace('-', '_')}", "to": f"proto_{n2.replace('-', '_')}", "kind": "protocol-gossip", "weight": 0.3})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "protocols-to-quilt",
        "description": "Bridge mapping 21 protocol repos to Quilt. A2A + A2UI + Baton + API tools.",
        "cells": cells, "edges": edges,
        "external_refs": [
            {"kind": "github-org", "name": "SuperInstance", "filter": "a2a-*, a2ui-*, baton-*, api-*"}
        ],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(A2A) + len(A2UI) + len(BATON) + len(API_TOOLS)},
        "tags": ["protocols", "a2a", "a2ui", "baton", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/protocols_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote protocols: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
