# Bridge: vessel → Quilt

| | |
|---|---|
| **Script** | `vessel_to_quilt.py` |
| **Source repo** | [SuperInstance/vessel-agent-system](https://github.com/SuperInstance/vessel-agent-system) |
| **Target** | `vessel.qzt` — **188 cells** |
| **CLI** | `python3 vessel_to_quilt.py --out <dir> --duration-min 30` |

## What the source is

F/V EILEEN's **digital twin** — the vessel-agent-system README's own words. It has a clean data model: vessel state, depth, GPS, course, speed, fish holds, crew. The twin is the fleet's "top view" of cellular architecture: state, environment, and history, all describing one hull.

## What the cells mean

The bridge maps the twin's data model onto Quilt cell regions:

| Region | Meaning | Example cells |
|---|---|---|
| `vessel.*` | present state of the hull | `vessel.lat`, `vessel.lon`, `vessel.sog_knots`, `vessel.cog_deg`, `vessel.heading_deg`, `vessel.autopilot`, `vessel.rpm` |
| `env.*` | the water around it | `env.depth_m`, `env.wind_speed_kt` |
| `bathy.*` | the seafloor grid — the TOP-view plane | bathymetry cells |
| `crew.*` / holds | who's aboard, what's in the holds | crew cells, hold state |
| `timeline.*` | sampled history over the run — the SIDE-view plane | `timeline.N.time` samples |

In production the source state would come from the AELMA twin; the bridge ships a clearly-marked `synth_vessel_state(t)` generator that produces the same shape (Southeast Alaska, Thomas Bay area) so the pipeline is runnable today.

## How it renders

- **TOP** — spatial chart of the vessel plus the bathy grid (openCPN-style)
- **FRONT** — dashboard of present-state signals (TimeZero-style)
- **SIDE** — timeline of vessel events over `--duration-min` (DAW-style)

## Example output

```json
{ "path": "vessel.sog_knots", "kind": "value", "value": 6.5 },
{ "path": "env.depth_m",      "kind": "value", "value": 45.0 },
{ "path": "timeline.12.time", "kind": "value", "value": "..." }
```

Load it: `https://superinstance.dev/three-view-studio.html?load=vessel`
