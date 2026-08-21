#!/usr/bin/env python3
"""
grand_pattern_to_quilt.py — Convert the Grand Pattern architecture to a Quilt sheet.

The Grand Pattern = Fibonacci dual-direction architecture:
  - Perception DB (Z_in)
  - Prediction DB (Z_out)
  - JEPA mapping (cross-DB surprise)
  - Vibe (position, velocity, acceleration)
  - GC (3-phase: merge → decay → prune)
  - Cellular graph (rooms as nodes, edges as algorithms, murmur as gossip)

Each component becomes a Quilt cell. The double-entry bookkeeping becomes a
cell with TWO input edges (one from Z_in, one from Z_out) and TWO output edges
(both must balance). The whole architecture is a Quilt sheet.

The 12 polyformalism ports become 12 sibling cells in the same sheet:
  - Fortran 2018
  - C
  - C++
  - Rust
  - Go
  - Chapel 2.x
  - Mojo
  - CUDA C++
  - NVIDIA PTX
  - OpenCL
  - Claude's implementation (LLM-authored)
  - Kimi's implementation (LLM-authored)

Plus the supporting fibonacci family:
  - fibonacci-growth (CR = 1/φ attractor)
  - fibonacci-fence (budget governor)
  - fibonacci-heap (data structure)
  - ternary-fib (Z₃ sequences)
  - spline-spectral (B-splines as spectral objects)
  - deadband-rs (Eisenstein, Berlekamp-Massey, Fibonacci spiral)
  - spectral-graph-v2 (Fibonacci growth + adaptive thresholds)
  - fibonacci-growth-v2
  - lau-fibonacci-growth

Total: ~80 cells.

Usage: python3 grand_pattern_to_quilt.py
Output: /workspace/superinstance-website/bridges/grand-pattern-quilt.qzt
"""

import json
import math
import time
from pathlib import Path

# ============================================================================
# Grand Pattern state
# ============================================================================
PHI = 1.618033988749895
INV_PHI = 0.618033988749895
EMBEDDING_DIM = 8

# The Grand Pattern primitives
PRIMITIVES = [
    {
        "name": "Z_in",
        "kind": "perception_db",
        "description": "Perception database — incoming sensor embeddings",
        "icon": "👁",
    },
    {
        "name": "Z_out",
        "kind": "prediction_db",
        "description": "Prediction database — predicted future embeddings",
        "icon": "🔮",
    },
    {
        "name": "JEPA",
        "kind": "jepa_mapping",
        "description": "JEPA mapping — cross-DB comparison, computes surprise",
        "icon": "🧠",
    },
    {
        "name": "DoubleEntry",
        "kind": "bookkeeping",
        "description": "Double-entry bookkeeping — every tick updates BOTH databases",
        "icon": "📒",
    },
    {
        "name": "Vibe",
        "kind": "vibe",
        "description": "Vibe — (position, velocity, acceleration) tuple on the embedding manifold",
        "icon": "🌊",
    },
    {
        "name": "GC",
        "kind": "gc",
        "description": "3-phase garbage collection — merge similar → decay old → prune weak",
        "icon": "🧹",
    },
    {
        "name": "CellularGraph",
        "kind": "graph",
        "description": "Cellular graph — rooms as nodes, algorithms as edges, murmur as gossip",
        "icon": "🕸",
    },
    {
        "name": "Murmur",
        "kind": "gossip",
        "description": "Murmur protocol — gossip between rooms",
        "icon": "📡",
    },
]

# The 12 polyformalism ports of the Grand Pattern
PORTS = [
    {"name": "fortran", "lang": "Fortran 2018", "repo": "grand-pattern-fortran", "icon": "🟦"},
    {"name": "c", "lang": "C", "repo": "grand-pattern-c", "icon": "🔷"},
    {"name": "cpp", "lang": "C++", "repo": "grand-pattern-cpp", "icon": "➕"},
    {"name": "rust", "lang": "Rust", "repo": "grand-pattern-rs", "icon": "🦀"},
    {"name": "go", "lang": "Go", "repo": "grand-pattern-go", "icon": "🐹"},
    {"name": "chapel", "lang": "Chapel 2.x", "repo": "grand-pattern-chapel", "icon": "⛪"},
    {"name": "mojo", "lang": "Mojo 🔥", "repo": "grand-pattern-mojo", "icon": "🔥"},
    {"name": "cuda", "lang": "CUDA C++", "repo": "grand-pattern-cuda", "icon": "🟢"},
    {"name": "ptx", "lang": "NVIDIA PTX", "repo": "grand-pattern-ptx", "icon": "🟡"},
    {"name": "opencl", "lang": "OpenCL", "repo": "grand-pattern-opencl", "icon": "🔵"},
    {"name": "claude", "lang": "Claude", "repo": "grand-pattern-claude", "icon": "🤖"},
    {"name": "kimi", "lang": "Kimi", "repo": "grand-pattern-kimi", "icon": "🌙"},
]

# The supporting Fibonacci family
FIBONACCI_FAMILY = [
    {"name": "growth", "lang": "Rust", "repo": "fibonacci-growth", "desc": "CR = 1/φ attractor — Penrose outward, Mandelbrot inward", "icon": "📈"},
    {"name": "fence", "lang": "Python", "repo": "fibonacci-fence", "desc": "Budget governor scaling by golden ratio", "icon": "🚧"},
    {"name": "heap", "lang": "Rust", "repo": "fibonacci-heap", "desc": "Classic Fibonacci heap data structure", "icon": "🥞"},
    {"name": "ternary", "lang": "Rust", "repo": "ternary-fib", "desc": "Fib in Z₃ — balanced ternary, tribonacci", "icon": "3️⃣"},
    {"name": "spline", "lang": "Rust", "repo": "spline-spectral", "desc": "B-splines as spectral objects (Cox-de Boor = Fibonacci)", "icon": "〰️"},
    {"name": "deadband", "lang": "Rust", "repo": "deadband-rs", "desc": "Eisenstein, Berlekamp-Massey, Fibonacci spiral", "icon": "📏"},
    {"name": "spectral-v2", "lang": "Rust", "repo": "spectral-graph-v2", "desc": "Fib growth + adaptive thresholds + negative space", "icon": "🌐"},
    {"name": "growth-v2", "lang": "Rust", "repo": "fibonacci-growth-v2", "desc": "Scaling dynamics for distributed agent systems", "icon": "📊"},
    {"name": "lau-growth", "lang": "Rust", "repo": "lau-fibonacci-growth", "desc": "Fib growth patterns for agent capability dev", "icon": "🌱"},
    {"name": "grand-c", "lang": "C", "repo": "grand-pattern-c", "desc": "Grand Pattern — C", "icon": "🔷"},
    {"name": "grand-claude", "lang": "Rust", "repo": "grand-pattern-claude", "desc": "Claude's Grand Pattern — AI-authored", "icon": "🤖"},
    {"name": "grand-kimi", "lang": "Rust", "repo": "grand-pattern-kimi", "desc": "Kimi's Grand Pattern — AI-authored", "icon": "🌙"},
]


def synth_embedding(seed: int, predicted: bool = False) -> list:
    """Synthesize an 8D embedding (mirrors the Rust grand-pattern-rs)."""
    arr = []
    for i in range(EMBEDDING_DIM):
        base = math.sin(seed * (i + 1) * 1.7 + (0.1 if predicted else 0)) * 0.5
        arr.append(base)
    return arr


def build_sheet():
    """Build the Quilt sheet representing the Grand Pattern."""
    cells = []

    # 1. The Grand Pattern primitives
    for i, p in enumerate(PRIMITIVES):
        # Compute the canonical address once
        p["address"] = f"pattern.{p['name'].lower()}"
        for dim in ["name", "description", "kind", "icon", "address"]:
            cells.append({
                "address": f"pattern.{p['name'].lower()}.{dim}",
                "kind": "string",
                "value": str(p[dim]),
            })
        # Embedding fingerprint
        emb = synth_embedding(i, False)
        for j in range(EMBEDDING_DIM):
            cells.append({
                "address": f"pattern.{p['name'].lower()}.embed[{j}]",
                "kind": "f64",
                "value": emb[j],
            })

    # 2. The 12 polyformalism ports
    for i, port in enumerate(PORTS):
        for dim in ["name", "lang", "repo", "icon"]:
            cells.append({
                "address": f"port.{port['name']}.{dim}",
                "kind": "string",
                "value": port[dim],
            })
        # Embedding
        emb = synth_embedding(i + 100, True)
        for j in range(EMBEDDING_DIM):
            cells.append({
                "address": f"port.{port['name']}.embed[{j}]",
                "kind": "f64",
                "value": emb[j],
            })

    # 3. The supporting Fibonacci family
    for i, fam in enumerate(FIBONACCI_FAMILY):
        for dim in ["name", "lang", "repo", "desc", "icon"]:
            cells.append({
                "address": f"family.{fam['name']}.{dim}",
                "kind": "string",
                "value": fam[dim],
            })
        # Embedding
        emb = synth_embedding(i + 200, True)
        for j in range(EMBEDDING_DIM):
            cells.append({
                "address": f"family.{fam['name']}.embed[{j}]",
                "kind": "f64",
                "value": emb[j],
            })

    # 4. Cross-cutting concepts (the "physics" cells)
    concepts = [
        {"name": "phi", "val": PHI, "kind": "f64"},
        {"name": "inv_phi", "val": INV_PHI, "kind": "f64"},
        {"name": "embedding_dim", "val": EMBEDDING_DIM, "kind": "usize"},
        {"name": "cr_target", "val": INV_PHI, "kind": "f64"},
        {"name": "ports_count", "val": 12, "kind": "usize"},
        {"name": "primitives_count", "val": 8, "kind": "usize"},
        {"name": "family_count", "val": len(FIBONACCI_FAMILY), "kind": "usize"},
        {"name": "now", "val": time.time(), "kind": "f64"},
    ]
    for c in concepts:
        cells.append({
            "address": f"stats.{c['name']}",
            "kind": c["kind"],
            "value": c["val"],
        })

    # 5. Edges (the algorithms)
    # Each primitive connects to every other primitive (the algorithm is "tick")
    edges = []
    for i, p1 in enumerate(PRIMITIVES):
        for j, p2 in enumerate(PRIMITIVES):
            if i < j:
                edges.append({
                    "from": f"pattern.{p1['name'].lower()}",
                    "to": f"pattern.{p2['name'].lower()}",
                    "kind": "tick",
                })
    # Each port supports each primitive
    for port in PORTS:
        for prim in PRIMITIVES:
            edges.append({
                "from": f"port.{port['name']}",
                "to": f"pattern.{prim['name'].lower()}",
                "kind": "implements",
            })
    # Each family member relates to the pattern primitives
    for fam in FIBONACCI_FAMILY:
        edges.append({
            "from": f"family.{fam['name']}",
            "to": "pattern.growth",
            "kind": "scales",
        })
    # JEPA connects Z_in and Z_out specifically
    edges.append({
        "from": "pattern.z_in",
        "to": "pattern.jepa",
        "kind": "input",
    })
    edges.append({
        "from": "pattern.z_out",
        "to": "pattern.jepa",
        "kind": "input",
    })
    edges.append({
        "from": "pattern.jepa",
        "to": "pattern.vibe",
        "kind": "surprise_drives",
    })
    edges.append({
        "from": "pattern.vibe",
        "to": "pattern.gc",
        "kind": "weak_vibes_pruned",
    })

    # 6. Rooms (the high-level containers)
    rooms = [
        {
            "id": "pattern",
            "name": "🏛 Pattern — the 8 primitives",
            "cell_count": 8 * (5 + EMBEDDING_DIM),
        },
        {
            "id": "port",
            "name": "🌐 12 language ports — polyformalism",
            "cell_count": 12 * (4 + EMBEDDING_DIM),
        },
        {
            "id": "family",
            "name": "🌀 Fibonacci family — the supports",
            "cell_count": len(FIBONACCI_FAMILY) * (5 + EMBEDDING_DIM),
        },
    ]

    return {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "Grand Pattern as Quilt sheet",
            "description": (
                "The Grand Pattern (Fibonacci dual-direction architecture) is the Quilt "
                "cell model. Perception DB → Z_in cell; Prediction DB → Z_out cell; JEPA → "
                "the cell evaluator; double-entry → the cell's input/output balance; Vibe → "
                "the cell's metadata; GC → the cell's lifecycle; Cellular graph → the Quilt "
                "sheet. The 12 polyformalism ports are the back-pressure demonstrating the "
                "pattern survives translation."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "grandpattern",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "pattern_primitives": len(PRIMITIVES),
            "polyformalism_ports": len(PORTS),
            "family_members": len(FIBONACCI_FAMILY),
        },
    }


def main():
    sheet = build_sheet()
    out_path = Path("/workspace/superinstance-website/bridges/grand-pattern-quilt.qzt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(sheet, f, indent=2)
    print(f"✓ Wrote {out_path}")
    print(f"  cells: {sheet['stats']['total_cells']}")
    print(f"  rooms: {sheet['stats']['total_rooms']}")
    print(f"  edges: {sheet['stats']['total_edges']}")
    print(f"  primitives: {sheet['stats']['pattern_primitives']}")
    print(f"  ports: {sheet['stats']['polyformalism_ports']}")
    print(f"  family: {sheet['stats']['family_members']}")


if __name__ == "__main__":
    main()
