# Adding a bridge — the porting template

Every bridge in this repo is the same shape: **source reader → cell writer**. If you have a pre-Quilt SuperInstance system (or a repo family) that isn't ported yet, this is the template it follows. The pattern is deliberately framework-free — each bridge is a single, self-contained, readable Python script.

## The pattern in one line

`python3 <system>_to_quilt.py --out <dir>` → `<system>.qzt` — read the source, map its parts to cells, emit the cell graph.

## Step 1 — Read

Start from the source system's real data model. Three tiers, best first:

1. **Real schema** — if the repo has a clean data model (like `vessel-agent-system`'s state or `chart-room`'s four panels), read it directly.
2. **Family inventory** — for family bridges (e.g. `agent-*`: 81 repos), enumerate the cohort and map each repo to a cell region.
3. **Faithful synthetic model** — where no live API exists yet, ship a `synth_*` generator that produces the same shape, clearly marked as synthetic (every bridge in this repo does this today).

## Step 2 — Map

Every meaningful part of the source becomes a **cell** with a stable dotted path. Use the tiny shared helper so every cell carries the same shape:

```python
def cell(path: str, kind: str, value: Any, depends_on: list[str] | None = None) -> dict:
    return {"path": path, "kind": kind, "value": value, **({"depends_on": depends_on} if depends_on else {})}
```

Follow the **region conventions** so any two bridges speak the same dialect:

| Region prefix | Meaning |
|---|---|
| `<system>.*`, `truth.*` | present state of the system |
| `env.*` | environment |
| `bathy.*` | spatial / TOP-plane cells |
| `nav.*`, `eng.*`, `tactical.*`, `sonar.*` | panel regions |
| `soul.*` | persistent identity cells |
| `timeline.*` | temporal / SIDE-plane samples |

## Step 3 — Emit (and satisfy the 3-views contract)

Serialize the graph as a `.qzt` file: plain JSON with `format`, `name`, `description`, `source`, `tags`, `cells` (and `edges` where links exist). **The 3-views contract is the hard requirement:** one `.qzt` file must render correctly in all three views without modification —

- **TOP** (spatial) — emit position/spatial cells (bathymetry, rooms, topology)
- **FRONT** (signals) — emit present-state signal cells (panels, sensor readings)
- **SIDE** (time) — emit temporal cells (timelines, deadlines, sampled history)

A bridge that only produces coordinates, or only instantaneous state, is incomplete. The original seven were the first to satisfy this; every new bridge must too.

## CLI contract

Match the existing bridges so the discovery tooling can call any of them uniformly:

```python
import argparse
p = argparse.ArgumentParser(description="<system> → Quilt bridge")
p.add_argument("--out", default="/tmp/<system>-quilt.json", help="Output .qzt path")
p.add_argument("--duration-min", type=float, default=30, help="Duration in minutes")
args = p.parse_args()
out = args.out if args.out.endswith(".qzt") else args.out + ".qzt"
```

`--duration-min` drives the SIDE-view temporal cells; systems without a time axis can default it.

## Checklist before committing

- [ ] Script runs: `python3 <system>_to_quilt.py --out /tmp/check.qzt`
- [ ] Emitted file loads in 3-View Studio and renders in **all three** views
- [ ] Cell paths use the region conventions; no invented dialects
- [ ] Synthetic data is clearly marked as synthetic
- [ ] Added to [the bridge catalog](bridge-catalog.md) with real cell count (read it from the emitted `stats`)
- [ ] One page in `docs/bridges/` following the per-bridge template (source repo, what it is, what the cells mean, cell count, example output)

Then port the next hull. The grid is waiting for it.
