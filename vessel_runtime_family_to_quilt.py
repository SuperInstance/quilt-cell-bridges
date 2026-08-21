#!/usr/bin/env python3
"""
vessel_runtime_family_to_quilt.py — Bridge the vessel runtime family to Quilt.

The vessel runtime family is the BODY of the cell: 7 repos that turn a
cell into something that can act in the physical world.

- vessel-constellation: N-body gravitational fleet sim
- vessel-bridge: hardware abstraction (ESP32, Jetson, Cloud)
- vessel-tuner: auto-kernel profiler
- deckboss-net: maritime reliable messaging
- nexus-edge-runtime: bytecode VM, trust engine, safety system
- hardware-adapter: pluggable JSON heartbeat schemas
- JetsonClaw1-vessel: vessel on Jetson
"""
import json
from pathlib import Path

VESSEL_RUNTIME = [
    ("vessel-constellation", "N-body gravitational fleet sim. 4 vessels as solar system with leapfrog integration.", "rust"),
    ("vessel-bridge", "Hardware abstraction: ESP32, Jetson, Cloud. Marine/Aerial/Industrial/Home/Medical domains.", "python"),
    ("vessel-tuner", "AutoKernel for the fleet: profile, benchmark, optimize.", "typescript"),
    ("deckboss-net", "Maritime reliable messaging. At-least-once with idempotency. Designed for VHF/satellite blackouts.", "rust"),
    ("nexus-edge-runtime", "Bytecode VM (32 ops, 64KB), INCREMENTS trust engine, 4-tier safety, intent compiler.", "python"),
    ("hardware-adapter", "Pluggable JSON heartbeat schemas for any board — auto-generates vessel interface.", "typescript"),
    ("JetsonClaw1-vessel", "Vessel on NVIDIA Jetson. Git-Agent Vessel — Lucineer realm specialist.", "cuda"),
]


def make_cell(name, desc, lang):
    primitives = []
    if "constellation" in name:
        primitives = ["Spawn", "Observe", "JEPA", "Mutate"]  # N-body
    elif "bridge" in name or "hardware" in name:
        primitives = ["Spawn", "Send", "Receive", "Observe"]  # I/O
    elif "tuner" in name:
        primitives = ["Spawn", "Observe", "Mutate", "JEPA"]  # profile
    elif "deckboss" in name or "net" in name:
        primitives = ["Spawn", "Send", "Receive", "GC"]  # messaging
    elif "runtime" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive", "JEPA", "GC"]  # full VM
    else:
        primitives = ["Spawn", "Observe", "Mutate", "Send"]
    return {
        "id": f"vessel_{name.replace('-', '_').lower()}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "primitives": primitives,
        "z_in": {"input": "physical sensors / hardware signals"},
        "z_out": {"output": "actuator commands / vessel actions"},
        "jepa": {"predict": "next sensor state", "observe": "actual"},
        "double_entry": {"gamma": 0.6, "eta": 0.4},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "act", "args": ["Action"], "returns": "Result"},
            {"name": "sense", "args": ["Sensor"], "returns": "Reading"},
        ],
        "substrate": {
            "address": f"/vessel-runtime/{name}",
            "scale": 0,
            "room": "VesselRoom",
            "protocol": "Hardware",
            "form": name,
            "state": "active"
        },
        "tags": ["vessel-runtime", "hardware", "body", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "vessel_runtime_meta",
            "kind": "cell",
            "form": {"name": "VesselRuntimeMeta"},
            "description": "The vessel runtime family IS the body of the cell. 7 repos that turn a cell into something that can act in the physical world. From bytecode VM to N-body fleet sim to maritime networking. The cell has a body.",
            "primitives": ["Observe"] * 7,
            "z_in": {"family": "vessel-runtime", "size": 7},
            "z_out": {"proof": "cell has a body"},
            "jepa": {"predict": "vessel = cell body", "verified": True},
            "double_entry": {"gamma": 0.6, "eta": 0.4},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"vessel_{n.replace('-', '_').lower()}" for n, _, _ in VESSEL_RUNTIME]},
            "openers": [
                {"name": "deploy", "args": ["Vessel"], "returns": "Unit"},
                {"name": "profile", "args": ["Vessel"], "returns": "Profile"},
            ],
            "tags": ["meta", "vessel-runtime", "body"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in VESSEL_RUNTIME:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _ in VESSEL_RUNTIME:
        for n2, _, _ in VESSEL_RUNTIME:
            if n1 != n2:
                edges.append({"from": f"vessel_{n1.replace('-', '_').lower()}", "to": f"vessel_{n2.replace('-', '_').lower()}", "kind": "vessel-gossip", "weight": 0.4})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "vessel-runtime-family-to-quilt",
        "description": "Bridge mapping the 7 vessel runtime repos to Quilt. The body of the cell: hardware abstraction, bytecode VM, N-body sim, maritime networking.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "vessel-*"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(VESSEL_RUNTIME)},
        "tags": ["vessel-runtime", "body", "hardware", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/vessel_runtime_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote vessel_runtime_family: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
