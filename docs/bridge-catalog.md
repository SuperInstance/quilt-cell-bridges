# Bridge Catalog — all 50 bridges

Every bridge in this repo is `source reader → cell writer`: it reads a SuperInstance system (or a whole repo family) and emits a `.qzt` cell graph for 3-View Studio. Grouped by family. Cell counts are the bridge's own `stats.total_cells` where the script declares them.

**Pattern in one line:** each bridge is a single self-contained script — `python3 <bridge>.py --out <dir>` → `<name>.qzt`.

---

## The original seven (fleet core)

| Bridge | Source → target | What it does |
|---|---|---|
| `vessel_to_quilt.py` | [vessel-agent-system](https://github.com/SuperInstance/vessel-agent-system) → 188 cells | Ports F/V EILEEN's digital twin: vessel state, depth, GPS, course, holds, crew, bathymetry — TOP chart, FRONT dashboard, SIDE event timeline |
| `chart_room_to_quilt.py` | [chart-room](https://github.com/SuperInstance/chart-room) → 144 cells | Four panels, one truth: nav / engineering / tactical / sonar regions all derived from a single TruthCell |
| `slackwater_tminus_to_quilt.py` | [slackwater-tminus](https://github.com/SuperInstance/slackwater-tminus) → 54 cells | Time-shaped coordination: DeadlineCell, CronCell, BPMSyncCell, SwarmAnchorCell, ConfirmCell as temporal cells |
| `hermes_home_to_quilt.py` | [hermes-home](https://github.com/SuperInstance/hermes-home) → 83 cells | Hermes's runtime: SOUL identity cells, agent sub-sheets, CNS monitor signal cells, cron bridge temporal cells |
| `spatial_registry_to_quilt.py` | [spatial-registry](https://github.com/SuperInstance/spatial-registry) → 762 cells | 4 worlds, 33 rooms, 6 cross-world portals as a spatial cell graph |
| `grand_pattern_to_quilt.py` | [grand-pattern-rs](https://github.com/SuperInstance/grand-pattern-rs) → 412 cells | Fibonacci dual-direction architecture (12 ports) as a Quilt sheet |
| `spline_spectral_to_quilt.py` | [spline-spectral](https://github.com/SuperInstance/spline-spectral) → 299 cells | B-splines as spectral objects |

## vessel family

| Bridge | Source → target | What it does |
|---|---|---|
| `vessel_runtime_family_to_quilt.py` | vessel runtime family (7 repos) → 8 cells / 42 edges | The body of the cell: hardware abstraction, bytecode VM, N-body sim, maritime networking |

## agent family

| Bridge | Source → target | What it does |
|---|---|---|
| `agent_family_to_quilt.py` | `agent-*` family (81 repos) → cells | The whole agent cohort as one Quilt sheet |
| `agent_cognition_family_to_quilt.py` | agent cognition family → cells | Memory, cognition, and reasoning subsystems of the agent family |
| `superinstance_agent_to_quilt.py` | superinstance-agent → cells | The SuperInstance agent itself as a cell graph |

## cocapn family

| Bridge | Source → target | What it does |
|---|---|---|
| `cocapn_family_to_quilt.py` | `cocapn-*` family (77 repos) → cells | The cocapn cohort as a Quilt sheet |
| `cocapn_nexus_to_quilt.py` | cocapn-nexus → 29,361-B qzt | The nexus gateway as cells |

## collective, character & context

| Bridge | Source → target | What it does |
|---|---|---|
| `collective_unconscious_to_quilt.py` | collective-unconscious → 63,097-B qzt | Shared cognition substrate as cells |
| `collective_context_to_quilt.py` | collective + context family → 48,547-B qzt | Context carriers and collective state as cells |
| `character_family_to_quilt.py` | character family → 19,982-B qzt | Character definitions as cells |

## conservation, constraint & synapse

| Bridge | Source → target | What it does |
|---|---|---|
| `conservation_family_to_quilt.py` | `conservation-*` family (60 repos) → cells | Conservation-law bearers as cells |
| `constraint_family_to_quilt.py` | `constraint-*` family (47 repos) → cells | Constraint engines as cells |
| `fleet_synapse_plato_family_to_quilt.py` | synapse + PLATO + sandbox family → 22,905-B qzt | The synapse/PLATO cohort as cells |

## wesley, othismos, ternary, provenance & colony

| Bridge | Source → target | What it does |
|---|---|---|
| `wesley_to_quilt.py` | wesley → cells | The ensign as a cell graph |
| `wesley_dmlog_imagination_to_quilt.py` | wesley-holodeck + dmlog + plato-dmn-ecm → 74,101-B qzt | The imagination substrate as cells |
| `othismos_reef_to_quilt.py` | othismos-reef → cells | The knowledge-graph reef as a Quilt sheet |
| `ternary_fleet_packing_to_quilt.py` | ternary-fleet-packing → cells | Ternary encodings as cells |
| `ternary_spreadsheet_to_quilt.py` | ternary-spreadsheet → cells | Ternary spreadsheets in .qzt form |
| `provenance_log_to_quilt.py` | provenance-log → cells | Time as a hash-chained cell |
| `colony_cell_to_quilt.py` | colony-cell → cells | Filesystem sandbox as cells |

## Quilt porting Quilt

| Bridge | Source → target | What it does |
|---|---|---|
| `quilt_ai_to_quilt.py` | `@quilt/ai` + `@quilt/rag` → cells | 4 providers × 8 cell kinds as a bridge (RAG pipeline folded in) |
| `quilt_ecosystem_to_quilt.py` | the Quilt ecosystem → cells | The whole ecosystem as one sheet |
| `quilt_flow_to_quilt.py` | quilt-flow → cells | The flow package as cells |
| `quilt_mesh_to_quilt.py` | quilt-mesh → cells | The mesh package as cells |
| `substrate_modules_to_quilt.py` | substrate modules → cells | Quilt's substrate modules as cells |
| `abstraction_levels_to_quilt.py` | the 8 abstraction levels → 9 cells / 56 edges | The fractal claim: same cell model at every grain, cell → system, with a `fractal_meta` cell |

## spreadsheet & data heritage

| Bridge | Source → target | What it does |
|---|---|---|
| `spreadsheet_engine_to_quilt.py` | spreadsheet-engine → cells | The spreadsheet engine as cells |
| `spectral_spreadsheet_to_quilt.py` | spectral-spreadsheet → cells | Spectral spreadsheets as cells |
| `crdt_to_quilt.py` | CRDT family → cells | CRDTs as cell graphs |
| `federated_artifact_to_quilt.py` | federated-artifact-store → cells | Federated artifact store as cells |
| `cell_rewind_to_quilt.py` | cell-rewind (Time-Travel DAW) → cells | The time-travel DAW as a sheet with connections |
| `temporal_heartbeat_to_quilt.py` | temporal-heartbeat → cells | Heartbeat cadence as temporal cells |

## spatial & signal

| Bridge | Source → target | What it does |
|---|---|---|
| `sonar_vision_to_quilt.py` | sonar-vision → cells | Sonar vision project as cells |

## infra & services

| Bridge | Source → target | What it does |
|---|---|---|
| `cudaclaw_to_quilt.py` | CudaClaw → cells | Repository structure as cells |
| `forgemaster_to_quilt.py` | forgemaster → 33,308-B qzt | The forgemaster as cells |
| `lever_runner_to_quilt.py` | lever-runner → 38,847-B qzt | The lever-runner as cells |
| `vaas_to_quilt.py` | VaaS → 33,271-B qzt | Vessel-as-a-service as cells |
| `elephant_to_quilt.py` | elephant → cells | The elephant repo as cells |
| `penrose_family_to_quilt.py` | Penrose family (12 repos) → cells | The Penrose cohort as cells |
| `marketplace_constellation_to_quilt.py` | marketplace + constellation repos → 14,870-B qzt | Marketplace/constellation as cells |
| `mud_family_to_quilt.py` | MUD family → 45,202-B qzt | The MUD cohort as cells |
| `nexus_fleet_family_to_quilt.py` | nexus fleet family → 12,764-B qzt | The nexus fleet as cells |
| `llm_runtime_family_to_quilt.py` | LLM runtime family → 46,743-B qzt | LLM runtimes as cells |
| `protocols_to_quilt.py` | protocols family → 82,381-B qzt | Protocol surfaces as cells |

---

## Quick reference

- **50 bridge scripts**, 17 with `.qzt` outputs checked in.
- **One pattern:** read source → map to cells → emit `.qzt` (4D: 3D space + time).
- **One contract:** every `.qzt` renders in all three views — TOP (spatial/openCPN), FRONT (signals/TimeZero), SIDE (time/DAW). See [architecture.md](architecture.md).
- **Missing a family?** If your system's repo (or family) isn't listed, it's a future bridge — the pattern is designed for porting; `adding-a-bridge` follows the same read → map → emit shape as every script here.
