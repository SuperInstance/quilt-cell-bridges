# quilt-cell-bridges

**Port the existing SuperInstance ecosystem to Quilt cells.**

The SuperInstance org has 300+ GitHub repos. Many of them were built
long before Quilt existed — but they were already expressing the cell
model in different forms. A vessel-agent-system's digital twin is a
graph of cells. A chart-room's four panels are four views of the same
cells. A slackwater-tminus's coordination primitives are temporal cells.

This repo contains the **bridges** that port those systems to Quilt
sheets, and a **discovery page** that lets users pick a system and see
it as cells.

## Bridges (live)

| Source repo | What it does | Quilt bridge | Cells |
|---|---|---|---|
| [vessel-agent-system](https://github.com/SuperInstance/vessel-agent-system) | F/V EILEEN's digital twin | `vessel_to_quilt.py` | 188 |
| [chart-room](https://github.com/SuperInstance/chart-room) | Four panels, one truth | `chart_room_to_quilt.py` | 144 |
| [slackwater-tminus](https://github.com/SuperInstance/slackwater-tminus) | Temporal coordination | `slackwater_tminus_to_quilt.py` | 54 |
| [hermes-home](https://github.com/SuperInstance/hermes-home) | Hermes's runtime home | `hermes_home_to_quilt.py` | 83 |

## Usage

```bash
# Generate a .qzt file for any bridge
python3 vessel_to_quilt.py --out /tmp/eileen --duration-min 30

# Open the discovery page
# https://superinstance.dev/cell-bridges.html

# Or load directly into 3-View Studio
# https://superinstance.dev/three-view-studio.html?load=vessel
```

## The 3-views model

Each bridge is a 4D cell graph (3D space + time). The 3-View Studio
renders it three ways:

- **TOP view** (spatial) — vessel-agent-system's bathymetry chart, openCPN-style
- **FRONT view** (signals) — chart-room's engineering panel, TimeZero-style
- **SIDE view** (time) — slackwater-tminus's coordination timeline, DAW-style

The same data, three openers, one file.

## Coming next

- `wesley` (the ensign as a cell)
- `othismos-reef` (knowledge graph as cells)
- `ternary-fleet-packing` (ternary encodings as cells)
- `provenance-log` (time as a hash-chained cell)
- `colony-cell` (filesystem sandbox as cells)
- `quilt-ai` (4 providers × 8 cell kinds as a bridge)
- `quilt-rag` (the RAG pipeline as a cell chain)

See [superinstance.dev/cell-bridges.html](https://superinstance.dev/cell-bridges.html) for the live discovery surface.

## License

MIT
