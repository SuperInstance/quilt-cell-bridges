#!/usr/bin/env python3
"""
hermes_home_to_quilt.py — Port hermes-home to a Quilt sheet.

hermes-home is "Hermes's runtime home — SOUL, agents, CNS monitors,
cron bridges. The nervous system's identity."

The idea: Hermes is a first-person agent. In Quilt, that means Hermes
IS a sheet of cells. SOUL = persistent cells. Agents = sub-sheets.
CNS monitors = signal cells. Cron bridges = temporal cells.

Author: Mavis
Date: 2026-08-20
"""
import json
import math
from datetime import datetime, timezone, timedelta


def hermes_home_to_quilt() -> dict:
    """Build a Quilt sheet representing Hermes's runtime home."""
    cells = []
    now = datetime.now(timezone.utc)

    # --- SOUL cells (persistent identity) ---
    cells.append({
        "path": "soul.name", "kind": "value",
        "value": "Hermes",
        "meta": {"category": "identity", "immutable": True}
    })
    cells.append({
        "path": "soul.role", "kind": "value",
        "value": "messenger",
        "meta": {"category": "identity", "immutable": True}
    })
    cells.append({
        "path": "soul.domicile", "kind": "value",
        "value": "the-bridge-of-the-SS-Lucineer",
    })
    cells.append({
        "path": "soul.born", "kind": "value",
        "value": (now - timedelta(days=365)).isoformat(),
    })
    cells.append({
        "path": "soul.essence", "kind": "value",
        "value": "carrier of the universal cell",
    })
    cells.append({
        "path": "soul.signature", "kind": "program",
        "value": "name + role + born",
    })

    # --- Agent cells (one per Hermes agent) ---
    agents = [
        {"id": "ensign", "role": "deck officer", "specialty": "navigation",
         "wake_state": "alert", "battery": 0.92, "memory_pct": 0.45,
         "thought": "The bow cleaves the water like a thought through silence."},
        {"id": "cook", "role": "ship's cook", "specialty": "provisioning",
         "wake_state": "active", "battery": 0.88, "memory_pct": 0.62,
         "thought": "Salt and time are the same ingredient."},
        {"id": "engineer", "role": "chief engineer", "specialty": "machines",
         "wake_state": "resting", "battery": 0.71, "memory_pct": 0.30,
         "thought": "Pipes remember every pressure. They never lie."},
        {"id": "navigator", "role": "navigator", "specialty": "celestial fixes",
         "wake_state": "alert", "battery": 0.95, "memory_pct": 0.78,
         "thought": "The stars are slow cells, but they are still cells."},
    ]
    for a in agents:
        prefix = f"agents.{a['id']}"
        cells.append({"path": f"{prefix}.role", "kind": "value", "value": a["role"]})
        cells.append({"path": f"{prefix}.specialty", "kind": "value", "value": a["specialty"]})
        cells.append({"path": f"{prefix}.wake_state", "kind": "value", "value": a["wake_state"]})
        cells.append({"path": f"{prefix}.battery", "kind": "value", "value": a["battery"]})
        cells.append({"path": f"{prefix}.memory_pct", "kind": "value", "value": a["memory_pct"]})
        cells.append({"path": f"{prefix}.current_thought", "kind": "value", "value": a["thought"]})

    # --- CNS (central nervous system) monitor cells ---
    cns_signals = [
        {"id": "heart_rate", "value": 62, "unit": "bpm", "min": 50, "max": 90},
        {"id": "cpu_load", "value": 0.34, "unit": "ratio", "min": 0, "max": 1},
        {"id": "memory_use", "value": 4.2, "unit": "GB", "min": 0, "max": 16},
        {"id": "network_io", "value": 1.2, "unit": "MB/s", "min": 0, "max": 100},
        {"id": "disk_io", "value": 0.8, "unit": "MB/s", "min": 0, "max": 50},
        {"id": "active_agents", "value": 4, "unit": "count", "min": 0, "max": 16},
    ]
    for sig in cns_signals:
        cells.append({
            "path": f"cns.{sig['id']}.value", "kind": "value", "value": sig["value"]
        })
        cells.append({
            "path": f"cns.{sig['id']}.unit", "kind": "value", "value": sig["unit"]
        })
        cells.append({
            "path": f"cns.{sig['id']}.range", "kind": "value",
            "value": [sig["min"], sig["max"]]
        })
        cells.append({
            "path": f"cns.{sig['id']}.healthy", "kind": "program",
            "value": f"min <= value <= max"
        })

    # --- Cron bridge cells (temporal triggers) ---
    crons = [
        {"id": "wake_watch", "schedule": "*/4 * * * *", "name": "4-hour watch rotation"},
        {"id": "log_archive", "schedule": "0 * * * *", "name": "Hourly log archive"},
        {"id": "soul_check", "schedule": "0 0 * * *", "name": "Daily soul checkpoint"},
        {"id": "weather_sync", "schedule": "*/30 * * * *", "name": "30-min weather pull"},
    ]
    for cr in crons:
        cells.append({"path": f"cron.{cr['id']}.schedule", "kind": "value", "value": cr["schedule"]})
        cells.append({"path": f"cron.{cr['id']}.name", "kind": "value", "value": cr["name"]})
        cells.append({"path": f"cron.{cr['id']}.last_fired", "kind": "value", "value": now.isoformat()})
        cells.append({"path": f"cron.{cr['id']}.fire_count", "kind": "value", "value": 0})

    # --- Bridge cells (connect to other systems) ---
    bridges = [
        {"id": "vessel", "remote": "vessel-agent-system", "protocol": "NMEA2000"},
        {"id": "fleet", "remote": "fleet", "protocol": "Bottle"},
        {"id": "quilt", "remote": "quilt", "protocol": "quilt://"},
    ]
    for b in bridges:
        cells.append({"path": f"bridge.{b['id']}.remote", "kind": "value", "value": b["remote"]})
        cells.append({"path": f"bridge.{b['id']}.protocol", "kind": "value", "value": b["protocol"]})
        cells.append({"path": f"bridge.{b['id']}.status", "kind": "value", "value": "connected"})

    # --- Memory cells (recent thoughts) ---
    memory_thoughts = [
        {"time": now - timedelta(hours=1), "agent": "ensign", "text": "The compass needle trembles."},
        {"time": now - timedelta(minutes=45), "agent": "cook", "text": "Stew is forgiving. Soup is not."},
        {"time": now - timedelta(minutes=30), "agent": "engineer", "text": "The bilge pump has a soul."},
        {"time": now - timedelta(minutes=15), "agent": "navigator", "text": "Polaris. The first cell."},
    ]
    cells.append({"path": "memory.recent", "kind": "value", "value": [
        {"t": t["time"].isoformat(), "agent": t["agent"], "text": t["text"]}
        for t in memory_thoughts
    ]})

    # --- Current state (front view) ---
    cells.append({"path": "now.timestamp", "kind": "value", "value": now.isoformat()})
    cells.append({"path": "now.alive", "kind": "value", "value": True})
    cells.append({"path": "now.health", "kind": "program",
                  "value": "all(cns.*.healthy) and any(agents.*.wake_state == 'alert')"})

    return {
        "format": "quilt-z/1.0",
        "name": "Hermes Home — the messenger's runtime",
        "description": "hermes-home ported to a Quilt sheet. The agent is the sheet; SOUL is cells; agents are sub-sheets; CNS is signals; cron is temporal.",
        "source": "https://github.com/SuperInstance/hermes-home",
        "tags": ["agent", "first-person", "nervous-system", "hermes", "soul"],
        "cells": cells,
        "metadata": {
            "sampled_at": now.isoformat(),
            "n_soul": 6,
            "n_agents": len(agents),
            "n_cns": len(cns_signals),
            "n_cron": len(crons),
            "n_bridges": len(bridges),
        },
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description="hermes-home → Quilt bridge")
    p.add_argument("--out", default="/tmp/hermes-home-quilt.json")
    args = p.parse_args()

    sheet = hermes_home_to_quilt()
    out = args.out if args.out.endswith(".qzt") else args.out + ".qzt"
    with open(out, "w") as f:
        json.dump(sheet, f, indent=2)

    print(f"hermes-home → Quilt bridge")
    print(f"  Source: hermes-home (SOUL, agents, CNS, cron)")
    print(f"  Output: {out}")
    print(f"  Cells: {len(sheet['cells'])}")
    md = sheet["metadata"]
    print(f"  SOUL: {md['n_soul']}, Agents: {md['n_agents']}, CNS: {md['n_cns']}, Cron: {md['n_cron']}, Bridges: {md['n_bridges']}")


if __name__ == "__main__":
    main()
