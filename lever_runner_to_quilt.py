#!/usr/bin/env python3
"""
lever_runner_to_quilt.py — Bridge the lever-runner to Quilt.

lever-runner IS the executor substrate of Quilt. A cell at level 3
(harness) needs an executor. lever-runner is the trust compiler:
- 3 gates: Rust fastloop → Python cache → LLM intent
- 70 tokens/query (vs 2000-5000 for competitors)
- Trust scoring per command
- Git-native agent: knowledge as code
- Surfaces: CLI, Telegram, HTTP API, TUI

The 3 gates map to the conservation law:
- Gate 1 (Rust, 50µs, template match) = γ-dominant (no LLM cost)
- Gate 2 (Python, 200µs, cache hit) = mixed
- Gate 3 (LLM, 500ms, intent) = η-dominant (LLM cost)
"""
import json
from pathlib import Path

LEVER_RUNNER_MODULES = [
    # The 3 gates
    ("gate1_rust_fastloop", "Template match: 'check disk' → 'df -h'. 50µs. No LLM.", "rust"),
    ("gate2_python_cache", "Embedding cache: 44% hit rate. 200µs. No LLM on hit.", "python"),
    ("gate3_llm_intent", "LLM intent extraction: 'check disk' → 'show disk usage'. 500ms. 70 tokens.", "python"),
    # The trust system
    ("trust_score", "Per-command trust score (0-100). Auto-promotes on success, demotes on failure.", "python"),
    ("sandbox_exec", "Per-session sandbox in /tmp/lever-runner/<id>/. Hard timeout 30s. No secrets.", "python"),
    # The git-native agent
    ("skill_pack", "JSONL of commands. Version-controlled. Forkable. Auditable.", "jsonl"),
    ("export_import", "lever export > skills.jsonl. lever import skills.jsonl.", "python"),
    ("pincher_nail", "Export for pincherOS. .nail files. Agent state migration.", "python"),
    # The surfaces
    ("surface_cli", "CLI: 'lever check disk'. Bash/zsh. Most common surface.", "python"),
    ("surface_telegram", "Telegram bot: '/do check disk'. /teach to add.", "python"),
    ("surface_http", "HTTP API: POST /run. Port 8765. JSON in/out.", "python"),
    ("surface_tui", "TUI: 'lever tui'. v0.5 planned. Terminal UI.", "rust"),
    ("surface_web", "Web UI: v0.6 planned. Browser-based dashboard.", "typescript"),
    ("surface_gradio", "Gradio: 'docker compose up'. Containerized UI.", "python"),
    # The auto-improve loop
    ("auto_promote", "Hourly cron. Promote winners (20+ successes), surface failures.", "python"),
    # The architecture
    ("passthrough_mode", "Zero LLM. Words → search key. $0/month. Offline.", "python"),
    ("local_llm", "Ollama. llama3.1:8b-instruct-q4_K_M. Local inference.", "python"),
    ("cloud_llm", "OpenAI/Anthropic. Highest accuracy. Pay per token.", "python"),
    # The built-ins
    ("builtin_67", "67 built-in commands seeded on first run.", "python"),
    # The sister repos
    ("sister_pincherOS", "pincherOS — agent runtime with reflex caching.", "rust"),
    ("sister_tile_compiler", "tile-compiler — strategy compilation (zero-dep).", "python"),
    ("sister_zeroclaw_arena", "zeroclaw-arena — self-improving game agents.", "python"),
    ("sister_PLATO", "PLATO — orchestration, distillation, rooms.", "python"),
]


def make_cell(name, description, language):
    primitives = []
    if "gate" in name:
        if "gate1" in name:
            primitives = ["Spawn", "Observe"]  # γ-dominant
        elif "gate2" in name:
            primitives = ["Spawn", "Observe", "Mutate"]  # mixed
        else:  # gate3
            primitives = ["Spawn", "Send", "Receive", "JEPA"]  # η-dominant
    elif "trust" in name or "sandbox" in name:
        primitives = ["Spawn", "Observe", "GC"]  # safety
    elif "surface" in name:
        primitives = ["Spawn", "Send", "Receive", "Observe"]  # I/O
    elif "builtin" in name or "sister" in name:
        primitives = ["Spawn", "Observe"]  # reference
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"lever_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("_", " ").title().replace(" ", "")},
        "description": description,
        "language": language,
        "primitives": primitives,
        "z_in": {"input": "user intent phrase"},
        "z_out": {"output": "shell command result"},
        "jepa": {"predict": "intent → command", "observe": "actual command"},
        "double_entry": {"gamma": 0.7, "eta": 0.3},  # Executors are γ-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "executing"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "run", "args": ["str"], "returns": "Result"},
            {"name": "teach", "args": ["str", "str"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/lever-runner/{name}",
            "scale": 0,
            "room": "ExecutionRoom",
            "protocol": "Shell",
            "form": name,
            "state": "ready"
        },
        "tags": ["lever-runner", "executor", "trust", language]
    }


def make_meta_cells():
    return [
        {
            "id": "lever_runner_meta",
            "kind": "cell",
            "form": {"name": "LeverRunnerMeta"},
            "description": "lever-runner IS the executor substrate of Quilt. The trust compiler: teach once, run forever. The 3 gates map to the conservation law (γ = work done, η = tokens spent). 70 tokens/query (vs 2000-5000 for competitors). The cell at level 3 (harness) needs an executor; lever-runner is that executor.",
            "primitives": ["Observe"] * 22,
            "z_in": {"trust_compiler": "yes", "git_native": "yes", "passthrough": "yes"},
            "z_out": {"proof": "executor = cell substrate"},
            "jepa": {"predict": "lever = executor", "verified": True},
            "double_entry": {"gamma": 0.7, "eta": 0.3},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"lever_{n.replace('-', '_')}" for n, _, _ in LEVER_RUNNER_MODULES]},
            "openers": [
                {"name": "run", "args": ["str"], "returns": "Result"},
                {"name": "teach", "args": ["str"], "returns": "Unit"},
                {"name": "trust", "args": ["str"], "returns": "int"},
            ],
            "tags": ["meta", "executor", "lever-runner"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in LEVER_RUNNER_MODULES:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    # All gates flow to sandbox
    for n, _, _ in LEVER_RUNNER_MODULES:
        if n.startswith("gate"):
            edges.append({"from": f"lever_{n.replace('-', '_')}", "to": "lever_sandbox_exec", "kind": "executes", "weight": 1.0})
    # All surfaces feed gate 1
    for n, _, _ in LEVER_RUNNER_MODULES:
        if n.startswith("surface"):
            edges.append({"from": f"lever_{n.replace('-', '_')}", "to": "lever_gate1_rust_fastloop", "kind": "calls", "weight": 0.8})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "lever-runner-to-quilt",
        "description": "Bridge mapping lever-runner to Quilt. lever-runner is the executor substrate — the trust compiler, git-native agent, 3-gate executor.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-repo", "name": "lever-runner", "org": "SuperInstance"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "modules": len(LEVER_RUNNER_MODULES),
            "gates": 3,
            "tokens_per_query": 70,
            "competitor_avg_tokens": 3500,
            "tests_passing": 160
        },
        "tags": ["lever-runner", "executor", "trust", "git-native", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/lever_runner_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
