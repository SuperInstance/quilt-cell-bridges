# Bridge: chart-room → Quilt

| | |
|---|---|
| **Script** | `chart_room_to_quilt.py` |
| **Source repo** | [SuperInstance/chart-room](https://github.com/SuperInstance/chart-room) |
| **Target** | `chart-room.qzt` — **144 cells** |
| **CLI** | `python3 chart_room_to_quilt.py --out <dir> --duration-min 30` |

## What the source is

"Four panels. Four perspectives. One truth." — chart-room is literally a 3-views architecture in 1995-era Python. Four panels (nav / engineering / tactical / sonar) all derive from a single shared truth state. If any bridge was already Quilt before Quilt, it's this one.

## What the cells mean

| Region | Meaning | Example cells |
|---|---|---|
| `truth.*` | the single source of truth | `truth.now`, `truth.source`, `truth.position` |
| `nav.*` | navigation panel | `nav.lat`, `nav.lon`, `nav.cog_deg`, `nav.heading_deg`, `nav.sog_knots` |
| `eng.*` | engineering panel | `eng.rpm`, `eng.fuel_pct`, `eng.oil_temp_c` |
| `tactical.*` | tactical panel | `tactical.threat_level`, `tactical.alert_count` |
| `sonar.*` | sonar panel | `sonar.fish_density`, `sonar.depth_to_fish_m` |
| `timeline.*` | one track per panel | 4 timeline tracks |

The bridge reads everything from `truth.now` — exactly like the source system: one truth cell, four panel regions derived from it. No cell may disagree with the truth.

## How it renders

- **TOP** — the navigation panel (spatial)
- **FRONT** — the engineering panel (signals)
- **SIDE** — tactical timeline + sonar sweep over time (temporal tracks)

## Example output

```json
{ "path": "truth.now",        "kind": "value", "value": "2026-08-20T22:00:00Z" },
{ "path": "nav.sog_knots",    "kind": "value", "value": 6.5 },
{ "path": "tactical.threat_level", "kind": "value", "value": "green" }
```
