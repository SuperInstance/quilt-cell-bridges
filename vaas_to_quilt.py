#!/usr/bin/env python3
"""
vaas_to_quilt.py — Bridge the VaaS to Quilt.

VaaS IS the cognitive architecture of Quilt. A cell at level 2 (agent)
or level 4 (fleet) needs a cognitive architecture. VaaS provides:
- 7 pillars: thermodynamics, communication, memory, timing, bridges, constitution, grafting
- Operator Field Ψ(t) — the system's collective state
- The hermit crab: mind (crab) migrates between hardware (shells)
- 4 shells: Periwinkle (phone), Turbo (PC), Conch (cluster), Custom
"""
import json
from pathlib import Path

VAAS_PILLARS = [
    # The 7 pillars
    (1, "thermodynamics", "Cognitive Thermodynamics: entropy budget, dream cycles. The engine's temperature gauge. When confusion gets too high, the agent dreams.", "entropy.py", "cognitive_thermodynamics"),
    (2, "communication", "Dual-Layer Communication: pheromones (fast, loose, environmental) + bridges (guaranteed, confirmed).", "communication.py", "dual_layer_communication"),
    (3, "memory", "Distributed Memory: active garden (on desk) + cryogenic archive (in basement) + holographic fragments (across all agents).", "memory.py", "distributed_memory"),
    (4, "polyrhythmic_timing", "Polyrhythmic Timing: multiple rhythms in coordination. Each agent's clock, the fleet's clock, the world's clock.", "timing.py", "polyrhythmic_timing"),
    (5, "holographic_bridges", "Holographic Bridges: every part contains the whole. A fragment can reconstruct the system.", "bridges.py", "holographic_bridges"),
    (6, "resonance_constitution", "Resonance Constitution: the laws that keep the system coherent. The constitution that defines what is allowed.", "constitution.py", "resonance_constitution"),
    (7, "grafting_protocol", "Grafting Protocol: how parts join. Migration of crab between shells. Memory transfer without loss.", "grafting.py", "grafting_protocol"),
]

VAAS_SHELLS = [
    ("periwinkle", "Phone/tablet. Minimal, portable. The crab's pocket shell."),
    ("turbo", "Wheelhouse PC. Full GPU, NMEA, serial. The crab's work shell."),
    ("conch", "Fleet cluster. Distributed, holographic. The crab's cloud shell."),
    ("custom", "Your hardware. See Harness Guide."),
]

VAAS_FIELDS = [
    ("operator_field", "Ψ(t) — the system's collective state. Computed, monitored, protected.", "the emergent property of all agents interacting through the 7 pillars"),
    ("entropy_budget", "How much confusion an agent can handle before it needs to dream.", "the engine's temperature gauge"),
    ("cognitive_garden", "The crab: memory, shorthand, instincts, referents.", "the part that matters, the part that survives the move"),
    ("resonance_field", "The constitution's reach: which patterns are allowed.", "the laws that keep the system coherent"),
]


def make_pillar_cell(num, name, desc, impl, slug):
    return {
        "id": f"vaas_pillar_{num}",
        "kind": "cell",
        "form": {"name": f"Pillar{num}_{name.title().replace('_', '')}"},
        "description": desc,
        "pillar_num": num,
        "pillar_name": name,
        "pillar_slug": slug,
        "implementation": impl,
        "primitives": ["Spawn", "Observe", "Mutate", "GC"] if "thermo" in name or "memory" in name else ["Spawn", "Observe", "Send", "Receive"],
        "z_in": {"input": f"inputs to {name}"},
        "z_out": {"output": f"outputs from {name}"},
        "jepa": {"predict": f"{name} surprise", "observe": "actual"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": num, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {"gossip_to": [f"vaas_pillar_{i}" for i in range(1, 8) if i != num], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "apply", "args": ["State"], "returns": "State"},
        ],
        "substrate": {
            "address": f"/vaas/pillars/{name}",
            "scale": 0,
            "room": f"Pillar{num}Room",
            "protocol": "VaaS",
            "form": name,
            "state": "active"
        },
        "tags": ["vaas", "pillar", f"pillar-{num}", slug]
    }


def make_shell_cell(name, desc):
    return {
        "id": f"vaas_shell_{name}",
        "kind": "cell",
        "form": {"name": f"Shell{name.title()}"},
        "description": desc,
        "shell_name": name,
        "primitives": ["Spawn", "Observe", "Resize", "Move"],
        "z_in": {"input": "crab (cognitive garden)"},
        "z_out": {"output": "shell-specific capabilities"},
        "jepa": {"predict": "shell can host", "observe": "shell hosts"},
        "double_entry": {"gamma": 0.7, "eta": 0.3},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "hosting"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "host", "args": ["Crab"], "returns": "Unit"},
            {"name": "migrate", "args": ["NewShell"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/vaas/shells/{name}",
            "scale": 0,
            "room": f"Shell{name.title()}Room",
            "protocol": "VaaS",
            "form": name,
            "state": "ready"
        },
        "tags": ["vaas", "shell", name]
    }


def make_field_cell(name, desc, meaning):
    return {
        "id": f"vaas_field_{name}",
        "kind": "cell",
        "form": {"name": name.replace("_", " ").title().replace(" ", "")},
        "description": f"{desc} — {meaning}",
        "field_name": name,
        "primitives": ["Observe"],
        "z_in": {"input": "system state"},
        "z_out": {"output": "field reading"},
        "jepa": {"predict": "field evolution", "observe": "actual evolution"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "monitoring"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "read", "args": [], "returns": "float"},
        ],
        "substrate": {
            "address": f"/vaas/fields/{name}",
            "scale": 0,
            "room": f"Field{name.title()}Room",
            "protocol": "VaaS",
            "form": name,
            "state": "active"
        },
        "tags": ["vaas", "field", name]
    }


def make_meta_cells():
    return [
        {
            "id": "vaas_meta",
            "kind": "cell",
            "form": {"name": "VaaSMeta"},
            "description": "VaaS IS the cognitive architecture of Quilt. 7 pillars + 4 shells + Operator Field Ψ(t). The hermit crab metaphor: the mind (crab) migrates between hardware (shells). The crab stays the same; the shell changes. Memory transfers without loss. This is cognitive portability.",
            "primitives": ["Observe"] * 15,
            "z_in": {"pillars": 7, "shells": 4, "fields": 4},
            "z_out": {"proof": "cognitive architecture = cell substrate"},
            "jepa": {"predict": "VaaS = Quilt cognitive layer", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"vaas_pillar_{n}" for n, _, _, _, _ in VAAS_PILLARS] + [f"vaas_shell_{n}" for n, _ in VAAS_SHELLS] + [f"vaas_field_{n}" for n, _, _ in VAAS_FIELDS]},
            "openers": [
                {"name": "migrate", "args": ["Crab", "NewShell"], "returns": "Unit"},
                {"name": "read_field", "args": ["str"], "returns": "float"},
            ],
            "tags": ["meta", "vaas", "cognitive-architecture"]
        }
    ]


def build_qzt():
    cells = []
    for num, name, desc, impl, slug in VAAS_PILLARS:
        cells.append(make_pillar_cell(num, name, desc, impl, slug))
    for name, desc in VAAS_SHELLS:
        cells.append(make_shell_cell(name, desc))
    for name, desc, meaning in VAAS_FIELDS:
        cells.append(make_field_cell(name, desc, meaning))
    cells.extend(make_meta_cells())
    edges = []
    # All pillars gossip with all
    for n, _, _, _, _ in VAAS_PILLARS:
        for m, _, _, _, _ in VAAS_PILLARS:
            if n != m:
                edges.append({"from": f"vaas_pillar_{n}", "to": f"vaas_pillar_{m}", "kind": "pillar-gossip", "weight": 0.5})
    # All shells talk to all
    for n, _ in VAAS_SHELLS:
        for m, _ in VAAS_SHELLS:
            if n != m:
                edges.append({"from": f"vaas_shell_{n}", "to": f"vaas_shell_{m}", "kind": "shell-migration", "weight": 0.7})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "vaas-to-quilt",
        "description": "Bridge mapping VaaS to Quilt. VaaS is the cognitive architecture: 7 pillars, 4 shells, Operator Field Ψ(t). The hermit crab metaphor made concrete.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-repo", "name": "VaaS", "org": "SuperInstance"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "pillars": len(VAAS_PILLARS),
            "shells": len(VAAS_SHELLS),
            "fields": len(VAAS_FIELDS),
            "size_kb": 410
        },
        "tags": ["vaas", "cognitive-architecture", "seven-pillars", "hermit-crab", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/vaas_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
