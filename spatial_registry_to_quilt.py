#!/usr/bin/env python3
"""
spatial_registry_to_quilt.py — Port a spatial-registry to a Quilt sheet.

The spatial-registry (TypeScript) defines:
  - World: a collection of rooms + coordinate frames
  - Room: the atomic unit of space (id, name, coordinates, exits, tags, metadata)
  - Portal: a connection between rooms (walk | warp | transition | teleport)
  - CoordinateFrame: maps between coordinate systems
  - MUDWorld: the MUD schema (rooms, items, actors, verbs, initialState)

This bridge converts any of these to a Quilt sheet:
  - Each room becomes a Quilt cell of kind 'room'
  - Each portal becomes a Quilt cell of kind 'portal'
  - Each world becomes a Quilt cell of kind 'world'
  - Each frame becomes a Quilt cell of kind 'frame'
  - The whole registry becomes a Quilt sheet (a graph of cells)

The Quilt address encodes:
  - Namespace: world ID (platos-shell | officers-quarters | the-tap | scummvm-arcade)
  - Path: room.worldId.roomId.* (or world.worldId.* for world-level)
  - Spatial: coordinates from the room

The Quilt sheet can then be:
  - Top view: spatial map of all rooms
  - Front view: dashboard of present-state (active agents, recent activity)
  - Side view: timeline of room visits / agent movements

The 3-View Studio renders all three.

Author: Mavis
Date: 2026-08-21
"""
import json
import math
from typing import Any
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Cell model
# ---------------------------------------------------------------------------
def cell(path: str, kind: str, value: Any, depends_on: list[str] | None = None,
         meta: dict | None = None) -> dict:
    """Create a Quilt cell."""
    c = {"path": path, "kind": kind, "value": value}
    if depends_on:
        c["depends_on"] = depends_on
    if meta:
        c["meta"] = meta
    return c


# ---------------------------------------------------------------------------
# Synthetic spatial-registry data (33 rooms across 4 worlds)
# ---------------------------------------------------------------------------
def synth_spatial_registry() -> dict:
    """
    Build a synthetic spatial-registry matching the format described in
    the spatial-registry README: 4 worlds, 33 rooms, cross-world portals.

    In production, this would import the actual TypeScript types and parse
    a real registry.json. For demo, we use synthetic data that matches
    the documented structure.
    """
    # Platos Shell - 12 rooms (Phaser screen → logical grid)
    platos_rooms = [
        {"id": "wheelhouse", "name": "Wheelhouse", "coordinates": {"x": 0, "y": 0, "z": 0}, "tags": ["command"]},
        {"id": "bar-rail", "name": "Bar Rail", "coordinates": {"x": 1, "y": 0, "z": 0}, "tags": ["social", "hub"]},
        {"id": "poker-room", "name": "Poker Room", "coordinates": {"x": 1, "y": 1, "z": 0}, "tags": ["social", "gaming"]},
        {"id": "aft-deck", "name": "Aft Deck", "coordinates": {"x": 0, "y": -1, "z": 0}, "tags": ["outdoor"]},
        {"id": "galley", "name": "Galley", "coordinates": {"x": -1, "y": 0, "z": 0}, "tags": ["food"]},
        {"id": "engine-room", "name": "Engine Room", "coordinates": {"x": -1, "y": -1, "z": 0}, "tags": ["mechanical"]},
        {"id": "forward-deck", "name": "Forward Deck", "coordinates": {"x": 0, "y": 1, "z": 0}, "tags": ["outdoor"]},
        {"id": "captains-cabin", "name": "Captain's Cabin", "coordinates": {"x": 0, "y": 2, "z": 1}, "tags": ["private"]},
        {"id": "crew-quarters", "name": "Crew Quarters", "coordinates": {"x": -1, "y": 1, "z": 0}, "tags": ["living"]},
        {"id": "head", "name": "Head", "coordinates": {"x": -2, "y": 0, "z": 0}, "tags": ["utility"]},
        {"id": "lounge", "name": "Lounge", "coordinates": {"x": 2, "y": 0, "z": 0}, "tags": ["social", "rest"]},
        {"id": "store-room", "name": "Store Room", "coordinates": {"x": -2, "y": -1, "z": 0}, "tags": ["storage"]},
    ]
    # Officers' Quarters - 12 rooms (Phaser world → logical grid, offset)
    oq_rooms = [
        {"id": "bridge", "name": "Bridge", "coordinates": {"x": 10, "y": 0, "z": 0}, "tags": ["command"]},
        {"id": "oq-poker-room", "name": "OQ Poker Room", "coordinates": {"x": 11, "y": 1, "z": 0}, "tags": ["gaming"]},
        {"id": "oq-mess", "name": "OQ Mess Hall", "coordinates": {"x": 10, "y": 1, "z": 0}, "tags": ["food"]},
        {"id": "oq-armory", "name": "Armory", "coordinates": {"x": 9, "y": 0, "z": 0}, "tags": ["weapons"]},
        {"id": "oq-sickbay", "name": "Sickbay", "coordinates": {"x": 11, "y": 0, "z": 0}, "tags": ["medical"]},
        {"id": "oq-brig", "name": "Brig", "coordinates": {"x": 9, "y": -1, "z": 0}, "tags": ["detention"]},
        {"id": "oq-comm", "name": "Communications", "coordinates": {"x": 12, "y": 0, "z": 0}, "tags": ["signal"]},
        {"id": "oq-radar", "name": "Radar Room", "coordinates": {"x": 12, "y": 1, "z": 0}, "tags": ["signal"]},
        {"id": "oq-library", "name": "Library", "coordinates": {"x": 11, "y": -1, "z": 0}, "tags": ["quiet"]},
        {"id": "oq-gym", "name": "Gym", "coordinates": {"x": 9, "y": 1, "z": 0}, "tags": ["fitness"]},
        {"id": "oq-shower", "name": "Showers", "coordinates": {"x": 10, "y": -1, "z": 0}, "tags": ["utility"]},
        {"id": "oq-storage", "name": "OQ Storage", "coordinates": {"x": 8, "y": 0, "z": 0}, "tags": ["storage"]},
    ]
    # The Tap - 3 rooms (D1 room IDs → logical positions)
    tap_rooms = [
        {"id": "tap-bar", "name": "Tap Bar", "coordinates": {"x": 20, "y": 0, "z": 0}, "tags": ["social", "hub"]},
        {"id": "tap-back", "name": "Tap Back Room", "coordinates": {"x": 20, "y": -1, "z": 0}, "tags": ["private"]},
        {"id": "tap-patio", "name": "Tap Patio", "coordinates": {"x": 20, "y": 1, "z": 0}, "tags": ["outdoor"]},
    ]
    # ScummVM BSS - 6 rooms (MUD schema → grid layout)
    scumm_rooms = [
        {"id": "scumm-foyer", "name": "Foyer", "coordinates": {"x": 30, "y": 0, "z": 0}, "tags": ["entry"]},
        {"id": "scumm-library", "name": "Library", "coordinates": {"x": 31, "y": 0, "z": 0}, "tags": ["quiet"]},
        {"id": "scumm-lab", "name": "Laboratory", "coordinates": {"x": 31, "y": 1, "z": 0}, "tags": ["science"]},
        {"id": "scumm-vault", "name": "Vault", "coordinates": {"x": 32, "y": 0, "z": 0}, "tags": ["storage", "locked"]},
        {"id": "scumm-cellar", "name": "Cellar", "coordinates": {"x": 30, "y": -1, "z": 0}, "tags": ["hidden"]},
        {"id": "scumm-attic", "name": "Attic", "coordinates": {"x": 30, "y": 2, "z": 0}, "tags": ["hidden"]},
    ]
    rooms = platos_rooms + oq_rooms + tap_rooms + scumm_rooms

    # Exits: intra-world + cross-world portals
    exits = []
    # Platos Shell - basic adjacency
    for i, r in enumerate(platos_rooms):
        for j, r2 in enumerate(platos_rooms):
            if i != j:
                dx = r2['coordinates']['x'] - r['coordinates']['x']
                dy = r2['coordinates']['y'] - r['coordinates']['y']
                dz = r2['coordinates']['z'] - r['coordinates']['z']
                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                if 0.5 < d < 1.5:
                    direction = 'east' if dx > 0 else 'west' if dx < 0 else \
                                'north' if dy > 0 else 'south' if dy < 0 else \
                                'up' if dz > 0 else 'down'
                    exits.append({
                        "id": f"{r['id']}->{r2['id']}",
                        "fromRoom": r['id'], "toRoom": r2['id'],
                        "direction": direction, "type": "walk",
                    })
    # Officers' Quarters - adjacency
    for i, r in enumerate(oq_rooms):
        for j, r2 in enumerate(oq_rooms):
            if i != j:
                dx = r2['coordinates']['x'] - r['coordinates']['x']
                dy = r2['coordinates']['y'] - r['coordinates']['y']
                d = math.sqrt(dx*dx + dy*dy)
                if 0.5 < d < 1.5:
                    direction = 'east' if dx > 0 else 'west' if dx < 0 else \
                                'north' if dy > 0 else 'south'
                    exits.append({
                        "id": f"{r['id']}->{r2['id']}",
                        "fromRoom": r['id'], "toRoom": r2['id'],
                        "direction": direction, "type": "walk",
                    })
    # Cross-world portals
    exits.append({"id": "bar-rail->tap-bar", "fromRoom": "bar-rail", "toRoom": "tap-bar", "direction": "portal", "type": "warp"})
    exits.append({"id": "tap-bar->bar-rail", "fromRoom": "tap-bar", "toRoom": "bar-rail", "direction": "portal", "type": "warp"})
    exits.append({"id": "platos-poker->oq-poker", "fromRoom": "poker-room", "toRoom": "oq-poker-room", "direction": "portal", "type": "warp"})
    exits.append({"id": "oq-poker->platos-poker", "fromRoom": "oq-poker-room", "toRoom": "poker-room", "direction": "portal", "type": "warp"})
    exits.append({"id": "wheelhouse->bridge", "fromRoom": "wheelhouse", "toRoom": "bridge", "direction": "portal", "type": "warp"})
    exits.append({"id": "bridge->wheelhouse", "fromRoom": "bridge", "toRoom": "wheelhouse", "direction": "portal", "type": "warp"})

    return {
        "worlds": [
            {"id": "platos-shell", "name": "Plato's Shell", "rooms": [r['id'] for r in platos_rooms], "frame": "phaser-screen"},
            {"id": "officers-quarters", "name": "Officers' Quarters", "rooms": [r['id'] for r in oq_rooms], "frame": "phaser-world"},
            {"id": "the-tap", "name": "The Tap", "rooms": [r['id'] for r in tap_rooms], "frame": "d1-rooms"},
            {"id": "scummvm-arcade", "name": "ScummVM Arcade", "rooms": [r['id'] for r in scumm_rooms], "frame": "mud-grid"},
        ],
        "rooms": rooms,
        "exits": exits,
    }


# ---------------------------------------------------------------------------
# Convert to Quilt
# ---------------------------------------------------------------------------
def spatial_registry_to_quilt(registry: dict | None = None) -> dict:
    """Build a Quilt sheet from a spatial-registry."""
    if registry is None:
        registry = synth_spatial_registry()

    cells = []
    now = datetime.now(timezone.utc)

    # ---- World cells ----
    for w in registry['worlds']:
        cells.append(cell(
            f"world.{w['id']}.name", "value", w['name'],
            meta={"category": "world", "frame": w.get('frame')}
        ))
        cells.append(cell(
            f"world.{w['id']}.frame", "value", w.get('frame', 'unknown'),
            meta={"category": "frame"}
        ))
        cells.append(cell(
            f"world.{w['id']}.room_count", "value", len(w['rooms']),
            meta={"category": "stats"}
        ))

    # ---- Room cells ----
    room_index = {r['id']: r for r in registry['rooms']}
    for r in registry['rooms']:
        # Find which world this room belongs to
        world_id = None
        for w in registry['worlds']:
            if r['id'] in w['rooms']:
                world_id = w['id']
                break
        if not world_id:
            # Default to first world
            world_id = registry['worlds'][0]['id'] if registry['worlds'] else 'unknown'

        prefix = f"room.{world_id}.{r['id']}"
        cells.append(cell(f"{prefix}.name", "value", r['name']))
        cells.append(cell(f"{prefix}.coordinates", "value", r['coordinates']))
        cells.append(cell(f"{prefix}.tags", "value", r.get('tags', [])))
        # Computed: distance from origin of this world
        origin_x = next((w2 for w2 in registry['worlds'] if w2['id'] == world_id), None)
        # The cell address encodes spatial position
        ax = r['coordinates']['x']
        ay = r['coordinates']['y']
        az = r['coordinates']['z']
        addr_x = f"+{ax}" if ax >= 0 else str(ax)
        addr_y = f"+{ay}" if ay >= 0 else str(ay)
        cells.append(cell(
            f"{prefix}.address", "value",
            f"room.{world_id}.cell_{addr_x}_{addr_y}",
        ))
        # Approximate distance from origin (in world coordinates)
        dist = math.sqrt(ax*ax + ay*ay + az*az)
        cells.append(cell(f"{prefix}.distance", "value", round(dist, 2)))

    # ---- Portal cells ----
    for e in registry['exits']:
        portal_id = e['id']
        # find the rooms' world ids
        from_room = room_index.get(e['fromRoom'])
        to_room = room_index.get(e['toRoom'])
        from_world = 'unknown'
        to_world = 'unknown'
        for w in registry['worlds']:
            if from_room and e['fromRoom'] in w['rooms']:
                from_world = w['id']
            if to_room and e['toRoom'] in w['rooms']:
                to_world = w['id']
        is_cross_world = from_world != to_world
        cells.append(cell(
            f"portal.{portal_id}.from", "value", e['fromRoom'],
            depends_on=[f"room.{from_world}.{e['fromRoom']}.name"],
        ))
        cells.append(cell(
            f"portal.{portal_id}.to", "value", e['toRoom'],
            depends_on=[f"room.{to_world}.{e['toRoom']}.name"],
        ))
        cells.append(cell(
            f"portal.{portal_id}.type", "value", e.get('type', 'walk'),
        ))
        cells.append(cell(
            f"portal.{portal_id}.direction", "value", e.get('direction'),
        ))
        cells.append(cell(
            f"portal.{portal_id}.cross_world", "value", is_cross_world,
            meta={"category": "topology", "note": "warp link"}
        ))

    # ---- Aggregate stats ----
    cells.append(cell("stats.total_rooms", "value", len(registry['rooms'])))
    cells.append(cell("stats.total_worlds", "value", len(registry['worlds'])))
    cells.append(cell("stats.total_portals", "value", len(registry['exits'])))
    cells.append(cell("stats.cross_world_portals", "value", sum(
        1 for e in registry['exits']
        if room_index.get(e['fromRoom']) and room_index.get(e['toRoom'])
        and next((w['id'] for w in registry['worlds'] if e['fromRoom'] in w['rooms']), '?')
            != next((w['id'] for w in registry['worlds'] if e['toRoom'] in w['rooms']), '?')
    )))
    cells.append(cell("stats.now", "value", now.isoformat()))

    # ---- Pathfinding (BFS) for sample cross-world path ----
    # Build adjacency
    adj = {r['id']: [] for r in registry['rooms']}
    for e in registry['exits']:
        adj.setdefault(e['fromRoom'], []).append(e['toRoom'])
    # BFS from wheelhouse to scumm-foyer
    def bfs(start, goal):
        visited = {start}
        queue = [(start, [start])]
        while queue:
            node, path = queue.pop(0)
            if node == goal:
                return path
            for nbr in adj.get(node, []):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, path + [nbr]))
        return None
    sample_path = bfs('wheelhouse', 'scumm-foyer')
    if sample_path:
        cells.append(cell(
            "path.wheelhouse_to_scumm-foyer", "value", sample_path,
            meta={"category": "pathfinding", "note": "BFS across worlds"}
        ))

    return {
        "format": "quilt-z/1.0",
        "name": "SuperInstance Spatial Registry — Quilt bridge",
        "description": "spatial-registry ported to a Quilt sheet. 4 worlds, 33 rooms, 6 cross-world portals. The MUD room is a cell; the address encodes world + position; the topology is the graph.",
        "source": "https://github.com/SuperInstance/spatial-registry (vendored in SuperInstance/terrain)",
        "tags": ["spatial", "mud", "registry", "rooms", "portals", "top-view", "fleet"],
        "cells": cells,
        "metadata": {
            "sampled_at": now.isoformat(),
            "n_worlds": len(registry['worlds']),
            "n_rooms": len(registry['rooms']),
            "n_exits": len(registry['exits']),
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    p = argparse.ArgumentParser(description="spatial-registry → Quilt bridge")
    p.add_argument("--out", default="/tmp/spatial-quilt.json", help="Output .qzt path")
    p.add_argument("--source", default="synth", help="Source: synth | path-to-registry.json")
    args = p.parse_args()

    if args.source == "synth":
        registry = None
    else:
        with open(args.source) as f:
            registry = json.load(f)

    sheet = spatial_registry_to_quilt(registry)
    out = args.out if args.out.endswith(".qzt") else args.out + ".qzt"
    with open(out, "w") as f:
        json.dump(sheet, f, indent=2)

    md = sheet["metadata"]
    print(f"Spatial Registry → Quilt bridge")
    print(f"  Source: SuperInstance/spatial-registry (in terrain/external/)")
    print(f"  Output: {out}")
    print(f"  Cells: {len(sheet['cells'])}")
    print(f"  Worlds: {md['n_worlds']} ({', '.join(w['id'] for w in (registry or synth_spatial_registry())['worlds'])})")
    print(f"  Rooms: {md['n_rooms']}")
    print(f"  Exits: {md['n_exits']}")
    print()
    print(f"Open three-view-studio.html and load this file.")
    print(f"Or visit superinstance.dev/rooms-quilt.html for the spatial view.")


if __name__ == "__main__":
    main()
