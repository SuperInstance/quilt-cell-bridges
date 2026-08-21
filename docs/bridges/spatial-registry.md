# Bridge: spatial-registry → Quilt

| | |
|---|---|
| **Script** | `spatial_registry_to_quilt.py` |
| **Source repo** | [SuperInstance/spatial-registry](https://github.com/SuperInstance/spatial-registry) (vendored in `SuperInstance/terrain`) |
| **Target** | `spatial-registry.qzt` — **762 cells** |
| **CLI** | `python3 spatial_registry_to_quilt.py --out <dir>` |

## What the source is

A TypeScript spatial registry defining **World** (collection of rooms + coordinate frames), **Room** (the atomic unit of space: id, name, coordinates, exits, tags, metadata), **Portal** (a connection between rooms — walk | warp | transition | teleport), **CoordinateFrame** (maps between coordinate systems), and **MUDWorld** (the MUD schema: rooms, items, actors, verbs, initialState). The registry holds **4 worlds, 33 rooms, and 6 cross-world portals**.

## What the cells mean

Each source entity becomes a cell whose kind names its role:

| Cell kind | Source entity | Example |
|---|---|---|
| `world` | a World | `world.platos-shell.name`, `world.platos-shell.frame`, `world.platos-shell.room_count` |
| `room` | a Room (atomic unit of space) | room cells with coordinates + exits |
| `portal` | a Portal (walk / warp / transition / teleport) | 6 cross-world portal cells |
| `frame` | a CoordinateFrame | coordinate mapping cells |

The Quilt address encodes the registry's own namespacing: world ID (`platos-shell` | `officers-quarters` | `the-tap` | `scummvm-arcade`) then `room.<worldId>.<roomId>.*`, with the room's coordinates carried in the cell.

## How it renders

- **TOP** — the spatial map of all 33 rooms and 6 portals across 4 worlds
- **FRONT** — present-state dashboard: active agents, recent activity
- **SIDE** — timeline of room visits / agent movements

Also viewable at `https://superinstance.dev/rooms-quilt.html` for the spatial view.

## Example output

```json
{ "path": "world.platos-shell.name", "kind": "value", "value": "Plato's Shell" },
{ "path": "world.the-tap.frame", "kind": "value", "value": "tap-local" }
```
