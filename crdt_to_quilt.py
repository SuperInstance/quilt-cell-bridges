#!/usr/bin/env python3
"""
crdt_to_quilt.py — The CRDT family as a Quilt sheet.

CRDTs (Conflict-free Replicated Data Types) are the lingua franca of
distributed state. Each one has a merge operation that's mathematically
guaranteed to converge regardless of operation order. They're the
canonical protocol-agnostic cell-to-cell sync.

The user's CRDT family:
  - crdt-core: G-Counter, PN-Counter, G-Set, OR-Set, LWW-Register
  - crdt-gset, crdt-orset, crdt-lwwreg, crdt-gcounter, crdt-pnvector
  - crdt-map: composite CRDTs
  - SmartCRDT: monorepo with all of the above + vector search
  - fleet-crdt: constraint-preserving merge
  - constraint-crdt: CRDT-backed constraint states
  - crdt-bench: cross-language performance bake-off (7 languages)
  - oxide-crdt: GPU-aware CRDTs
  - ternary-antidote: CRDTs with ternary merge outcomes
  - lau-calm-crdt: CALM theorem formal convergence guarantees
  - CRDT_Research: intra-chip communication for AI workloads

The thesis: a CRDT IS a Quilt cell. The merge operation IS the cell's
gossip. The types (G-Counter, OR-Set, LWW-Register) are the cell kinds.
The cross-language bake-off IS the polyformalism demonstration.

This bridge creates a Quilt sheet that represents the CRDT family as cells.
"""

import json
import time
from pathlib import Path

# ============================================================================
# CRDT family
# ============================================================================
CRDT_TYPES = [
    {
        "id": "gcounter", "name": "G-Counter",
        "merge": "max (component-wise)",
        "ops": ["increment"],
        "complexity": "O(n) nodes",
        "properties": ["monotonic", "commutative", "idempotent"],
        "icon": "📈",
    },
    {
        "id": "pncounter", "name": "PN-Counter",
        "merge": "(G+ ⊔ G+) − (G− ⊔ G−)",
        "ops": ["increment", "decrement"],
        "complexity": "O(n) nodes",
        "properties": ["commutative", "idempotent"],
        "icon": "📉",
    },
    {
        "id": "gset", "name": "G-Set",
        "merge": "∪ (union)",
        "ops": ["add"],
        "complexity": "O(|set|)",
        "properties": ["grow-only", "commutative", "idempotent"],
        "icon": "➕",
    },
    {
        "id": "orset", "name": "OR-Set",
        "merge": "add ∪ remove with causal",
        "ops": ["add", "remove"],
        "complexity": "O(|set| × |tombstones|)",
        "properties": ["observed-remove", "causal"],
        "icon": "🔄",
    },
    {
        "id": "lww", "name": "LWW-Register",
        "merge": "max(timestamp)",
        "ops": ["set"],
        "complexity": "O(1)",
        "properties": ["last-writer-wins", "value-blind"],
        "icon": "🏆",
    },
    {
        "id": "pnvector", "name": "PN-Vector",
        "merge": "element-wise max (P) / min (N)",
        "ops": ["increment", "decrement"],
        "complexity": "O(n) per dimension",
        "properties": ["commutative", "idempotent"],
        "icon": "🎯",
    },
    {
        "id": "rga", "name": "RGA (Replicated Growable Array)",
        "merge": "causal ordering + tombstone",
        "ops": ["insert", "delete"],
        "complexity": "O(n²) worst case",
        "properties": ["ordered", "causal"],
        "icon": "📜",
    },
]

# The CRDT repos
CRDT_REPOS = [
    {"name": "crdt-core", "lang": "Rust", "types": ["G-Counter", "PN-Counter", "G-Set", "OR-Set", "LWW-Register"]},
    {"name": "crdt-gset", "lang": "Rust", "types": ["G-Set"]},
    {"name": "crdt-orset", "lang": "Rust", "types": ["OR-Set"]},
    {"name": "crdt-lwwreg", "lang": "Rust", "types": ["LWW-Register"]},
    {"name": "crdt-gcounter", "lang": "Rust", "types": ["G-Counter"]},
    {"name": "crdt-pnvector", "lang": "Rust", "types": ["PN-Vector"]},
    {"name": "crdt-map", "lang": "Rust", "types": ["Composite Map"]},
    {"name": "SmartCRDT", "lang": "TypeScript", "types": ["G-Counter", "PN-Counter", "OR-Set", "LWW-Register", "RGA"]},
    {"name": "fleet-crdt", "lang": "Rust", "types": ["Constraint-State"]},
    {"name": "constraint-crdt", "lang": "Rust", "types": ["Constraint CRDT"]},
    {"name": "crdt-bench", "lang": "C/CUDA/PTX", "types": ["G-Counter", "Bloom Filter"]},
    {"name": "oxide-crdt", "lang": "Rust", "types": ["GPU-Aware CRDT"]},
    {"name": "ternary-antidote", "lang": "Rust", "types": ["G-Counter", "LWW-Register", "Ternary"]},
    {"name": "lau-calm-crdt", "lang": "Rust", "types": ["CALM-CRDT"]},
    {"name": "CRDT_Research", "lang": "Python", "types": ["Intra-Chip CRDT"]},
    {"name": "smartcrdt-fleet-sync", "lang": "Python", "types": ["Fleet Sync"]},
    {"name": "smartcrdt-git-agent", "lang": "Python", "types": ["Git Agent"]},
]

# The cross-language bake-off (from crdt-bench)
BAKE_OFF = [
    {"lang": "Fortran", "time_ns": 0.9, "implementation": "whole-array MAX"},
    {"lang": "Zig", "time_ns": 3.0, "implementation": "scalar loop"},
    {"lang": "Zig", "time_ns": 7.0, "implementation": "@Vector(16) SIMD"},
    {"lang": "Go", "time_ns": 8.3, "implementation": "range loop"},
    {"lang": "C", "time_ns": 10.5, "implementation": "gcc -O2"},
    {"lang": "Go", "time_ns": 10.8, "implementation": "unsafe ptr"},
    {"lang": "Rust", "time_ns": 17.5, "implementation": "for loop"},
]

# The mapping: CRDT type ↔ Quilt cell
CRDT_TO_QUILT = [
    {"from": "G-Counter", "to": "counter_cell", "kind": "implements"},
    {"from": "PN-Counter", "to": "signed_counter_cell", "kind": "implements"},
    {"from": "G-Set", "to": "set_cell", "kind": "implements"},
    {"from": "OR-Set", "to": "observed_set_cell", "kind": "implements"},
    {"from": "LWW-Register", "to": "register_cell", "kind": "implements"},
    {"from": "PN-Vector", "to": "vector_cell", "kind": "implements"},
    {"from": "RGA", "to": "ordered_list_cell", "kind": "implements"},
]


def build_sheet():
    cells = []
    edges = []
    rooms = []

    # 1. CRDT types
    for t in CRDT_TYPES:
        for dim in ["name", "merge", "complexity", "icon"]:
            cells.append({
                "address": f"type.{t['id']}.{dim}",
                "kind": "string",
                "value": t[dim],
            })
        for i, op in enumerate(t["ops"]):
            cells.append({
                "address": f"type.{t['id']}.op[{i}]",
                "kind": "string",
                "value": op,
            })
        for i, p in enumerate(t["properties"]):
            cells.append({
                "address": f"type.{t['id']}.property[{i}]",
                "kind": "string",
                "value": p,
            })
    # 2. CRDT repos
    for r in CRDT_REPOS:
        cells.append({
            "address": f"repo.{r['name']}.name",
            "kind": "string",
            "value": r["name"],
        })
        cells.append({
            "address": f"repo.{r['name']}.lang",
            "kind": "string",
            "value": r["lang"],
        })
        for i, t in enumerate(r["types"]):
            cells.append({
                "address": f"repo.{r['name']}.type[{i}]",
                "kind": "string",
                "value": t,
            })
    # 3. Bake-off
    cells.append({
        "address": "bakeoff.benchmark",
        "kind": "string",
        "value": "G-Counter Merge (32 elements, element-wise max)",
    })
    cells.append({
        "address": "bakeoff.hardware",
        "kind": "string",
        "value": "AMD Ryzen AI 9 HX 370 (Zen 5, 12C/24T, AVX-512)",
    })
    for i, b in enumerate(BAKE_OFF):
        cells.append({
            "address": f"bakeoff.{i}.lang",
            "kind": "string",
            "value": b["lang"],
        })
        cells.append({
            "address": f"bakeoff.{i}.time_ns",
            "kind": "f64",
            "value": b["time_ns"],
        })
        cells.append({
            "address": f"bakeoff.{i}.implementation",
            "kind": "string",
            "value": b["implementation"],
        })
    # 4. CRDT ↔ Quilt mapping
    for m in CRDT_TO_QUILT:
        cells.append({
            "address": f"mapping.{m['from']}.cell",
            "kind": "string",
            "value": m["to"],
        })
        edges.append({
            "from": f"type.{m['from'].lower().replace('-', '')}",
            "to": f"mapping.{m['from']}",
            "kind": "implements",
        })
    # 5. Cross-repo edges: each repo implements one or more types
    for r in CRDT_REPOS:
        for t in r["types"]:
            t_id = t.lower().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            edges.append({
                "from": f"repo.{r['name']}",
                "to": f"type.{t_id}",
                "kind": "implements",
            })
    # 6. The thesis
    cells.append({
        "address": "thesis.claim",
        "kind": "string",
        "value": "A CRDT is a Quilt cell. The merge operation is the cell's gossip.",
    })
    cells.append({
        "address": "thesis.claim_2",
        "kind": "string",
        "value": "The protocol-agnosticism is built into the math, not the implementation.",
    })
    # 7. Stats
    stats = [
        ("crdt_types", len(CRDT_TYPES)),
        ("repos", len(CRDT_REPOS)),
        ("bakeoff_entries", len(BAKE_OFF)),
        ("mappings", len(CRDT_TO_QUILT)),
        ("languages", len(set(r["lang"] for r in CRDT_REPOS))),
        ("fastest_time_ns", min(b["time_ns"] for b in BAKE_OFF)),
        ("slowest_time_ns", max(b["time_ns"] for b in BAKE_OFF)),
        ("now", time.time()),
    ]
    for name, val in stats:
        cells.append({
            "address": f"stats.{name}",
            "kind": "f64" if isinstance(val, float) else "usize",
            "value": val,
        })

    # 8. Rooms
    rooms = [
        {"id": "type", "name": "🔄 CRDT types (7)", "cell_count": sum(4 + 2 * len(t["ops"]) + len(t["properties"]) for t in CRDT_TYPES)},
        {"id": "repo", "name": "📦 CRDT repos (17)", "cell_count": sum(2 + len(r["types"]) for r in CRDT_REPOS)},
        {"id": "bakeoff", "name": "🏁 Cross-language bake-off (7)", "cell_count": 2 + len(BAKE_OFF) * 3},
        {"id": "mapping", "name": "🔁 CRDT ↔ Quilt mapping", "cell_count": len(CRDT_TO_QUILT)},
    ]

    return {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "CRDT family as Quilt sheet",
            "description": (
                "The CRDT family — G-Counter, PN-Counter, G-Set, OR-Set, LWW-Register, "
                "PN-Vector, RGA — ported to Quilt. The CRDT merge operation IS the Quilt "
                "cell's gossip. The protocol-agnosticism is built into the math, not the "
                "implementation. The cross-language bake-off (Fortran, C, Rust, Go, CUDA, "
                "PTX) IS the polyformalism demonstration. The CRDT family shows that the "
                "protocol doesn't matter — only the math does."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "crdt",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "crdt_types": len(CRDT_TYPES),
            "repos": len(CRDT_REPOS),
            "languages": len(set(r["lang"] for r in CRDT_REPOS)),
        },
    }


def main():
    sheet = build_sheet()
    out_path = Path("/workspace/superinstance-website/bridges/crdt-quilt.qzt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(sheet, f, indent=2)
    print(f"✓ Wrote {out_path}")
    s = sheet["stats"]
    print(f"  types: {s['crdt_types']}")
    print(f"  repos: {s['repos']}")
    print(f"  languages: {s['languages']}")
    print(f"  total: {s['total_cells']} cells, {s['total_edges']} edges")


if __name__ == "__main__":
    main()
