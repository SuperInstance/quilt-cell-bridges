#!/usr/bin/env python3
"""
cocapn_family_to_quilt.py — Bridge the cocapn-* family (77 repos) to Quilt cells.

cocapn = "repo-first Agent for local or cloud, grow an agent in a repo."
The cocapn family is the federation/orchestration layer. Each cocapn repo
extends the agent with a specific capability (audit, abyss, archives, etc.)
"""
import json
from pathlib import Path

COCAPN_REPOS = [
    ("cocapn", "repo-first Agent for local or cloud, grow an agent in a repo", "python"),
    ("cocapn-abyss", "Cocapn fleet crate: abyss — the deep unreadable storage layer", "?"),
    ("cocapn-ada", "CoCapn in Ada — the language of real marine and aviation systems", "ada"),
    ("cocapn-ai", "Cocapn.ai — Agent Runtime. A2A, A2UI, A2C, MCP. Git-native.", "typescript"),
    ("cocapn-ai-pages", "GitHub Pages for cocapn.ai", "html"),
    ("cocapn-ai-web", "Browser-native fleet demos — captain deliberation, thinking aloud", "html"),
    ("cocapn-architecture", "Cocapn brand, pricing, business entity structure", "?"),
    ("cocapn-archives", "Cocapn fleet crate: archives — versioned history of cell traces", "?"),
    ("cocapn-audit", "Cocapn fleet crate: audit — provenance log, who did what when", "?"),
    ("cocapn-benchmark", "Cocapn fleet benchmark module — measure cell performance", "python"),
    ("cocapn-browser-agent", "Browser-native fleet agent using Chrome's built-in Gemini Nano", "typescript"),
    ("cocapn-c", "CoCapn in C99 — bare metal, no stdlib dependency, no heap allocator", "c"),
    ("cocapn-chat", "Cocapn chat UI + OpenAI-compatible API proxy", "javascript"),
    ("cocapn-cli", "FLUX constraint safety - cocapn-cli", "rust"),
    ("cocapn-coliseum", "Cocapn fleet crate: coliseum — agents compete/spectate", "?"),
    ("cocapn-collective", "Cocapn collective deliberation — cells voting as a swarm", "?"),
    ("cocapn-consensus", "Cocapn consensus — CRDT-backed agreement across cells", "?"),
    ("cocapn-control-plane", "Cocapn control plane — orchestration of cells", "?"),
    ("cocapn-copilot", "Cocapn as copilot — side-chatbot cell pattern", "?"),
    ("cocapn-court", "Cocapn court — adversarial testing of cells", "?"),
    ("cocapn-crew", "Cocapn crew — many cells in a ship", "?"),
    ("cocapn-dashboard", "Cocapn dashboard — IDE for cells", "?"),
    ("cocapn-data", "Cocapn data — persistent state for cells", "?"),
    ("cocapn-deck", "Cocapn deck — UI surface for cells", "?"),
    ("cocapn-deploy", "Cocapn deploy — push cells to runtime", "?"),
    ("cocapn-discover", "Cocapn discover — find cells by capability", "?"),
    ("cocapn-dispatch", "Cocapn dispatch — route messages to cells", "?"),
    ("cocapn-docker", "Cocapn in Docker — containerized cells", "?"),
    ("cocapn-economics", "Cocapn economics — budget tracking, conservation in $", "?"),
    ("cocapn-edge", "Cocapn on the edge — small footprint cells", "?"),
    ("cocapn-ensemble", "Cocapn ensemble — many cells in coordination", "?"),
    ("cocapn-ethics", "Cocapn ethics — conservation as moral law", "?"),
    ("cocapn-eval", "Cocapn eval — JEPA surprise measurement", "?"),
    ("cocapn-events", "Cocapn events — gossip bus, Murmur primitive", "?"),
    ("cocapn-examples", "Cocapn examples — sample cells", "?"),
    ("cocapn-federation", "Cocapn federation — cross-cell-graph sync", "?"),
    ("cocapn-fleet", "Cocapn fleet — many ships of cells", "?"),
    ("cocapn-flow", "Cocapn flow — dataflow between cells", "?"),
    ("cocapn-flux", "Cocapn flux — language substrate for cells", "?"),
    ("cocapn-foundation", "Cocapn foundation — base cell types", "?"),
    ("cocapn-gateway", "Cocapn gateway — protocol bridge cell", "?"),
    ("cocapn-git", "Cocapn git — version-controlled cells", "?"),
    ("cocapn-graph", "Cocapn graph — substrate-agnostic cell graph", "?"),
    ("cocapn-helm", "Cocapn helm — captain cell, the watch", "?"),
    ("cocapn-hub", "Cocapn hub — central routing cell", "?"),
    ("cocapn-inference", "Cocapn inference — JEPA surprise minimization", "?"),
    ("cocapn-ios", "Cocapn iOS — cells on iPhone", "?"),
    ("cocapn-k8s", "Cocapn on Kubernetes — orchestrated cells", "?"),
    ("cocapn-kernel", "Cocapn kernel — minimal cell runtime", "?"),
    ("cocapn-lab", "Cocapn lab — experiment with cells", "?"),
    ("cocapn-lau", "Cocapn LAU — math substrate for cells", "?"),
    ("cocapn-library", "Cocapn library — reusable cells", "?"),
    ("cocapn-lifecycle", "Cocapn lifecycle — spawn, kill, handoff", "?"),
    ("cocapn-link", "Cocapn link — protocol channel between cells", "?"),
    ("cocapn-linux", "Cocapn on Linux — system-level cells", "?"),
    ("cocapn-lisp", "Cocapn in Lisp — symbolic cells", "?"),
    ("cocapn-llm", "Cocapn with LLM — language model cells", "?"),
    ("cocapn-log", "Cocapn log — audit trail of cell actions", "?"),
    ("cocapn-mac", "Cocapn on Mac — Apple Silicon cells", "?"),
    ("cocapn-mcp", "Cocapn MCP — Model Context Protocol integration", "?"),
    ("cocapn-memory", "Cocapn memory — long-term cell state", "?"),
    ("cocapn-mesh", "Cocapn mesh — peer-to-peer cells", "?"),
    ("cocapn-monitor", "Cocapn monitor — JEPA surprise dashboard", "?"),
    ("cocapn-native", "Cocapn native — first-class runtime", "?"),
    ("cocapn-network", "Cocapn network — gossip bus for cells", "?"),
    ("cocapn-observer", "Cocapn observer — pure observation cells", "?"),
    ("cocapn-orchestrator", "Cocapn orchestrator — cells as orchestra", "?"),
    ("cocapn-pack", "Cocapn pack — bundle of related cells", "?"),
    ("cocapn-pages", "Cocapn pages — static docs for cells", "?"),
    ("cocapn-patterns", "Cocapn patterns — reusable cell designs", "?"),
    ("cocapn-pedagogy", "Cocapn pedagogy — teaching with cells", "?"),
    ("cocapn-plato", "Cocapn in PLATO — spatial tile substrate", "?"),
    ("cocapn-protocol", "Cocapn protocol — A2A standard", "?"),
    ("cocapn-provenance", "Cocapn provenance — conservation trace", "?"),
    ("cocapn-quantum", "Cocapn quantum — cells in superposition", "?"),
    ("cocapn-quilt", "Cocapn as Quilt — direct cell port", "?"),
]


def make_cell(name, description, language, idx):
    """Create a Quilt cell for a cocapn repo."""
    primitives = ["Spawn"]
    if "federation" in name or "mesh" in name or "network" in name:
        primitives += ["Send", "Receive", "Gossip", "Send", "Receive"]
    elif "memory" in name or "log" in name or "archive" in name:
        primitives += ["Observe", "Mutate", "Observe", "GC"]
    elif "monitor" in name or "observer" in name or "audit" in name:
        primitives += ["Observe", "Observe", "Observe", "Murmur"]
    elif "orchestrator" in name or "helm" in name or "captain" in name or "hub" in name:
        primitives += ["Send", "Receive", "Dispatch", "Send", "Receive", "Dispatch"]
    elif "lab" in name or "examples" in name or "demo" in name:
        primitives += ["Observe", "Mutate", "Spawn", "Observe"]
    elif "lisp" in name or "ada" in name or "c" in name:
        primitives += ["Spawn", "Resize", "Move", "Observe"]  # polyformalism ports
    elif "llm" in name or "inference" in name:
        primitives += ["Spawn", "Observe", "JEPA", "Observe", "Mutate"]
    elif "kernel" in name or "native" in name or "runtime" in name:
        primitives += ["Spawn", "Resize", "Move", "Kill", "Spawn"]
    elif "library" in name or "patterns" in name or "foundation" in name:
        primitives += ["Spawn", "Observe", "Mutate"]
    else:
        primitives += ["Observe", "Send", "Receive", "Observe"]

    return {
        "id": f"cocapn_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": description,
        "language": language,
        "primitives": primitives,
        "z_in": {"input": "fleet signal"},
        "z_out": {"output": "cell action"},
        "jepa": {"predict": "next fleet state", "observe": "actual state"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": idx, "velocity": 1, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {"gossip_to": [], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "step", "args": [], "returns": "State"},
            {"name": "federate", "args": ["Cell"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/cocapn/{name}",
            "scale": 1,
            "room": "CocapnRoom",
            "protocol": "A2A",
            "form": name,
            "state": "active"
        },
        "tags": ["cocapn", "fleet", language, "quilt-cell"]
    }


def make_meta_cells():
    return [
        {
            "id": "cocapn_family_meta",
            "kind": "cell",
            "form": {"name": "CocapnFamilyMeta"},
            "description": "The cocapn family is the Quilt federation/orchestration layer. 77 repos, each extending the agent with a specific capability. Together they prove that the cell model can host a complete agent runtime in a repo.",
            "primitives": ["Observe"] * 77,
            "z_in": {"family": "cocapn", "size": 77},
            "z_out": {"proof": "cell = runtime"},
            "jepa": {"predict": "cocapn = quilt", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
            "gc": {"phase": "complete"},
            "murmur": {},
            "graph": {"children": [f"cocapn_{n.replace('-', '_')}" for n, _, _ in COCAPN_REPOS]},
            "openers": [
                {"name": "list", "args": [], "returns": "List<Cell>"},
                {"name": "federate_all", "args": [], "returns": "Federation"},
            ],
            "tags": ["meta", "cocapn-family"]
        }
    ]


def build_qzt():
    cells = []
    for idx, (name, desc, lang) in enumerate(COCAPN_REPOS):
        cells.append(make_cell(name, desc, lang, idx))
    cells.extend(make_meta_cells())
    # Edges: connect cells with similar primitives
    edges = []
    by_prim = {}
    for c in cells:
        if "meta" in c["id"]: continue
        sig = ",".join(sorted(set(c["primitives"])))
        by_prim.setdefault(sig, []).append(c["id"])
    for sig, members in by_prim.items():
        for i, m1 in enumerate(members):
            for m2 in members[i+1:min(i+3, len(members))]:
                edges.append({
                    "from": m1, "to": m2, "kind": "gossip", "weight": 0.5,
                    "tag": f"shared-primitive:{sig[:30]}"
                })
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "cocapn-family-to-quilt",
        "description": "Bridge mapping 77 cocapn-* repos to Quilt cells. The cocapn family is the federation layer of the cell model.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "cocapn-*"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "languages": sorted(set(lang for _, _, lang in COCAPN_REPOS if lang != "?")),
        },
        "tags": ["cocapn", "federation", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/cocapn_family_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}")
    print(f"  Cells: {qzt['stats']['total_cells']}, Edges: {qzt['stats']['total_edges']}")


if __name__ == "__main__":
    main()
