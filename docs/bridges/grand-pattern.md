# Bridge: grand-pattern-rs → Quilt

| | |
|---|---|
| **Script** | `grand_pattern_to_quilt.py` |
| **Source repo** | [SuperInstance/grand-pattern-rs](https://github.com/SuperInstance/grand-pattern-rs) |
| **Target** | `grand-pattern-quilt.qzt` — **412 cells, 140 edges** |
| **CLI** | `python3 grand_pattern_to_quilt.py` |

## What the source is

The **Grand Pattern** — a Fibonacci dual-direction architecture: a Perception DB (`Z_in`), a Prediction DB (`Z_out`), a JEPA mapping (cross-DB surprise), Vibe (position / velocity / acceleration), GC (3-phase: merge → decay → prune), and a cellular graph (rooms as nodes, edges as algorithms, murmur as gossip). It is the pattern Quilt was built around — the bridge ports the pattern itself.

## What the cells mean

| Address | Meaning |
|---|---|
| `pattern.z_in.*` | the Perception DB — inputs, embeddings (`pattern.z_in.name`, `pattern.z_in.embed[0..7]`) |
| `pattern.z_out.*` | the Prediction DB — predicted states |
| `pattern.jepa.*` | cross-DB surprise mapping |
| `pattern.vibe.*` | position / velocity / acceleration in the graph |
| `pattern.gc.*` | the 3-phase garbage-collection cycle (merge → decay → prune) |
| double-entry cells | bookkeeping cells with **two input edges** (one from Z_in, one from Z_out) and **two output edges** — both must balance |

Plus the **12 polyformalism ports** as 12 sibling cells in the same sheet (Fortran 2018, C, C++, Rust, Go, Chapel 2.x, Mojo, CUDA C++, NVIDIA PTX, OpenCL, and Claude's and Kimi's LLM-authored implementations), and the supporting fibonacci family (`fibonacci-growth`, `fibonacci-fence`, `fibonacci-heap`, `ternary-fib`, `spline-spectral`, `deadband-rs`, `spectral-graph-v2`, `fibonacci-growth-v2`, `lau-fibonacci-growth`).

## How it renders

- **TOP** — the cellular graph: rooms as nodes, edges as algorithms
- **FRONT** — the Z_in/Z_out dual databases and JEPA surprise readings
- **SIDE** — the GC cycle and vibe dynamics over time

## Example output

```json
{ "address": "pattern.z_in.name", "kind": "string", "value": "Z_in" },
{ "address": "pattern.z_in.embed[0]", "kind": "float", "value": 0.0 }
```
