#!/usr/bin/env python3
"""
wesley_dmlog_imagination_to_quilt.py — Bridge the imagination substrate to Quilt.

The imagination substrate is the cell's CAPACITY FOR STORY:
- wesley-holodeck: creative loop, 2B model writes, 4 teachers, Myst-style visual
- dmlog-agent: agent framework for D&D/Tabletop RPGs (NPCs, factions, locations)
- dmlog-ai-1: AI Dungeon Master for TTRPGs (Cloudflare Workers, fork-first)
- plato-dmn-ecm: DMN/ECN reverse-actualization engine (creativity via functional distance)

This is the cell's INNER LIFE — the capacity to make meaning.
"""
import json
from pathlib import Path

IMAGINATION = [
    # wesley-holodeck
    ("wesley-holodeck", "Creative loop: 2B model (Wesley/granite-3.1-dense:2b) writes, 4 teachers rotate, FLUX-2-max scene, TTS narration, Myst-style visual holodeck. Twin worlds: text + visual.", "html", "creative-loop"),
    # dmlog-agent
    ("dmlog-agent", "Agent framework for D&D/Tabletop RPGs. NPC tracking, factions, locations, encounters, session notes, JSON export/import.", "python", "ttrpg-agent"),
    # dmlog-ai-1
    ("dmlog-ai-1", "DMLog.ai — AI Dungeon Master for TTRPGs. Cloudflare Workers, fork-first, zero lock-in, plain text in KV, zero runtime deps.", "?", "dungeon-master"),
    # plato-dmn-ecm
    ("plato-dmn-ecm", "DMN/ECN reverse-actualization. Default Mode Network (creative) + Executive Control Network (logical) in tandem, with PLATO as rostral prefrontal cortex bridge. Gradient = DMN novelty − ECN constraint.", "python", "creativity-engine"),
    # wesley-holodeck sub-systems
    ("wesley_writer", "Wesley (granite-3.1-dense:2b) writes first draft via local Ollama. No API calls. His own voice.", "ollama", "writer"),
    ("wesley_teachers", "4 teachers rotate: Earnest (Seed-2.0-mini, kind), Philosopher (Seed-2.0-pro, deep), Craftsman (Qwen3-Coder, form), Voice (Hermes-3-Llama-3.1-405B, personality).", "deepinfra", "teachers"),
    ("wesley_flux", "FLUX-2-max scene illustration. Myst-style atmospheric backgrounds.", "flux", "scene-art"),
    ("wesley_tts", "Qwen3-TTS-VoiceDesign. Narration. Speaks Wesley's pieces.", "tts", "narration"),
    ("wesley_holodeck_html", "Myst/Monkey Island-style point-and-click. Dark scenes, ambient audio, clickable hotspots. The visual twin of Wesley's text world.", "html", "visual-twin"),
    # dmlog subsystems
    ("dmlog_npcs", "NPC tracking: secrets, motivations, alignment, status.", "python", "npc"),
    ("dmlog_factions", "Faction management: influence, allies, enemies.", "python", "faction"),
    ("dmlog_locations", "Location database: connections, notable features.", "python", "location"),
    ("dmlog_encounters", "Encounter builder: terrain, creatures, objectives, ratings.", "python", "encounter"),
    # dmn-ecm subsystems
    ("dmn_divergent", "DMN model generates N creative options, no filtering. The divergent phase.", "?", "divergent"),
    ("ecn_convergent", "ECN model critiques each option for logical consistency. The convergent phase.", "?", "convergent"),
    ("dmn_recombination", "DMN model revises based on critiques without losing novelty.", "?", "recombination"),
    ("ecn_final", "ECN model ranks and synthesizes the best result.", "?", "final"),
    ("rpec_bridge", "PLATO as rostral prefrontal cortex bridge. The bridge that holds DMN and ECN apart.", "?", "bridge"),
]


def make_cell(name, desc, lang, slug):
    primitives = []
    if "wesley" in name or "holodeck" in name:
        if "writer" in name or "flux" in name or "tts" in name or "html" in name:
            primitives = ["Spawn", "Mutate", "Send", "Receive"]  # creative output
        elif "teachers" in name:
            primitives = ["Spawn", "Observe", "JEPA", "Send"]  # feedback
        else:
            primitives = ["Spawn", "Observe", "Mutate", "JEPA", "Murmur"]  # holodeck core
    elif "dmlog" in name:
        if "npcs" in name or "factions" in name or "locations" in name:
            primitives = ["Spawn", "Observe", "Mutate", "GC"]  # knowledge base
        else:
            primitives = ["Spawn", "Observe", "Mutate", "Send", "Receive"]  # game
    elif "dmn" in name or "ecn" in name or "rpec" in name:
        if "divergent" in name or "recombination" in name:
            primitives = ["Spawn", "Observe", "Mutate", "Send"]  # creative
        else:
            primitives = ["Spawn", "Observe", "JEPA", "Mutate"]  # logical
    else:
        primitives = ["Spawn", "Observe", "Mutate"]
    return {
        "id": f"img_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("-", " ").title().replace(" ", "")},
        "description": desc,
        "language": lang,
        "slug": slug,
        "primitives": primitives,
        "z_in": {"input": "story, prompt, NPC, encounter, gradient target"},
        "z_out": {"output": "draft, scene, narration, NPC state, reverse-actualized result"},
        "jepa": {"predict": "creative trajectory", "observe": "actual output"},
        "double_entry": {"gamma": 0.8, "eta": 0.2},  # Creativity is γ-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "imagining"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "imagine", "args": ["Prompt"], "returns": "Story"},
            {"name": "play", "args": ["Session"], "returns": "Game"},
        ],
        "substrate": {
            "address": f"/imagination/{name}",
            "scale": 1,
            "room": "ImaginationRoom",
            "protocol": "Story",
            "form": name,
            "state": "ready"
        },
        "tags": ["imagination", "story", "creativity", lang]
    }


def make_meta_cells():
    return [
        {
            "id": "imagination_meta",
            "kind": "cell",
            "form": {"name": "ImaginationMeta"},
            "description": "The imagination substrate IS the cell's capacity for story. wesley-holodeck (creative loop, twin worlds), dmlog-agent/dmlog-ai-1 (TTRPG), plato-dmn-ecm (reverse-actualization). The cell can dream, write, play, and create.",
            "primitives": ["Observe"] * 18,
            "z_in": {"family": "imagination", "size": 18},
            "z_out": {"proof": "cell can imagine"},
            "jepa": {"predict": "story arc", "verified": True},
            "double_entry": {"gamma": 0.8, "eta": 0.2},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {"children": [f"img_{n.replace('-', '_')}" for n, _, _, _ in IMAGINATION]},
            "tags": ["meta", "imagination", "story"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang, slug in IMAGINATION:
        cells.append(make_cell(name, desc, lang, slug))
    cells.extend(make_meta_cells())
    edges = []
    for n1, _, _, _ in IMAGINATION:
        for n2, _, _, _ in IMAGINATION:
            if n1 != n2:
                edges.append({"from": f"img_{n1.replace('-', '_')}", "to": f"img_{n2.replace('-', '_')}", "kind": "imagination-gossip", "weight": 0.4})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "imagination-substrate-to-quilt",
        "description": "Bridge mapping 4 imagination repos + 14 subsystems to Quilt. The cell's capacity for story: wesley-holodeck, dmlog-agent, dmlog-ai-1, plato-dmn-ecm.",
        "cells": cells, "edges": edges,
        "external_refs": [
            {"kind": "github-repo", "name": "wesley-holodeck", "org": "SuperInstance"},
            {"kind": "github-repo", "name": "dmlog-agent", "org": "SuperInstance"},
            {"kind": "github-repo", "name": "dmlog-ai-1", "org": "SuperInstance"},
            {"kind": "github-repo", "name": "plato-dmn-ecm", "org": "SuperInstance"},
        ],
        "stats": {
            "total_cells": len(cells), "total_edges": len(edges),
            "repos": 4, "subsystems": 14
        },
        "tags": ["imagination", "story", "creativity", "wesley", "dmlog", "dmn-ecm", "bridge"]
    }


def main():
    qzt = build_qzt()
    Path("/workspace/bridges/wesley_dmlog_imagination_to_quilt.qzt").write_text(json.dumps(qzt, indent=2))
    print(f"Wrote imagination: {len(qzt['cells'])} cells, {len(qzt['edges'])} edges")


if __name__ == "__main__":
    main()
