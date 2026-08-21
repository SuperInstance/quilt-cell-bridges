#!/usr/bin/env python3
"""
agent_cognition_family_to_quilt.py — Bridge the agent cognition family to Quilt.

The agent cognition family is the MIND of the cell: 8 repos that make
the cell think, remember, learn, and act with purpose.

- agent-dna: genetic code for vessel capabilities
- actualizer-ai: reverse-actualization, 7 time horizons
- home-ai: private home AI, accumulated context IS the product
- fishinglog-ai: edge AI fishing vessel, Jetson-powered
- trust-graph: trust relationships between vessels
- context-serializer: serialize context for transfer
- hybrid-memory: git + KV + causal memory
- oracle1-workspace: fleet coordination, agent identities
"""
import json
from pathlib import Path

AGENT_COGNITION = [
    ("agent-dna", "Genetic code for vessel capabilities. AgentGenome, traits, evolution.", "python"),
    ("actualizer-ai", "Reverse-actualization: work backward from 1, 5, 10, 25, 50, 100 year futures.", "python"),
    ("home-ai", "Private home AI. Accumulated context IS the product. Cloudflare Workers.", "typescript"),
    ("fishinglog-ai", "Edge AI fishing vessel. Jetson-powered species classification. NMEA + camera + sounder.", "typescript"),
    ("trust-graph", "Trust relationships between vessels. Composite trust scoring.", "typescript"),
    ("context-serializer", "Serialize/deserialize context for transfer between vessels.", "typescript"),
    ("hybrid-memory", "Git + KV + causal memory equipment for fleet vessels.", "typescript"),
    ("oracle1-workspace", "Fleet coordination. Agent identities. SOUL.md, IDENTITY.md, COMMS.md.", "python"),
]


def make_cell(name, desc, lang):
    primitives = []
    if "dna" in name:
        primitives = ["Spawn", "Observe", "Mutate", "JEPA", "GC"]  # genetic
    elif "actualizer" in name:
        primitives = ["Spawn", "Observe", "JEPA", "Mutate"]  # reverse
    elif "home" in name or "fishinglog" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive"]  # agent
    elif "trust" in name:
        primitives = ["Observe", "Murmur"]  # trust
    elif "context" in name or "memory" in name:
        primitives = ["Spawn", "Observe", "Mutate", "GC"]  # memory
    elif "oracle" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive", "Murmur", "GC"]  # full
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"cog_{name.replace('-', '_').lower()}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "primitives": primitives,
        "z_in": {"input": "thoughts, contexts, identities"},
        "z_out": {"output": "decisions, plans, memory updates"},
        "jepa": {"predict": "next thought", "observe": "actual thought"},
        "double_entry": {"gamma": 0.4, "eta": 0.6},  # Mind is η-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "thinking"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "think", "args": ["Context"], "returns": "Thought"},
            {"name": "remember", "args": ["Memory"], "returns": "Recall"},
        ],
        "substrate": {
            "address": f"/agent-cognition/{name}",
            "scale": 1,
            "room": "MindRoom",
            "protocol": "Cognition",
            "form": name,
            "state": "active"
        },
        "tags": ["agent-cognition", "mind", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "agent_cognition_meta",
            "kind": "cell",
            "form": {"name": "AgentCognitionMeta"},
            "description": "The agent cognition family IS the mind of the cell. 8 repos: DNA, actualizer, home-ai, fishinglog-ai, trust-graph, context-serializer, hybrid-memory, oracle1-workspace. The cell thinks, remembers, learns, and acts with purpose.",
            "primitives": ["Observe"] * 8,
            "z_in": {"family": "agent-cognition", "size": 8},
            "z_out": {"proof": "cell has a mind"},
            "jepa": {"predict": "agent = cell mind", "verified": True},
            "double_entry": {"gamma": 0.4, "eta": 0.6},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"cog_{n.replace('-', '_').lower()}" for n, _, _ in AGENT_COGNITION]},
            "openers": [
                {"name": "think", "args": ["Context"], "returns": "Thought"},
            ],
            "tags": ["meta", "agent-cognition", "mind"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in AGENT_COGNITION:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _ in AGENT_COGNITION:
        for n2, _, _ in AGENT_COGNITION:
            if n1 != n2:
                edges.append({"from": f"cog_{n1.replace('-', '_').lower()}", "to": f"cog_{n2.replace('-', '_').lower()}", "kind": "cog-gossip", "weight": 0.4})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "agent-cognition-family-to-quilt",
        "description": "Bridge mapping 8 agent cognition repos to Quilt. The mind of the cell: DNA, actualizer, home-ai, fishinglog, trust, context, memory, oracle.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "agent-*, oracle*, trust-*, home-ai, fishinglog-ai, context-serializer, hybrid-memory, actualizer-ai"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(AGENT_COGNITION)},
        "tags": ["agent-cognition", "mind", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/agent_cognition_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote agent_cognition_family: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
