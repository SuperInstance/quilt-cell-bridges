# Bridge: slackwater-tminus → Quilt

| | |
|---|---|
| **Script** | `slackwater_tminus_to_quilt.py` |
| **Source repo** | [SuperInstance/slackwater-tminus](https://github.com/SuperInstance/slackwater-tminus) |
| **Target** | `slackwater-tminus.qzt` — **54 cells** |
| **CLI** | `python3 slackwater_tminus_to_quilt.py --out <dir> --duration-min 60` |

## What the source is

**Time-shaped coordination primitives** for swarm-anchor: predict-and-confirm, deadlines, BPM clocks, cron. It is a temporal coordination system — a natural fit for the Quilt SIDE view (the timeline plane).

## What the cells mean

| Region | Meaning | Example cells |
|---|---|---|
| `clock.*` | the master clock | `clock.bpm`, `clock.period_s`, `clock.start`, `clock.beats` (one beat cell per beat in the duration, 4/4 time) |
| `deadline.*` | T-minus countdowns | `deadline.deploy_window.name`, `deadline.deploy_window.at_s`, `deadline.deploy_window.owner`, `deadline.deploy_window.remaining_s` |
| `cron.*` | repeating triggers | cron cells firing at intervals |
| `swarm.*` | shared swarm state | `swarm.*` anchor cells |
| `confirm.*` | predict-and-confirm | confirm cells that a deadline was met |
| `tracks.*` | agent tracks on the timeline | per-agent timeline tracks |

Each cell type is a real coordination primitive from the source protocol: a `DeadlineCell` emits a signal at time T, a `CronCell` at intervals, a `BPMSyncCell` synchronizes cells to a tempo, a `SwarmAnchorCell` holds shared state, a `ConfirmCell` confirms a deadline was met.

## How it renders

- **TOP** — swarm positions over the run
- **FRONT** — live clock / deadline dashboard
- **SIDE** — the coordination timeline: beats, deadlines, cron fires, agent tracks (DAW-style — this is the bridge's home view)

## Example output

```json
{ "path": "clock.bpm", "kind": "value", "value": 60 },
{ "path": "deadline.deploy_window.at_s", "kind": "value", "value": 120.0 },
{ "path": "clock.beats", "kind": "value", "value": [ { "time": 0.0, "beat": 0, "phase": 0, "measure": 0 } ] }
```
