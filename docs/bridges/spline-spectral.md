# Bridge: spline-spectral → Quilt

| | |
|---|---|
| **Script** | `spline_spectral_to_quilt.py` |
| **Source repo** | [SuperInstance/spline-spectral](https://github.com/SuperInstance/spline-spectral) |
| **Target** | `spline-spectral-quilt.qzt` — **299 cells, 11 edges** |
| **CLI** | `python3 spline_spectral_to_quilt.py` |

## What the source is

The aha moment: **B-spline basis functions are eigenvectors of the path graph Laplacian.** The Cox-de Boor recurrence is Fibonacci for function spaces. Spline smoothing is spectral filtering. The deepest insight in the repo: *a function space is a graph* — the basis functions are its eigenvectors, the recurrence that defines them is the Fibonacci recurrence, and smoothing is filtering.

## What the cells mean

| Address | Meaning |
|---|---|
| `graph.path.*` | the path graph itself — `graph.path.n` (5 nodes), `graph.path.adj[i][j]` adjacency entries |
| `graph.laplacian.*` | path graph Laplacian, eigenvalues λ_k = 2(1 − cos(kπ/n)) |
| `spline.knots.*` | KnotVector — sorted breakpoints |
| `spline.control.*` | ControlPoints — the function values |
| `spline.basis.*` | B-spline basis functions — the eigenvectors |
| `spline.cox_de_boor.*` | the Cox-de Boor recurrence — Fibonacci for function spaces |
| `spline.graph_spline.*` | GraphSpline — constrained smoothing |

Plus the supporting spectral family: `spectral-graph-v2` (Fibonacci growth + adaptive thresholds), `deadband-rs` (Eisenstein, Berlekamp-Massey), and `grand-pattern-rs` (JEPA surprise).

## How it renders

- **TOP** — the path graph and its adjacency structure
- **FRONT** — basis functions and control points as signals
- **SIDE** — the recurrence building the function space over time

## Example output

```json
{ "address": "graph.path.n", "kind": "usize", "value": 5 },
{ "address": "graph.path.adj[0][1]", "kind": "float", "value": 1.0 }
```
