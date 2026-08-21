#!/usr/bin/env python3
"""
nexus_fleet_family_to_quilt.py — Bridge the nexus fleet family to Quilt.

The nexus fleet family is the NERVOUS SYSTEM of the cell: 5 repos that
connect cells to each other, manage discovery, simulate, and learn.
"""
import json
from pathlib import Path

NEXUS = [
    ("nexus-edge-runtime", "Edge runtime: bytecode VM, INCREMENTS trust, 4-tier safety, intent compiler.", "python"),
    ("nexus-node-registry", "Node registry: discovery, config, lifecycle management for Cocapn fleet.", "python"),
    ("nexus-simulation", "Physics simulation: Monte Carlo scenarios, environment models, sensor noise.", "python"),
    ("nexus-swarm", "Swarm behaviors: emergence detection, consensus protocols, pheromone trails.", "python"),
    ("nexus-learning", "Reinforcement learning: skill acquisition, experience replay, reward shaping.", "python"),
]


def make_cell(name, desc, lang):
    primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive", "Murmur", "JEPA", "GC"]
    return {
        "id": f"nx_{name.replace('-', '_').lower()}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "primitives": primitives,
        "z_in": {"input": "fleet signals, network events"},
        "z_out": {"output": "discovery, simulation, learning, routing"},
        "jepa": {"predict": "next fleet state", "observe": "actual"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "discover", "args": [], "returns": "List<Node>"},
            {"name": "simulate", "args": ["Scenario"], "returns": "Result"},
            {"name": "learn", "args": ["Experience"], "returns": "Policy"},
        ],
        "substrate": {
            "address": f"/nexus/{name}",
            "scale": 1,
            "room": "NexusRoom",
            "protocol": "Nexus",
            "form": name,
            "state": "active"
        },
        "tags": ["nexus", "network", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "nexus_meta",
            "kind": "cell",
            "form": {"name": "NexusMeta"},
            "description": "The nexus fleet family IS the nervous system of the cell. 5 repos: edge runtime, node registry, simulation, swarm, learning. The cell discovers, simulates, learns, and routes.",
            "primitives": ["Observe"] * 5,
            "z_in": {"family": "nexus", "size": 5},
            "z_out": {"proof": "cell has a nervous system"},
            "jepa": {"predict": "nexus = cell network", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"nx_{n.replace('-', '_').lower()}" for n, _, _ in NEXUS]},
            "tags": ["meta", "nexus", "nervous-system"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in NEXUS:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _ in NEXUS:
        for n2, _, _ in NEXUS:
            if n1 != n2:
                edges.append({"from": f"nx_{n1.replace('-', '_').lower()}", "to": f"nx_{n2.replace('-', '_').lower()}", "kind": "nexus-gossip", "weight": 0.6})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "nexus-fleet-family-to-quilt",
        "description": "Bridge mapping 5 nexus fleet repos to Quilt. The nervous system: edge runtime, registry, simulation, swarm, learning.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "nexus-*"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(NEXUS)},
        "tags": ["nexus", "network", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/nexus_fleet_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote nexus_fleet_family: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
