# Bridge: hermes-home → Quilt

| | |
|---|---|
| **Script** | `hermes_home_to_quilt.py` |
| **Source repo** | [SuperInstance/hermes-home](https://github.com/SuperInstance/hermes-home) |
| **Target** | `hermes-home.qzt` — **83 cells** |
| **CLI** | `python3 hermes_home_to_quilt.py --out <dir>` |

## What the source is

Hermes's **runtime home** — "SOUL, agents, CNS monitors, cron bridges. The nervous system's identity." Hermes is a first-person agent; in Quilt terms that means Hermes *is* a sheet of cells: SOUL as persistent cells, agents as sub-sheets, CNS monitors as signal cells, cron bridges as temporal cells.

## What the cells mean

| Region | Meaning | Example cells |
|---|---|---|
| `soul.*` | persistent identity (immutable) | `soul.name` ("Hermes"), `soul.role` ("messenger"), `soul.domicile` ("the-bridge-of-the-SS-Lucineer"), `soul.born`, `soul.essence`, `soul.signature` |
| `agents.*` | one sub-sheet per agent | `agents.ensign.role`, `agents.ensign.specialty`, `agents.ensign.wake_state`, `agents.ensign.thought` |
| `cns.*` | CNS monitor signal cells | monitor readings |
| `cron.*` | cron bridges as temporal cells | scheduled bridge fires |
| `bridges.*` | bridge state | runtime bridge cells |

Breakdown from the bridge's own run output: **6 SOUL cells, 4 agent sub-sheets, 6 CNS monitors, 4 cron bridges, 3 runtime bridges** = 83 cells.

## How it renders

- **TOP** — the runtime's layout: home, agents, monitors
- **FRONT** — the nervous-system dashboard: agent battery, memory, wake state, monitor signals
- **SIDE** — cron schedule and agent activity over time

## Example output

```json
{ "path": "soul.name", "kind": "value", "value": "Hermes", "meta": { "category": "identity", "immutable": true } },
{ "path": "agents.ensign.role", "kind": "value", "value": "deck officer" },
{ "path": "agents.cook.thought", "kind": "value", "value": "Salt and time are the same ingredient." }
```
