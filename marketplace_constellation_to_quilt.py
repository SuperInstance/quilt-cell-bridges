#!/usr/bin/env python3
"""
marketplace_constellation_to_quilt.py — Bridge marketplace/constellation repos to Quilt.

The marketplace/constellation group is the COMMERCE and CONSTELLATION
substrate of the cell:
- fleet-marketplace: adaptive autonomy marketplace, vessels bid on tasks
- fleet-constellation: map vessel relationships as a star constellation
- equipment-catalog: browse and install equipment
- deckboss-ai: AI-powered system design for edge robotics and IoT
- cuda-swarm-agent: autonomous swarm vessel with fleet coordination
- boot-camp: from empty repo to working agent in one session
"""
import json
from pathlib import Path

MARKETPLACE = [
    ("fleet-marketplace", "Adaptive autonomy marketplace. Vessels bid on tasks. Part of the Cocapn fleet.", "typescript", "marketplace"),
    ("fleet-constellation", "Map vessel relationships as a star constellation. Spatial view of fleet.", "typescript", "constellation"),
    ("equipment-catalog", "Browse and install equipment for vessels. The vessel's library.", "typescript", "catalog"),
    ("deckboss-ai", "AI-powered system design for edge robotics and IoT. Layer 3 of the ecosystem.", "typescript", "design"),
    ("cuda-swarm-agent", "Autonomous swarm vessel — self-contained agent with fleet coordination, deliberation, health.", "rust", "swarm"),
    ("boot-camp", "From empty repo to working agent in one session. <500 lines JS, zero deps, Cloudflare Workers.", "javascript", "boot"),
]


def make_cell(name, desc, lang, slug):
    primitives = []
    if "marketplace" in slug:
        primitives = ["Spawn", "Send", "Receive", "Murmur"]  # bidding
    elif "constellation" in slug:
        primitives = ["Spawn", "Observe", "Mutate"]  # map
    elif "catalog" in slug:
        primitives = ["Spawn", "Observe", "Resize"]  # install
    elif "design" in slug:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive"]  # design
    elif "swarm" in slug:
        primitives = ["Spawn", "Send", "Receive", "Murmur", "JEPA"]  # swarm
    elif "boot" in slug:
        primitives = ["Spawn", "Observe", "GC", "Mutate"]  # learn
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"mkt_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "task bid, vessel map, equipment spec, design request, swarm signal, repo"},
        "z_out": {"output": "market outcome, constellation, equipment install, design, swarm coord, agent"},
        "jepa": {"predict": "system state", "observe": "actual"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "use", "args": ["Request"], "returns": "Result"},
        ],
        "substrate": {
            "address": f"/marketplace/{name}",
            "scale": 0,
            "room": "MarketRoom",
            "protocol": "Market",
            "form": name,
            "state": "active"
        },
        "tags": ["marketplace", "constellation", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "marketplace_meta",
            "kind": "cell",
            "form": {"name": "MarketplaceMeta"},
            "description": "The marketplace/constellation family is the COMMERCE and CONSTELLATION substrate of Quilt. 6 repos for the cell's economic and spatial visibility.",
            "primitives": ["Observe"] * 6,
            "z_in": {"family": "marketplace", "size": 6},
            "z_out": {"proof": "cell has commerce + constellation"},
            "jepa": {"predict": "market dynamics", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"mkt_{n.replace('-', '_')}" for n, _, _, _ in MARKETPLACE]},
            "tags": ["meta", "marketplace", "constellation"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in MARKETPLACE:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in MARKETPLACE:
        for n2, _, _, _ in MARKETPLACE:
            if n1 != n2:
                edges.append({"from": f"mkt_{n1.replace('-', '_')}", "to": f"mkt_{n2.replace('-', '_')}", "kind": "market-gossip", "weight": 0.3})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "marketplace-constellation-to-quilt",
        "description": "Bridge mapping 6 marketplace/constellation repos to Quilt. The commerce and spatial-visibility substrate.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "fleet-marketplace, fleet-constellation, equipment-catalog, deckboss-ai, cuda-swarm-agent, boot-camp"}],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(MARKETPLACE)},
        "tags": ["marketplace", "constellation", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/marketplace_constellation_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote marketplace: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
