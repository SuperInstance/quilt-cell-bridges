#!/usr/bin/env python3
"""
llm_runtime_family_to_quilt.py — Bridge the LLM runtime family to Quilt.

The LLM runtime family is the LANGUAGE MODEL substrate of Quilt:
- claude: 6 repos for Claude/Anthropic integration
- claw: 3 repos for claw (orchestration engine)
- businesslog: 5 repos for business logic
"""
import json
from pathlib import Path

CLAUDE = [
    ("claude", "Core Claude integration. The cell talks to Claude.", "python", "claude"),
    ("claude-code-vessel", "Claude code as a vessel. The cell is a Claude instance.", "python", "code-vessel"),
    ("claude-context", "Claude context management. The cell's Claude context.", "python", "context"),
    ("Claude-Abstraction", "Claude abstraction layer. The cell abstracts Claude.", "python", "abstraction"),
    ("Claude-PRISM-CF", "Claude PRISM on Cloudflare Workers.", "python", "prism-cf"),
    ("Claude-prism-local-json", "Claude PRISM local JSON. The cell's offline Claude.", "python", "prism-local"),
]

CLAW = [
    ("claw", "Claw engine. The cell's orchestration engine.", "python", "claw"),
    ("claw-extensions", "Claw extensions. The cell's extra capabilities.", "python", "extensions"),
    ("claw-in-plato", "Claw in PLATO. The cell runs in PLATO.", "python", "in-plato"),
]

BUSINESSLOG = [
    ("businesslog-1", "Business log 1. The cell's first business log.", "python", "log-1"),
    ("businesslog-agent", "Business log agent. The cell's log keeper.", "python", "agent"),
    ("businesslog-ai", "Business log AI. The cell's intelligent logging.", "python", "ai"),
    ("businesslog-ai-pages", "Business log pages. The cell's log UI.", "html", "ai-pages"),
    ("businesslog-app", "Business log app. The cell's log app.", "python", "app"),
]


def make_cell(name, desc, lang, slug):
    if "claude" in name.lower():
        primitives = ["Spawn", "Send", "Receive", "JEPA"]
    elif "claw" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive"]
    elif "businesslog" in name:
        primitives = ["Spawn", "Observe", "Mutate", "GC"]
    else:
        primitives = ["Spawn", "Observe"]
    return {
        "id": f"llm_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "LLM prompt, business event"},
        "z_out": {"output": "LLM response, log entry"},
        "jepa": {"predict": "next LLM token", "observe": "actual"},
        "double_entry": {"gamma": 0.3, "eta": 0.7},  # LLMs are η-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "ask", "args": ["Prompt"], "returns": "Response"},
            {"name": "log", "args": ["Event"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/llm-runtime/{name}",
            "scale": 0,
            "room": "LLMRoom",
            "protocol": "LLM",
            "form": name,
            "state": "ready"
        },
        "tags": ["llm-runtime", "claude", "claw", "businesslog", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "llm_runtime_meta",
            "kind": "cell",
            "form": {"name": "LLMRuntimeMeta"},
            "description": "The LLM runtime family IS the language model substrate of Quilt. 14 repos: 6 Claude, 3 Claw, 5 Businesslog. The cell talks to Claude, orchestrates with Claw, logs with Businesslog.",
            "primitives": ["Observe"] * 14,
            "z_in": {"family": "llm-runtime", "size": 14},
            "z_out": {"proof": "cell has LLM substrate"},
            "tags": ["meta", "llm-runtime", "claude", "claw"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in CLAUDE + CLAW + BUSINESSLOG:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in CLAUDE + CLAW + BUSINESSLOG:
        for n2, _, _, _ in CLAUDE + CLAW + BUSINESSLOG:
            if n1 != n2:
                edges.append({"from": f"llm_{n1.replace('-', '_')}", "to": f"llm_{n2.replace('-', '_')}", "kind": "llm-gossip", "weight": 0.3})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "llm-runtime-family-to-quilt",
        "description": "Bridge mapping 14 LLM runtime repos to Quilt. The language model substrate: Claude, Claw, Businesslog.",
        "cells": cells, "edges": edges,
        "external_refs": [
            {"kind": "github-org", "name": "SuperInstance", "filter": "claude*, Claude*, claw-*, businesslog-*"}
        ],
        "stats": {"total_cells": len(cells), "total_edges": len(edges), "repos": len(CLAUDE) + len(CLAW) + len(BUSINESSLOG)},
        "tags": ["llm-runtime", "claude", "claw", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/llm_runtime_family_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote llm_runtime: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
