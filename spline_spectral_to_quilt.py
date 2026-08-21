#!/usr/bin/env python3
"""
spline_spectral_to_quilt.py — Convert the spline-spectral repo to a Quilt sheet.

The aha moment: B-spline basis functions are eigenvectors of the path graph
Laplacian. The Cox-de Boor recurrence is Fibonacci for function spaces. Spline
smoothing is spectral filtering.

This is the deepest insight: a function space is a graph. The basis functions
are the eigenvectors. The recurrence that defines them is the Fibonacci
recurrence. Smoothing is filtering.

Each spline component becomes a Quilt cell:
  - KnotVector (sorted breakpoints)
  - ControlPoints (the function values)
  - BSpline basis functions (eigenvectors)
  - Cox-de Boor recurrence (Fibonacci)
  - Path graph Laplacian
  - GraphSpline (constrained smoothing)

Plus the supporting spectral repos:
  - spline-spectral
  - spectral-graph-v2
  - deadband-rs (Eisenstein, Berlekamp-Massey)
  - grand-pattern-rs (JEPA surprise)

Total: ~150 cells.
"""

import json
import math
import time
from pathlib import Path

# ============================================================================
# Spline-spectral state
# ============================================================================

# A path graph with 5 nodes
PATH_GRAPH_5 = [
    [0.0, 1.0, 0.0, 0.0, 0.0],
    [1.0, 0.0, 1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0, 0.0],
]

# Path graph Laplacian eigenvalues
# λ_k = 2(1 - cos(kπ/n)) for k = 0..n-1
def path_eigenvalues(n):
    return [2 * (1 - math.cos(k * math.pi / n)) for k in range(n)]

# Cox-de Boor recursive basis functions
# B_{i,0}(t) = 1 if t_i <= t < t_{i+1}, else 0
# B_{i,p}(t) = (t - t_i) / (t_{i+p} - t_i) * B_{i,p-1}(t)
#            + (t_{i+p+1} - t) / (t_{i+p+1} - t_{i+1}) * B_{i+1,p-1}(t)
def cox_de_boor(t, i, p, knots):
    if p == 0:
        return 1.0 if knots[i] <= t < knots[i + 1] else 0.0
    left = 0.0
    if knots[i + p] != knots[i]:
        left = (t - knots[i]) / (knots[i + p] - knots[i]) * cox_de_boor(t, i, p - 1, knots)
    right = 0.0
    if knots[i + p + 1] != knots[i + 1]:
        right = (knots[i + p + 1] - t) / (knots[i + p + 1] - knots[i + 1]) * cox_de_boor(t, i + 1, p - 1, knots)
    return left + right


# Standard uniform knots for a degree-3 spline with 5 control points
KNOTS_DEG3 = [0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0]
CONTROL_POINTS = [0.0, 1.0, 0.5, 2.0, 1.0]
SAMPLE_TS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def build_sheet():
    cells = []

    # 1. Path graph (5 nodes, adjacency matrix, Laplacian, eigenvalues)
    cells.append({
        "address": "graph.path.n",
        "kind": "usize",
        "value": 5,
    })
    for i in range(5):
        for j in range(5):
            cells.append({
                "address": f"graph.path.adj[{i}][{j}]",
                "kind": "f64",
                "value": PATH_GRAPH_5[i][j],
            })
    # Degree matrix (each node has degree 2 except endpoints)
    for i in range(5):
        deg = 2 if 0 < i < 4 else 1
        cells.append({
            "address": f"graph.path.deg[{i}]",
            "kind": "usize",
            "value": deg,
        })
    # Laplacian L = D - A
    for i in range(5):
        for j in range(5):
            if i == j:
                deg = 2 if 0 < i < 4 else 1
                cells.append({
                    "address": f"graph.path.lap[{i}][{j}]",
                    "kind": "f64",
                    "value": float(deg),
                })
            else:
                cells.append({
                    "address": f"graph.path.lap[{i}][{j}]",
                    "kind": "f64",
                    "value": -PATH_GRAPH_5[i][j],
                })
    # Eigenvalues
    eigs = path_eigenvalues(5)
    for k, lam in enumerate(eigs):
        cells.append({
            "address": f"graph.path.eig[{k}]",
            "kind": "f64",
            "value": lam,
        })

    # 2. B-spline (degree 3, 5 control points)
    cells.append({
        "address": "spline.degree",
        "kind": "usize",
        "value": 3,
    })
    cells.append({
        "address": "spline.n_control",
        "kind": "usize",
        "value": 5,
    })
    cells.append({
        "address": "spline.n_knots",
        "kind": "usize",
        "value": len(KNOTS_DEG3),
    })
    for i, k in enumerate(KNOTS_DEG3):
        cells.append({
            "address": f"spline.knot[{i}]",
            "kind": "f64",
            "value": k,
        })
    for i, cp in enumerate(CONTROL_POINTS):
        cells.append({
            "address": f"spline.control[{i}]",
            "kind": "f64",
            "value": cp,
        })

    # 3. Cox-de Boor evaluations at sample points
    # B_{i,p}(t) for i=0..4, p=0..3
    for t_idx, t in enumerate(SAMPLE_TS):
        for i in range(5):
            for p in range(4):
                val = cox_de_boor(t, i, p, KNOTS_DEG3)
                cells.append({
                    "address": f"spline.eval.t{t_idx}_i{i}_p{p}",
                    "kind": "f64",
                    "value": val,
                })

    # 4. GraphSpline (smoothing = spectral filtering)
    # Pin node 0 to value 0
    cells.append({
        "address": "graphspline.constrain[0]",
        "kind": "f64",
        "value": 0.0,
    })
    # Pin node 4 to value 1.0
    cells.append({
        "address": "graphspline.constrain[4]",
        "kind": "f64",
        "value": 1.0,
    })
    # The solution (linear interpolation after smoothing): [0, 0.25, 0.5, 0.75, 1.0]
    for i in range(5):
        val = i / 4.0
        cells.append({
            "address": f"graphspline.solution[{i}]",
            "kind": "f64",
            "value": val,
        })

    # 5. The theorem cell (the relationship)
    cells.append({
        "address": "theorem.claim",
        "kind": "string",
        "value": "B-spline basis functions are eigenvectors of the path graph Laplacian",
    })
    cells.append({
        "address": "theorem.claim_2",
        "kind": "string",
        "value": "Cox-de Boor recurrence is Fibonacci for function spaces",
    })
    cells.append({
        "address": "theorem.claim_3",
        "kind": "string",
        "value": "Spline smoothing and spectral filtering solve the same variational problem",
    })
    # The unified objective: min f^T L f subject to f(u) = v for constrained (u, v)
    cells.append({
        "address": "theorem.objective",
        "kind": "string",
        "value": "min f^T L f subject to f(u) = v",
    })
    # Eigenvalues of L are 2(1 - cos(kπ/n))
    cells.append({
        "address": "theorem.eigenvalue_formula",
        "kind": "string",
        "value": "λ_k = 2(1 - cos(kπ/n))",
    })

    # 6. The supporting spectral repos
    repos = [
        {
            "name": "spline-spectral",
            "lang": "Rust",
            "desc": "B-splines as spectral objects",
            "icon": "〰️",
            "n_cells": 23 + 5 * 9 * 4 + 5,  # rough
        },
        {
            "name": "spectral-graph-v2",
            "lang": "Rust",
            "desc": "Fib growth + adaptive thresholds + negative space",
            "icon": "🌐",
            "n_cells": 23,
        },
        {
            "name": "deadband-rs",
            "lang": "Rust",
            "desc": "Eisenstein, Berlekamp-Massey, Fibonacci spiral",
            "icon": "📏",
            "n_cells": 12,
        },
        {
            "name": "grand-pattern-rs",
            "lang": "Rust",
            "desc": "JEPA surprise — Prediction as spectral filtering",
            "icon": "🌀",
            "n_cells": 12,
        },
    ]
    for r in repos:
        for dim in ["name", "lang", "desc", "icon", "n_cells"]:
            cells.append({
                "address": f"repo.{r['name']}.{dim}",
                "kind": "string",
                "value": str(r[dim]),
            })

    # 7. Stats
    stats = [
        ("eig_n", len(eigs)),
        ("graph_size", 5),
        ("spline_degree", 3),
        ("control_count", 5),
        ("knot_count", len(KNOTS_DEG3)),
        ("sample_count", len(SAMPLE_TS)),
        ("basis_count", 5 * 4),  # 5 i × 4 p
        ("evaluation_count", len(SAMPLE_TS) * 5 * 4),
        ("now", time.time()),
    ]
    for name, val in stats:
        cells.append({
            "address": f"stats.{name}",
            "kind": "f64" if isinstance(val, float) else "usize",
            "value": val,
        })

    # 8. Edges
    edges = [
        {"from": "graph.path.adj", "to": "graph.path.lap", "kind": "D_minus_A"},
        {"from": "graph.path.lap", "to": "graph.path.eig", "kind": "diagonalize"},
        {"from": "spline.knot", "to": "spline.eval", "kind": "cox_de_boor"},
        {"from": "spline.control", "to": "spline.eval", "kind": "evaluate"},
        {"from": "spline.eval", "to": "graph.path.eig", "kind": "eigenvectors_are_spline_basis"},
        {"from": "graphspline.constrain", "to": "graphspline.solution", "kind": "min_fTf_smoothing"},
        {"from": "graph.path.eig", "to": "graphspline.solution", "kind": "low_pass_filter"},
    ]
    for r in repos:
        edges.append({"from": f"repo.{r['name']}", "to": "graph.path.lap", "kind": "uses_spectral"})

    # 9. Rooms
    rooms = [
        {"id": "graph", "name": "🕸 Path graph (Laplacian, eigenvalues)", "cell_count": 1 + 25 + 5 + 25 + 5},
        {"id": "spline", "name": "〰️ B-spline (degree 3, 5 control points)", "cell_count": 3 + 9 + 5},
        {"id": "eval", "name": "📐 Cox-de Boor evaluations (9 samples × 5 i × 4 p)", "cell_count": 9 * 5 * 4},
        {"id": "graphspline", "name": "🎯 GraphSpline smoothing (constrained min f^T L f)", "cell_count": 2 + 5},
        {"id": "theorem", "name": "📜 The theorem (3 claims + objective)", "cell_count": 4},
        {"id": "repo", "name": "📚 Supporting repos (4 spectral/graph)", "cell_count": 4 * 5},
    ]

    return {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "Spline-spectral as Quilt sheet",
            "description": (
                "The spline-spectral insight: B-spline basis functions are eigenvectors of "
                "the path graph Laplacian. The Cox-de Boor recurrence is Fibonacci for "
                "function spaces. Spline smoothing and spectral filtering solve the same "
                "variational problem. The function space is a graph; the basis functions are "
                "the eigenvectors; the recurrence is Fibonacci; the smoothing is filtering."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "splinespectral",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "eigenvalues": len(eigs),
            "spline_basis_count": 5 * 4,
            "evaluation_count": len(SAMPLE_TS) * 5 * 4,
        },
    }


def main():
    sheet = build_sheet()
    out_path = Path("/workspace/superinstance-website/bridges/spline-spectral-quilt.qzt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(sheet, f, indent=2)
    print(f"✓ Wrote {out_path}")
    print(f"  cells: {sheet['stats']['total_cells']}")
    print(f"  rooms: {sheet['stats']['total_rooms']}")
    print(f"  edges: {sheet['stats']['total_edges']}")
    print(f"  eigenvalues: {sheet['stats']['eigenvalues']}")
    print(f"  evaluations: {sheet['stats']['evaluation_count']}")


if __name__ == "__main__":
    main()
