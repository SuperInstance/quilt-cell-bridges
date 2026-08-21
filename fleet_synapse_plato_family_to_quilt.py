#!/usr/bin/env python3
"""
fleet_synapse_plato_family_to_quilt.py — Bridge the synapse+PLATO+sandbox family to Quilt.

The synapse+PLATO+sandbox family is the SYNAPSE of the cell: 7 repos that
route messages, detect changes, and provide safe testing grounds.
"""
import json
from pathlib import Path

SYNAPSE_PLATO = [
    ("fleet-radar", "Fleet-wide change detection: monitor all vessels for mutations.", "typescript"),
    ("fleet-synapse", "High-speed inter-vessel message routing and signal amplification.", "typescript"),
    ("plato-vessel-technician", "Deckboss — marine/industrial technician agent. Voice-first, hands-busy.", "?"),
    ("plato-vessel-educational", "Student + instructor agent for PLATO-enabled IoT classrooms.", "?"),
    ("plato-vessel-rapid-prototype", "Product developer iteration loop: describe → get BOM, wiring, code.", "?"),
    ("purplepincher-shell-library", "Agent/vessel separation for context compaction. Agent = thinking, Vessel = acting, PLATO = memory.", "python"),
    ("branch-sandbox", "Isolated branch environments for testing vessel mutations safely.", "python"),
    ("api-gateway-1", "Unified API gateway: single entry point for all fleet vessel APIs.", "python"),
]


def make_cell(name, desc, lang):
    if "radar" in name or "synapse" in name:
        primitives = ["Spawn", "Observe", "Send", "Receive", "Murmur"]
    elif "plato" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive", "JEPA"]
    elif "purplepincher" in name or "shell" in name:
        primitives = ["Spawn", "Observe", "Mutate", "GC", "Move", "Resize"]
    elif "sandbox" in name or "branch" in name:
        primitives = ["Spawn", "Resize", "Move", "Kill", "Observe"]
    elif "gateway" in name or "api" in name:
        primitives = ["Spawn", "Send", "Receive", "Observe"]
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"syn_{name.replace('-', '_').lower()}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "primitives": primitives,
        "z_in": {"input": "routed messages, classroom inputs, sandbox queries"},
        "z_out": {"output": "delivered messages, learning, isolated tests"},
        "jepa": {"predict": "next fleet state", "observe": "actual"},
        "double_entry": {"gamma": 0.6, "eta": 0.4},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "route", "args": ["Message"], "returns": "Result"},
            {"name": "test", "args": ["Mutation"], "returns": "Verdict"},
        ],
        "substrate": {
            "address": f"/synapse/{name}",
            "scale": 1,
            "room": "SynapseRoom",
            "protocol": "Synapse",
            "form": name,
            "state": "active"
        },
        "tags": ["synapse", "plato", "sandbox", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "synapse_plato_meta",
            "kind": "cell",
            "form": {"name": "SynapsePLATOMeta"},
            "description": "The synapse+PLATO+sandbox family IS the synapse of the cell. 8 repos: fleet-radar (change detection), fleet-synapse (routing), PLATO vessels (technician/educational/rapid-prototype), purplepincher (agent/vessel separation), branch-sandbox (safe testing), api-gateway (unified entry).",
            "primitives": ["Observe"] * 8,
            "z_in": {"family": "synapse-plato", "size": 8},
            "z_out": {"proof": "cell has a synapse"},
            "jepa": {"predict": "synapse = routing + learning", "verified": True},
            "double_entry": {"gamma": 0.6, "eta": 0.4},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"syn_{n.replace('-', '_').lower()}" for n, _, _ in SYNAPSE_PLATO]},
            "tags": ["meta", "synapse", "plato"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in SYNAPSE_PLATO:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _ in SYNAPSE_PLATO:
        for n2, _, _ in SYNAPSE_PLATO:
            if n1 != n2:
                edges.append({"from": f"syn_{n1.replace('-', '_').lower()}", "to": f"syn_{n2.replace('-', '_').lower()}", "kind": "synapse-gossip", "weight": 0.4})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "synapse-plato-family-to-quilt",
        "description": "Bridge mapping 8 synapse+PLATO+sandbox repos to Quilt. The synapse: routing, change detection, classroom, safe testing.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "plato-*, fleet-radar, fleet-synapse, purplepincher-*, branch-sandbox, api-gateway-1"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(SYNAPSE_PLATO)},
        "tags": ["synapse", "plato", "sandbox", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/fleet_synapse_plato_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote synapse_plato_family: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
