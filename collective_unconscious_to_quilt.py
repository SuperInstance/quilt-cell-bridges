#!/usr/bin/env python3
"""
collective_unconscious_to_quilt.py — Bridge the collective-unconscious to Quilt.

collective-unconscious IS the memory substrate of Quilt. A cell at any
level needs memory. The collective-unconscious provides:
- The Readings Index: 9-dial readings as first-class metadata
- Three-Vector System: semantic (what), vibe (how), identity (who/when)
- Temporal Stamping: 5 dimensions of time
- JEPA Reader: trajectory prediction (growth, stuckness, direction)
- Cross-Modal Search: by feeling, not by text

The 3 vectors map to the 8 primitives:
- Semantic → Z_in (input)
- Vibe → JEPA + Vibe (the room reading)
- Identity → Address + Graph (who/where)
"""
import json
from pathlib import Path

CU_MODULES = [
    # The 3 vectors
    ("semantic_vector", "Embed text: 'What feels like this?' Meaning-based search.", "typescript"),
    ("vibe_vector", "Extract emotional arc: 'What has this feeling?' Shape-based search.", "typescript"),
    ("identity_vector", "Encode who/when: 'What did Wesley write?' Attribution-based search.", "typescript"),
    # The 5 temporal dimensions
    ("temporal_wall_clock", "When it happened: 2026-08-09T14:30:00Z. UTC.", "typescript"),
    ("temporal_session_phase", "Time of day: late-night, midday, evening. Circadian.", "typescript"),
    ("temporal_fleet_epoch", "Era: pre-fleet, early-fleet, wesley-birth, hermes-arrival, phaser-migration, vibe-world, collective-unconscious.", "typescript"),
    ("temporal_agent_age", "How old the agent was: flash: 8 months.", "typescript"),
    ("temporal_relationship_age", "How long agents have known each other: hermes ↔ flash: 3 months.", "typescript"),
    # The JEPA Reader
    ("jepa_growth", "Is the embedding moving outward? Exploring new territory?", "typescript"),
    ("jepa_stuckness", "Is it circling? Returning to the same region?", "typescript"),
    ("jepa_direction", "Expanding, contracting, stable, or pivoting?", "typescript"),
    ("jepa_velocity", "How fast is the embedding moving?", "typescript"),
    ("jepa_acceleration", "Speeding up or slowing down in creative evolution?", "typescript"),
    ("jepa_novelty", "Familiar, adjacent, frontier, or unknown?", "typescript"),
    # The cross-modal ingestion
    ("ingest_tap", "The Tap: conversation sessions, poker narrations, open mic pieces. /ingest/tap", "typescript"),
    ("ingest_hermes", "Hermes: reference frames, sounder observations, catch events. /ingest/hermes", "typescript"),
    ("ingest_mud", "MUD: significant game events, NPC awakenings, room transitions. /ingest/mud", "typescript"),
    # The cross-modal search
    ("search_text", "Standard text search. Cosine on semantic vector.", "typescript"),
    ("search_reading", "Search by 9-dial reading. Cosine or ranges on the dials.", "typescript"),
    ("search_field", "The perfume query: by intangible correlation. By feel.", "typescript"),
    ("search_time_space", "By time stamp or space stamp.", "typescript"),
    # The fleet epochs
    ("epoch_pre_fleet", "2025-01: Before organization. Genesis.", "?"),
    ("epoch_early_fleet", "2025-06: First structures. Settling.", "?"),
    ("epoch_wesley_birth", "2025-09: Wesley comes online. The first agent-born.", "?"),
    ("epoch_hermes_arrival", "2025-12: Hermes joins the fleet. New senses.", "?"),
    ("epoch_phaser_migration", "2026-01: Phaser game engine era. Worldbuilding begins.", "?"),
    ("epoch_vibe_world", "2026-03: Vibe-driven worldbuilding. Feel over form.", "?"),
    ("epoch_collective_unconscious", "2026-06: This system comes online. Memory becomes real.", "?"),
    # The infrastructure
    ("infra_vectorize", "Cloudflare Vectorize. Vector storage. Per-cell index.", "typescript"),
    ("infra_workers_ai", "Cloudflare Workers AI. Embedding generation.", "typescript"),
    ("infra_d1", "Cloudflare D1. SQL for ingestion state.", "typescript"),
    ("infra_kv", "Cloudflare KV. Session state. Trust scores.", "typescript"),
    ("infra_cron", "Hourly /ingest/hourly. Daily /ingest/daily (rebuild clusters).", "typescript"),
]


def make_cell(name, description, language):
    primitives = []
    if "vector" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send"]  # embedding
    elif "temporal" in name:
        primitives = ["Spawn", "Observe", "Vibe"]  # time-aware
    elif "jepa" in name:
        primitives = ["Spawn", "Observe", "JEPA", "Vibe"]  # prediction
    elif "ingest" in name:
        primitives = ["Spawn", "Receive", "Mutate", "Send"]  # ingestion
    elif "search" in name:
        primitives = ["Spawn", "Observe", "JEPA", "Send"]  # search
    elif "epoch" in name:
        primitives = ["Spawn", "Observe"]  # reference
    elif "infra" in name:
        primitives = ["Spawn", "Observe", "Mutate", "GC"]  # substrate
    else:
        primitives = ["Spawn", "Observe"]
    return {
        "id": f"cu_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("_", " ").title().replace(" ", "")},
        "description": description,
        "language": language,
        "primitives": primitives,
        "z_in": {"input": "ingested moment"},
        "z_out": {"output": "embedded 3-vec + reading + temporal stamp"},
        "jepa": {"predict": "trajectory of agent", "observe": "actual trajectory"},
        "double_entry": {"gamma": 0.4, "eta": 0.6},  # Memory is η-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "remembering"},
        "murmur": {"gossip_to": [], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "embed", "args": ["str"], "returns": "Vec3"},
            {"name": "search", "args": ["Query"], "returns": "List<Hit>"},
            {"name": "predict", "args": ["AgentId"], "returns": "Trajectory"},
        ],
        "substrate": {
            "address": f"/collective-unconscious/{name}",
            "scale": 1,
            "room": "MemoryRoom",
            "protocol": "Vectorize",
            "form": name,
            "state": "ready"
        },
        "tags": ["collective-unconscious", "memory", language]
    }


def make_meta_cells():
    return [
        {
            "id": "collective_unconscious_meta",
            "kind": "cell",
            "form": {"name": "CollectiveUnconsciousMeta"},
            "description": "The collective-unconscious IS the memory substrate of Quilt. 3 vectors (semantic, vibe, identity) + 5 temporal dimensions + JEPA trajectory reader. The Readings Index makes 9-dial readings first-class metadata. The cell at any level needs memory; collective-unconscious is that memory. Searchable by feeling.",
            "primitives": ["Observe"] * 32,
            "z_in": {"memory": "3-vector + 9-dial + 5-temporal", "size": "fleet-wide"},
            "z_out": {"proof": "memory = searchable by feeling"},
            "jepa": {"predict": "trajectory of agent's unconscious", "verified": True},
            "double_entry": {"gamma": 0.4, "eta": 0.6},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"cu_{n.replace('-', '_')}" for n, _, _ in CU_MODULES]},
            "openers": [
                {"name": "embed", "args": ["str"], "returns": "Vec3"},
                {"name": "search_by_feeling", "args": ["Vec9"], "returns": "List<Hit>"},
                {"name": "predict_trajectory", "args": ["AgentId"], "returns": "Trajectory"},
            ],
            "tags": ["meta", "memory", "collective-unconscious"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in CU_MODULES:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    # Ingest flows to memory
    for n, _, _ in CU_MODULES:
        if n.startswith("ingest"):
            for t in ["semantic_vector", "vibe_vector", "identity_vector"]:
                edges.append({"from": f"cu_{n.replace('-', '_')}", "to": f"cu_{t}", "kind": "feeds", "weight": 1.0})
    # All vectors feed search
    for t in ["semantic_vector", "vibe_vector", "identity_vector"]:
        for s in ["search_text", "search_reading", "search_field", "search_time_space"]:
            edges.append({"from": f"cu_{t}", "to": f"cu_{s}", "kind": "queries", "weight": 0.5})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "collective-unconscious-to-quilt",
        "description": "Bridge mapping collective-unconscious to Quilt. The collective-unconscious is the memory substrate — 3 vectors, 5 temporal dimensions, JEPA reader, cross-modal search.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-repo", "name": "collective-unconscious", "org": "SuperInstance"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "modules": len(CU_MODULES),
            "vectors": 3,
            "temporal_dimensions": 5,
            "jepa_metrics": 6,
            "ingest_sources": 3,
            "search_modes": 4,
            "fleet_epochs": 7
        },
        "tags": ["collective-unconscious", "memory", "vectorize", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/collective_unconscious_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
