#!/usr/bin/env python3
"""
chart_room_to_quilt.py — Port chart-room data to a Quilt sheet.

The chart-room repo is "Four panels. Four perspectives. One truth."
This is literally a 3-views architecture in 1995-era Python.

This bridge maps the four chart-room panels to four cell regions,
all derived from a single TruthCell. The 3-View Studio can then render
the same cell graph as:
  - TOP view: Navigation panel
  - FRONT view: Engineering panel
  - SIDE view: Tactical timeline + Sonar sweep

Author: Mavis
Date: 2026-08-20
"""
import json
import math
from datetime import datetime, timezone


def synth_truth(t: float = 0.0) -> dict:
    """Generate a single truth state at time t."""
    return {
        "vessel_id": "F/V EILEEN",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "position": {
            "lat": 57.0 + math.sin(t * 0.01) * 0.1,
            "lon": -132.9 + math.cos(t * 0.01) * 0.1,
        },
        "course": {
            "cog_deg": 135 + math.sin(t * 0.05) * 20,
            "heading_deg": 135 + math.cos(t * 0.05) * 15,
            "sog_knots": 6.5 + math.sin(t * 0.1) * 0.8,
        },
        "environment": {
            "depth_m": 45 + math.sin(t * 0.2) * 15,
            "wind_kt": 8 + math.sin(t * 0.3) * 3,
            "sea_state": 2 + math.sin(t * 0.04) * 1,
        },
        "engine": {
            "rpm": 1450 + int(math.sin(t * 0.1) * 100),
            "fuel_pct": max(0, 82 - t * 0.001),
            "oil_temp_c": 78 + math.sin(t * 0.05) * 3,
        },
        "tactical": {
            "threat_level": "green" if t < 600 else "yellow" if t < 1200 else "orange",
            "closest_vessel_nm": round(2.5 + math.sin(t * 0.05) * 1.0, 1),
            "alert_count": int(t / 300) % 4,
        },
        "sonar": {
            "fish_density": round(0.3 + math.sin(t * 0.1) * 0.2, 2),
            "depth_to_fish_m": round(30 + math.sin(t * 0.2) * 10, 1),
            "school_size_kg": round(500 + math.sin(t * 0.3) * 200, 0),
        },
    }


def chart_room_to_quilt(
    duration_s: float = 1800.0,
    dt_s: float = 60.0,
) -> dict:
    """
    Build a Quilt sheet mirroring chart-room's four panels.

    Cell regions:
      - truth.*      — the single source of truth (all four panels read from here)
      - nav.*        — Navigation panel (top view)
      - eng.*        — Engineering panel (front view)
      - tac.*        — Tactical panel
      - son.*        — Sonar panel
      - timeline.*   — historical truth snapshots (side view)
    """
    cells = []
    n_samples = int(duration_s / dt_s) + 1
    truth_now = synth_truth(duration_s)

    # --- The ONE Truth ---
    # This is the "cell of cells" — every panel reads from it.
    cells.append({"path": "truth.now", "kind": "value", "value": truth_now})
    cells.append({"path": "truth.source", "kind": "value", "value": "chart-room:four-panels-one-truth"})

    # --- Navigation panel cells (top view) ---
    p = truth_now["position"]
    c = truth_now["course"]
    cells.append({"path": "nav.lat", "kind": "value", "value": p["lat"], "depends_on": ["truth.now"]})
    cells.append({"path": "nav.lon", "kind": "value", "value": p["lon"], "depends_on": ["truth.now"]})
    cells.append({"path": "nav.cog_deg", "kind": "value", "value": c["cog_deg"]})
    cells.append({"path": "nav.heading_deg", "kind": "value", "value": c["heading_deg"]})
    cells.append({"path": "nav.sog_knots", "kind": "value", "value": c["sog_knots"]})
    cells.append({"path": "nav.vessel_id", "kind": "value", "value": truth_now["vessel_id"]})

    # --- Engineering panel cells (front view) ---
    e = truth_now["engine"]
    cells.append({"path": "eng.rpm", "kind": "value", "value": e["rpm"]})
    cells.append({"path": "eng.fuel_pct", "kind": "value", "value": e["fuel_pct"], "depends_on": ["eng.fuel_burn"]})
    cells.append({"path": "eng.fuel_burn", "kind": "value", "value": -0.5, "depends_on": ["eng.rpm"]})
    cells.append({"path": "eng.oil_temp_c", "kind": "value", "value": e["oil_temp_c"]})
    cells.append({"path": "eng.healthy", "kind": "program", "value": "fuel_pct > 5 and oil_temp_c < 95"})

    # --- Tactical panel cells ---
    ta = truth_now["tactical"]
    cells.append({"path": "tac.threat_level", "kind": "value", "value": ta["threat_level"]})
    cells.append({"path": "tac.closest_vessel_nm", "kind": "value", "value": ta["closest_vessel_nm"]})
    cells.append({"path": "tac.alert_count", "kind": "value", "value": ta["alert_count"]})

    # --- Sonar panel cells ---
    s = truth_now["sonar"]
    cells.append({"path": "son.fish_density", "kind": "value", "value": s["fish_density"]})
    cells.append({"path": "son.depth_to_fish_m", "kind": "value", "value": s["depth_to_fish_m"]})
    cells.append({"path": "son.school_size_kg", "kind": "value", "value": s["school_size_kg"]})

    # --- Timeline cells (side view) ---
    # Each panel gets its own track in the timeline.
    nav_track = []
    eng_track = []
    tac_track = []
    son_track = []

    for i in range(n_samples):
        t = i * dt_s
        truth = synth_truth(t)
        nav_track.append({"time": t, "lat": truth["position"]["lat"], "lon": truth["position"]["lon"], "cog": truth["course"]["cog_deg"]})
        eng_track.append({"time": t, "rpm": truth["engine"]["rpm"], "fuel": truth["engine"]["fuel_pct"]})
        tac_track.append({"time": t, "threat": truth["tactical"]["threat_level"], "alert": truth["tactical"]["alert_count"]})
        son_track.append({"time": t, "density": truth["sonar"]["fish_density"], "size_kg": truth["sonar"]["school_size_kg"]})

    cells.append({"path": "timeline.nav", "kind": "value", "value": nav_track})
    cells.append({"path": "timeline.eng", "kind": "value", "value": eng_track})
    cells.append({"path": "timeline.tac", "kind": "value", "value": tac_track})
    cells.append({"path": "timeline.son", "kind": "value", "value": son_track})

    # --- Bathymetry grid for the chart-room's chart panel ---
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            dist = math.sqrt(dx * dx + dy * dy)
            depth = 25 + dist * 4 + math.sin(dx * 0.5) * 8
            cells.append({"path": f"chart.bathy_{dx:+d}_{dy:+d}.depth", "kind": "value", "value": round(depth, 1)})

    return {
        "format": "quilt-z/1.0",
        "name": "Chart Room — Four Panels, One Truth",
        "description": "chart-room (1995 architecture) ported to a Quilt sheet. The single TruthCell feeds all four panels.",
        "source": "https://github.com/SuperInstance/chart-room",
        "tags": ["chart-room", "multi-panel", "3-views", "vessel", "telemetry"],
        "cells": cells,
        "metadata": {
            "sampled_at": datetime.now(timezone.utc).isoformat(),
            "n_samples": n_samples,
            "duration_s": duration_s,
            "panels": ["nav", "eng", "tac", "son"],
        },
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description="chart-room → Quilt bridge")
    p.add_argument("--out", default="/tmp/chart-room-quilt.json")
    p.add_argument("--duration-min", type=float, default=30)
    p.add_argument("--dt-s", type=float, default=60)
    args = p.parse_args()

    sheet = chart_room_to_quilt(args.duration_min * 60, args.dt_s)
    out = args.out if args.out.endswith(".qzt") else args.out + ".qzt"
    with open(out, "w") as f:
        json.dump(sheet, f, indent=2)

    print(f"Chart Room → Quilt bridge")
    print(f"  Source: chart-room (four-panels-one-truth)")
    print(f"  Output: {out}")
    print(f"  Cells: {len(sheet['cells'])}")
    print(f"  Panels: nav, eng, tac, son (all read from truth.now)")
    print(f"  Timeline tracks: 4 (one per panel)")


if __name__ == "__main__":
    main()
