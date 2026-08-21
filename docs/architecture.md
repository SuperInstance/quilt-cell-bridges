# Architecture — quilt-cell-bridges

> How a pre-Quilt system becomes a `.qzt` cell graph, and how that one file opens three ways.

---

## 1. The bridge pattern

Every bridge in this repo is the same shape: **source reader → cell writer**.

```
┌────────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  Source system     │     │  Bridge script   │     │  Target: .qzt file      │
│  (repo / family)   │ ──► │  *_to_quilt.py   │ ──► │  4D cell graph          │
│  data model        │     │  read → map →    │     │  cells + edges + stats  │
└────────────────────┘     │  emit            │     └────────────┬────────────┘
                           └──────────────────┘                  │
                                                                 ▼
                                            ┌─────────────────────────────────┐
                                            │  3-View Studio: TOP / FRONT /   │
                                            │  SIDE — same data, three openers │
                                            └─────────────────────────────────┘
```

1. **Read.** The source system's data model — real where a repo has a clean schema (`vessel-agent-system`'s state, `chart-room`'s four panels), a family inventory where the bridge covers a repo cohort (`agent-*`: 81 repos, `cocapn-*`: 77), or a faithful synthetic model where no live API exists yet (all bridges fall back to `synth_*` generators, clearly marked).
2. **Map.** Every meaningful part of the source becomes a **cell** with a stable, dotted path — `vessel.rpm`, `truth.position`, `soul.name`, `timeline.12`. Cells are grouped into path-prefixed **regions** that mirror the source's own anatomy (see §4).
3. **Emit.** The graph is serialized as a `.qzt` file — plain JSON, self-describing, portable. No services, no build step. `python3 <bridge>.py --out <dir>` and the file exists.

The codebase enforces this with tiny shared helpers (`cell(path, kind, value, depends_on)`) rather than a framework — each bridge stays a self-contained, readable story about one source system.

## 2. The .qzt format

Every `.qzt` file is JSON with the same top-level shape:

| Key | Meaning |
|---|---|
| `version` | format version (`"1.0"`) |
| `kind` | always `"quilt-zip-target"` |
| `name` | e.g. `"vessel-runtime-family-to-quilt"` |
| `description` | one-line bridge story |
| `cells` | the cell graph's nodes |
| `edges` | the graph's links (kind, weight, from → to) |
| `external_refs` | pointers back to the source material (papers, repos, files) |
| `stats` | `total_cells`, `total_edges`, plus bridge-specific counts |
| `tags` | searchable labels |

### Cell anatomy

A cell is not a value — it's a live, addressable capability. Bridge cells carry the full anatomy the Quilt model expects:

| Field | Meaning |
|---|---|
| `id` / `path` | stable address (`vessel.rpm`, `level_3`) |
| `kind` | cell kind — value, formula, sensor, program, … |
| `form` | display name (`{"name": "L3_Harness"}`) |
| `description` | what this cell is |
| `primitives` | the cell ops it supports (Spawn, Observe, Mutate, Send, Receive, Move, Resize, Kill) |
| `z_in` / `z_out` | input/output contracts |
| `jepa` | predict / observe pair (surprise detection) |
| `double_entry` | conservation bookkeeping (gamma / eta) |
| `vibe` | position / velocity / acceleration in the graph |
| `gc` | lifecycle phase |
| `murmur` | gossip neighbors |
| `graph` | children / parents |
| `openers` | methods callers can invoke |
| `substrate` | address, room, protocol, form, state |
| `tags` | labels |

A `QuiltCell`-class variant (used by `cell_rewind_to_quilt.py` et al.) is equivalent: `id`, `type`, `name`, `properties`, `connections`. The shape differs per bridge era; the contract — stable address + kind + links — is constant.

## 3. The 3-views rendering contract

Each bridge emits a **4D cell graph**: 3D space plus time. 3-View Studio renders it three ways, and the views are not decorations — each corresponds to what the source system actually was:

| View | Axis | What it renders | Instrument |
|---|---|---|---|
| **TOP** (spatial) | x/y | positions, bathymetry, rooms, worlds, topology | openCPN-style chart — `vessel`'s bathy grid, `spatial-registry`'s 33 rooms |
| **FRONT** (signals) | value | live state, panels, sensor readings, dashboards | TimeZero-style engineering console — `chart-room`'s four panels |
| **SIDE** (time) | t | timelines, coordination, history, deadlines | DAW-style timeline — `slackwater-tminus`'s coordination, `vessel`'s timeline.* samples |

**The rule:** one `.qzt` file must render correctly in all three views without modification. A bridge that only produces coordinates in the TOP plane, or only instantaneous state for FRONT, is incomplete — it must also emit the temporal cells (SIDE) and the spatial cells (TOP). The original README's seven bridges were the first to satisfy this; the family bridges follow the same contract.

## 4. Three scale views: cell, bridge, ecosystem

The abstraction-levels bridge (`abstraction_levels_to_quilt.py`) frames the deeper claim: **the same cell model holds at every scale — what changes is the grain.** Three scales matter here:

- **Cell view** — one cell is a live, addressable capability: a number, a sensor, a room, a panel, a deadline, a person. The 8 primitives, 7 substrates, 9 dials, conservation law, and watch oscillation apply at every level.
- **Bridge view** — one bridge is a **sheet**: a graph of cells (β₁ topology) with edges (murmur, depends_on, cites) connecting them. The bridge's 3-views contract is this sheet's interface.
- **Ecosystem view** — the 50 bridges together are a **fleet-to-ecosystem mapping**: 300+ repos, each ported or port-ready, each knowing its place in the grid. The collection is the migration story; the discovery page ([cell-bridges.html](https://superinstance.dev/cell-bridges.html)) is its chart table.

The full 8-level fractal — cell → sheet → agent → harness → fleet → ecosystem → infrastructure → system — is itself bridged in `abstraction_levels_to_quilt.py`, with a `fractal_meta` cell asserting the claim directly in the graph.

## 5. Region conventions

Bridges map source anatomy onto consistent path regions, so any two bridges speak the same dialect:

| Region prefix | Meaning | Example |
|---|---|---|
| `vessel.*`, `truth.*` | present state of the system | `vessel.sog_knots`, `truth.position` |
| `env.*` | environment | `env.wind_speed_kt`, `env.depth_m` |
| `bathy.*` | spatial / TOP-plane cells | bathymetry grid |
| `nav.*`, `eng.*`, `tactical.*`, `sonar.*` | panel regions (chart-room's four) | `eng.rpm`, `tactical.threat_level` |
| `soul.*` | persistent identity cells (hermes) | `soul.name`, `soul.role` |
| `timeline.*` | temporal / SIDE-plane samples | `timeline.12.time` |
| `level_N` | abstraction-level cells (0–7) | `level_3` = harness |

A reader who knows the conventions can open any `.qzt` in the repo and find the state, the space, and the time within seconds.
