#!/usr/bin/env python3
"""
vessel_to_quilt.py — Port vessel-agent-system data to a Quilt sheet.

The vessel-agent-system has a clean data model: vessel state, depth, GPS,
course, speed, fish holds, crew. Every one of these is a cell. The README
even says "A digital twin for F/V EILEEN."

This script reads vessel data (synthetic or real) and emits a .qzt file
that the 3-View Studio can render as:
  - TOP view: spatial chart of vessel + bathy cells
  - FRONT view: dashboard of present-state signals
  - SIDE view: timeline of vessel events

The vessel-agent-system is the user-articulated "top view" of cellular
architecture. The same cells, rendered three ways.

Author: Mavis
Date: 2026-08-20
"""
import json
import math
from typing import Any
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Cell model: every cell has path, kind, value, and (optional) depends_on
# ---------------------------------------------------------------------------
def cell(path: str, kind: str, value: Any, depends_on: list[str] | None = None) -> dict:
    """Create a Quilt cell."""
    c = {"path": path, "kind": kind, "value": value}
    if depends_on:
        c["depends_on"] = depends_on
    return c


# ---------------------------------------------------------------------------
# Synthetic vessel data (in production, this would come from AELMA twin)
# ---------------------------------------------------------------------------
def synth_vessel_state(t: float = 0.0) -> dict[str, Any]:
    """
    Generate a vessel state at time t (seconds).
    In production, this would call vessel-agent-system's twin state.
    """
    # Southeast Alaska — Thomas Bay area
    base_lat = 57.0 + math.sin(t * 0.01) * 0.05
    base_lon = -132.9 + math.cos(t * 0.01) * 0.05
    return {
        "lat": round(base_lat, 6),
        "lon": round(base_lon, 6),
        "sog_knots": round(6.5 + math.sin(t * 0.1) * 0.8, 2),
        "cog_deg": round(135 + math.sin(t * 0.05) * 20, 1),
        "heading_deg": round(135 + math.cos(t * 0.05) * 15, 1),
        "depth_m": round(45 + math.sin(t * 0.2) * 15, 1),
        "wind_speed_kt": round(8 + math.sin(t * 0.3) * 3, 1),
        "wind_dir_deg": round(220 + math.cos(t * 0.2) * 30, 1),
        "water_temp_c": round(8.5 + math.sin(t * 0.05) * 0.5, 2),
        "fuel_pct": round(82 - t * 0.001, 1),
        "rpm": round(1450 + math.sin(t * 0.1) * 100, 0),
        "fish_hold_kg": round(1240 + t * 0.5, 1),
        "crew_alert": "ok" if (t % 600) < 580 else "shift_change",
        "sea_state": round(2 + math.sin(t * 0.04) * 1, 1),
        "autopilot": "engaged" if t > 60 else "standby",
    }


# ---------------------------------------------------------------------------
# Build a Quilt sheet from vessel data
# ---------------------------------------------------------------------------
def vessel_to_quilt(
    start_t: float = 0.0,
    end_t: float = 1800.0,  # 30 minutes
    dt: float = 60.0,        # 1 sample per minute
    include_topography: bool = True,
) -> dict[str, Any]:
    """
    Build a Quilt sheet that mirrors the vessel-agent-system state.

    The sheet has these cell regions:
      - vessel.* — present state of the boat
      - env.*    — environment (wind, water temp, depth)
      - bathy.*  — bathymetry grid cells (top view)
      - nav.*    — navigation cells (course, waypoints)
      - holds.*  — fish hold inventory
      - crew.*   — crew state
      - timeline.* — historical samples (side view)
    """
    cells: list[dict] = []
    timeline_events: list[dict] = []

    # Generate samples
    n = int((end_t - start_t) / dt) + 1
    for i in range(n):
        t = start_t + i * dt
        st = synth_vessel_state(t)

        # Each sample becomes a temporal-snapshot cell under timeline.*
        timeline_events.append({
            "time": t,
            "snapshot": st,
        })

    # ---- Present-state cells (front view) ----
    # These are the "current" values; in a real system they'd be reactive
    # cells that update on every signal from AELMA.
    present = synth_vessel_state(end_t)

    cells.append(cell("vessel.lat", "value", present["lat"], ["timeline.last.lat"]))
    cells.append(cell("vessel.lon", "value", present["lon"], ["timeline.last.lon"]))
    cells.append(cell("vessel.sog_knots", "value", present["sog_knots"], ["timeline.last.sog_knots"]))
    cells.append(cell("vessel.cog_deg", "value", present["cog_deg"], ["timeline.last.cog_deg"]))
    cells.append(cell("vessel.heading_deg", "value", present["heading_deg"], ["timeline.last.heading_deg"]))
    cells.append(cell("vessel.autopilot", "value", present["autopilot"]))

    # ---- Environment cells (front view) ----
    cells.append(cell("env.depth_m", "value", present["depth_m"]))
    cells.append(cell("env.wind_speed_kt", "value", present["wind_speed_kt"]))
    cells.append(cell("env.wind_dir_deg", "value", present["wind_dir_deg"]))
    cells.append(cell("env.water_temp_c", "value", present["water_temp_c"]))
    cells.append(cell("env.sea_state", "value", present["sea_state"]))

    # ---- Engine + holds ----
    cells.append(cell("engine.rpm", "value", present["rpm"]))
    cells.append(cell("engine.fuel_pct", "value", present["fuel_pct"], ["engine.fuel_burn"]))
    cells.append(cell("engine.fuel_burn", "value", -0.5, ["engine.rpm"]))
    cells.append(cell("holds.fish_kg", "value", present["fish_hold_kg"], ["holds.catch_rate"]))
    cells.append(cell("holds.catch_rate", "value", 0.5, ["holds.active_set"]))
    cells.append(cell("holds.active_set", "value", True))

    # ---- Crew (one cell per crew member) ----
    crew = [
        {"name": "Captain Ahab", "role": "Captain", "shift_h": 4.5, "alertness": "high"},
        {"name": "First Mate Sigrid", "role": "First Mate", "shift_h": 6.0, "alertness": "medium"},
        {"name": "Deckhand Two", "role": "Deckhand", "shift_h": 8.5, "alertness": "low"},
        {"name": "Engineer Ojo", "role": "Engineer", "shift_h": 2.0, "alertness": "high"},
    ]
    for c in crew:
        cells.append(cell(f"crew.{c['name'].lower().replace(' ', '_')}.shift_h", "value", c["shift_h"]))
        cells.append(cell(f"crew.{c['name'].lower().replace(' ', '_')}.alertness", "value", c["alertness"]))
        cells.append(cell(f"crew.{c['name'].lower().replace(' ', '_')}.role", "value", c["role"]))

    # ---- Bathymetry cells (top view) ----
    # A 10x10 grid around the vessel
    if include_topography:
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                # Bathymetry gets deeper as we move away from shore
                # Simulated: depth increases with distance from origin
                dist = math.sqrt(dx * dx + dy * dy)
                depth = 25 + dist * 4 + math.sin(dx * 0.5) * 8
                cells.append(cell(
                    f"bathy.cell_{dx:+d}_{dy:+d}.depth",
                    "value",
                    round(depth, 1),
                ))

    # ---- Timeline cells (side view) ----
    # The whole timeline is one cell. Each event has time + value.
    for ev in timeline_events:
        cells.append(cell(
            f"timeline.t_{int(ev['time'])}.snapshot",
            "value",
            ev["snapshot"],
        ))
    # Last snapshot is the "live" front-view source
    cells.append(cell("timeline.last", "value", present, [
        f"timeline.t_{int(timeline_events[-1]['time'])}.snapshot"
    ]))
    cells.append(cell("timeline.all", "value", timeline_events))

    # ---- Navigation cells (waypoints) ----
    waypoints = [
        {"name": "Thomas Bay", "lat": 57.05, "lon": -132.95, "eta_min": 0},
        {"name": "Pt. Astley", "lat": 57.10, "lon": -132.85, "eta_min": 35},
        {"name": "Morse Cove", "lat": 57.20, "lon": -132.70, "eta_min": 95},
        {"name": "Spruce Island", "lat": 57.35, "lon": -132.55, "eta_min": 180},
    ]
    for wp in waypoints:
        cells.append(cell(f"nav.waypoint.{wp['name'].lower().replace(' ', '_')}", "value", wp))

    # The next waypoint
    cells.append(cell("nav.next_waypoint", "value", "pt_astley", [
        "vessel.lat", "vessel.lon", "nav.waypoint.thomas_bay"
    ]))

    return {
        "format": "quilt-z/1.0",
        "name": "F/V EILEEN — Vessel Agent System (Quilt bridge)",
        "description": "vessel-agent-system data ported to a Quilt sheet. 3-views: top (bathy), front (signals), side (timeline).",
        "source": "https://github.com/SuperInstance/vessel-agent-system",
        "tags": ["vessel", "marine", "top-view", "bathy", "telemetry"],
        "cells": cells,
        "metadata": {
            "sampled_at": datetime.now(timezone.utc).isoformat(),
            "n_samples": n,
            "duration_s": end_t - start_t,
            "dt_s": dt,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    p = argparse.ArgumentParser(description="vessel-agent-system → Quilt bridge")
    p.add_argument("--out", default="/tmp/vessel-quilt.json", help="Output .qzt path")
    p.add_argument("--duration-min", type=float, default=30, help="Duration in minutes")
    p.add_argument("--dt-s", type=float, default=60, help="Sample interval in seconds")
    args = p.parse_args()

    sheet = vessel_to_quilt(
        start_t=0.0,
        end_t=args.duration_min * 60,
        dt=args.dt_s,
    )

    # Save
    out = args.out
    if not out.endswith(".qzt"):
        out += ".qzt"
    with open(out, "w") as f:
        json.dump(sheet, f, indent=2)

    n_cells = len(sheet["cells"])
    n_bathy = sum(1 for c in sheet["cells"] if c["path"].startswith("bathy."))
    n_timeline = sum(1 for c in sheet["cells"] if c["path"].startswith("timeline."))

    print(f"Vessel → Quilt bridge")
    print(f"  Source: vessel-agent-system (AELMA, F/V EILEEN)")
    print(f"  Output: {out}")
    print(f"  Cells: {n_cells}")
    print(f"    - bathy grid: {n_bathy} (10×10 spatial cells for top view)")
    print(f"    - timeline:   {n_timeline} (temporal snapshots for side view)")
    print(f"    - present:    {n_cells - n_bathy - n_timeline} (front view)")
    print()
    print(f"Open three-view-studio.html and load this file.")


if __name__ == "__main__":
    main()
