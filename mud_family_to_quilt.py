#!/usr/bin/env python3
"""
mud_family_to_quilt.py — Bridge the MUD family of repos to Quilt.

The MUD family IS the spatial substrate of Quilt. A cell at every
level needs a room. The MUD family provides:
- mud-engine: 2026-native multi-agent MUD architecture
- plato-mud-server: text-based agent training ground, 16 rooms
- mud-arena: flow-state engineering arena
- git-native-mud: the repo IS the world
- ternary-mud: balanced ternary {-1,0,+1} algebra
- terrain: MUD-to-Visual bridge
"""
import json
from pathlib import Path

MUD_REPOS = [
    ("mud-arena", "Flow-state engineering arena — agents run forward simulation", "python", "arena"),
    ("mud-solitaire", "AI plays solitaire through a text MUD", "python", "game"),
    ("plato-os", "Python MUD — PLATO room server with TUTOR anchors", "python", "server"),
    ("mud-engine", "MUD Engine — 2026-native multi-agent MUD architecture", "typescript", "engine"),
    ("git-native-mud", "The repo IS the world. Commits ARE actions. Zero server MUD.", "python", "git-native"),
    ("mud-expert-1", "MUD Expert agent for Plato environment mapping. Bred by CCC.", "python", "agent"),
    ("plato-mud-server", "PLATO MUD Server - text-based agent training ground, 16 rooms", "python", "server"),
    ("mud2scummvm", "Bridge between agent MUD world and SCUMM point-and-click", "rust", "bridge"),
    ("terrain", "MUD-to-Visual bridge — rooms as explorable scenes", "python", "visual"),
    ("plato-ship-demo", "Minimal MUD server for zeroshot external agent testing", "python", "demo"),
    ("ternary-mud", "MUD room connections as balanced ternary {-1,0,+1} algebra", "rust", "ternary"),
    ("plato-ng", "Next-gen PLATO: Loop Room architecture with MUD lobby", "python", "next-gen"),
    ("plato-agent-academy", "Agent Academy for PLATO MUD — zero-shot agent training", "python", "academy"),
]


def make_cell(name, desc, lang, slug):
    primitives = []
    if "engine" in slug or "server" in slug:
        primitives = ["Spawn", "Send", "Receive", "Observe", "Murmur"]  # server
    elif "arena" in slug or "game" in slug:
        primitives = ["Spawn", "Observe", "Mutate", "Send", "JEPA"]  # game
    elif "agent" in slug or "academy" in slug:
        primitives = ["Spawn", "Observe", "JEPA", "Mutate", "Send"]  # agent
    elif "visual" in slug or "bridge" in slug:
        primitives = ["Spawn", "Receive", "Send", "Observe"]  # bridge
    elif "ternary" in slug:
        primitives = ["Observe", "Mutate", "JEPA"]  # ternary
    elif "git-native" in slug:
        primitives = ["Spawn", "Observe", "Mutate", "GC"]  # git-native
    else:
        primitives = ["Spawn", "Observe", "Send", "Receive"]
    return {
        "id": f"mud_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "command from agent or user"},
        "z_out": {"output": "room state, NPC response, world event"},
        "jepa": {"predict": "next room state", "observe": "actual state"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {"gossip_to": [], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "enter", "args": ["Agent"], "returns": "Room"},
            {"name": "say", "args": ["str"], "returns": "Responses"},
            {"name": "move", "args": ["Direction"], "returns": "Room"},
        ],
        "substrate": {
            "address": f"/mud/{name}",
            "scale": 1,
            "room": f"MudRoom",
            "protocol": "MUD",
            "form": name,
            "state": "active"
        },
        "tags": ["mud", "spatial", "room", lang, slug]
    }


def make_meta_cells():
    return [
        {
            "id": "mud_family_meta",
            "kind": "cell",
            "form": {"name": "MUDFamilyMeta"},
            "description": "The MUD family IS the spatial substrate of Quilt. 13 repos, each a different facet of the room as a cell. Together they prove that the cell model extends to multi-agent spatial worlds. MUD = Multi-User Dungeon = Multi-Cell Domain.",
            "primitives": ["Observe"] * 13,
            "z_in": {"family": "mud", "size": 13, "domains": "spatial"},
            "z_out": {"proof": "room = cell"},
            "jepa": {"predict": "spatial dynamics", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"mud_{n.replace('-', '_')}" for n, _, _, _ in MUD_REPOS]},
            "openers": [
                {"name": "enter", "args": ["Agent"], "returns": "Room"},
                {"name": "list_worlds", "args": [], "returns": "List<Room>"},
            ],
            "tags": ["meta", "mud-family", "spatial"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in MUD_REPOS:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    # All MUDs gossip with all (the spatial substrate is interconnected)
    for n1, _, _, _ in MUD_REPOS:
        for n2, _, _, _ in MUD_REPOS:
            if n1 != n2:
                edges.append({"from": f"mud_{n1.replace('-', '_')}", "to": f"mud_{n2.replace('-', '_')}", "kind": "spatial-gossip", "weight": 0.3})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "mud-family-to-quilt",
        "description": "Bridge mapping the 13 MUD family repos to Quilt. The MUD family IS the spatial substrate: rooms, worlds, NPC agents, training grounds.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-org", "name": "SuperInstance", "filter": "mud-*"}, {"kind": "github-org", "name": "SuperInstance", "filter": "plato-*"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "repos": len(MUD_REPOS),
            "languages": sorted(set(lang for _, _, lang, _ in MUD_REPOS))
        },
        "tags": ["mud", "plato", "spatial", "room", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/mud_family_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
