#!/usr/bin/env python3
"""
collective_context_to_quilt.py — Bridge the collective+context family to Quilt.

The collective+context family is the SWARM + MEMORY-MANAGEMENT substrate.
- collective: 7 repos for swarm intelligence, distributed reasoning
- context: 7 repos for context management, transfer, compaction
"""
import json
from pathlib import Path

COLLECTIVE = [
    ("collective-ai", "Swarm AI. Many minds, one answer.", "python", "swarm-ai"),
    ("collective-inference", "Distributed inference. Inference across many cells.", "python", "inference"),
    ("collective-mind", "Swarm mind. The cell's collective cognition.", "python", "mind"),
    ("collective-mind-v2", "v2: better algorithms.", "python", "mind-v2"),
    ("collective-reasoning", "Distributed reasoning. Reasoning across cells.", "python", "reasoning"),
    ("collective-recall-demo", "Demo of collective recall.", "python", "recall-demo"),
    ("collective-unconscious", "Jungian collective unconscious. The deep shared memory.", "python", "unconscious"),
]

CONTEXT = [
    ("context-broker", "Broker context between cells. The cell's memory router.", "typescript", "broker"),
    ("context-compactor", "Compact context for transfer. Reduce without losing meaning.", "typescript", "compactor"),
    ("context-compactor-v2", "v2: better algorithms.", "typescript", "compactor-v2"),
    ("context-lattice", "Context as a lattice. The cell's memory topology.", "typescript", "lattice"),
    ("context-limits", "Manage context limits. The cell's memory boundaries.", "typescript", "limits"),
    ("context-recycler", "Recycle context. The cell's memory GC.", "typescript", "recycler"),
    ("context-serializer", "Serialize context for transfer between cells.", "typescript", "serializer"),
]


def make_cell(name, desc, lang, slug):
    if "unconscious" in name or "mind" in name or "reasoning" in name or "inference" in name:
        primitives = ["Observe", "JEPA", "Murmur"]
    elif "lattice" in name or "broker" in name:
        primitives = ["Spawn", "Observe", "Send", "Receive"]
    elif "compactor" in name or "recycler" in name or "limits" in name:
        primitives = ["Spawn", "Observe", "GC"]
    elif "serializer" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send"]
    else:
        primitives = ["Spawn", "Observe", "Murmur"]
    return {
        "id": f"colctx_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "context, swarm signal"},
        "z_out": {"output": "compacted context, swarm answer"},
        "jepa": {"predict": "next context state", "observe": "actual"},
        "double_entry": {"gamma": 0.4, "eta": 0.6},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {"gossip_to": [], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "process", "args": ["Context"], "returns": "Result"},
        ],
        "substrate": {
            "address": f"/collective-context/{name}",
            "scale": 1,
            "room": "CollectiveContextRoom",
            "protocol": "Swarm",
            "form": name,
            "state": "ready"
        },
        "tags": ["collective", "context", "swarm", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "collective_context_meta",
            "kind": "cell",
            "form": {"name": "CollectiveContextMeta"},
            "description": "The collective+context family IS the swarm + memory-management substrate of Quilt. 14 repos: 7 for collective intelligence, 7 for context lifecycle. The cell thinks with the swarm and remembers with the lattice.",
            "primitives": ["Observe"] * 14,
            "z_in": {"family": "collective-context", "size": 14},
            "z_out": {"proof": "cell thinks with swarm, remembers with lattice"},
            "tags": ["meta", "collective", "context"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in COLLECTIVE + CONTEXT:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in COLLECTIVE + CONTEXT:
        for n2, _, _, _ in COLLECTIVE + CONTEXT:
            if n1 != n2:
                edges.append({"from": f"colctx_{n1.replace('-', '_')}", "to": f"colctx_{n2.replace('-', '_')}", "kind": "swarm-gossip", "weight": 0.3})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "collective-context-to-quilt",
        "description": "Bridge mapping 14 collective+context repos to Quilt. The swarm intelligence + memory management substrate.",
        "cells": cells, "edges": edges,
        "external_refs": [
            {"kind": "github-org", "name": "SuperInstance", "filter": "collective-*"},
            {"kind": "github-org", "name": "SuperInstance", "filter": "context-*"}
        ],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(COLLECTIVE) + len(CONTEXT)},
        "tags": ["collective", "context", "swarm", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/collective_context_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote collective_context: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
