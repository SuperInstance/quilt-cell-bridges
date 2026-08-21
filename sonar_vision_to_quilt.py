#!/usr/bin/env python3
"""
sonar_vision_to_quilt.py — Convert the sonar-vision project to a Quilt sheet.

The sonar-vision project is a pure-Python library for:
  - Active sonar simulation (ping → propagation → echo)
  - Signal processing (sine, chirp, noise, filters, FFT)
  - Object tracking (multi-target gating, velocity)
  - Spatial mapping (occupancy grid)
  - ASCII rendering (radar sweeps, occupancy maps)

The Quilt IDE for sonar-vision: a vertical column of depth cells, each
holding a camera and a slice of the sounder feed. ML trains on the daisy
chain. STT supervises. Triggers fire on events. Confidence progresses.

This bridge creates a Quilt sheet that represents the sonar-vision
pipeline as cells: each ping → propagation → echo → detection → track
→ map is a cell. Each component is a cell. The whole library is a sheet.
"""

import json
import time
import math
from pathlib import Path

# ============================================================================
# Sonar Vision components
# ============================================================================
PIPELINE = [
    # The 5-stage pipeline
    {"id": "ping", "name": "Ping (emit)", "kind": "emit", "icon": "📡",
     "description": "Active sonar ping — emits acoustic signal"},
    {"id": "propagation", "name": "Propagation", "kind": "physics", "icon": "🌊",
     "description": "Two-way transmission loss: spreading + absorption"},
    {"id": "echo", "name": "Echo (return)", "kind": "physics", "icon": "🪞",
     "description": "Acoustic echo returns with target strength"},
    {"id": "detection", "name": "Detection", "kind": "process", "icon": "👁",
     "description": "SNR threshold — extract detections from echo"},
    {"id": "tracker", "name": "ObjectTracker", "kind": "process", "icon": "🎯",
     "description": "Multi-target gating, velocity estimation"},
    {"id": "map", "name": "SpatialMap", "kind": "storage", "icon": "🗺",
     "description": "Occupancy grid from sonar returns"},
]

COMPONENTS = [
    # Sonar
    {"id": "Sonar", "name": "Sonar", "kind": "class", "icon": "📡",
     "methods": ["ping", "ping_return_signal", "round_trip_time",
                 "spreading_loss", "absorption_loss", "total_loss",
                 "in_beam", "beam_coverage"]},
    # Signal
    {"id": "Signal", "name": "Signal", "kind": "class", "icon": "📈",
     "methods": ["sine", "chirp", "noise", "lowpass", "highpass",
                 "bandpass", "fft", "energy", "envelope"]},
    # ObjectTracker
    {"id": "ObjectTracker", "name": "ObjectTracker", "kind": "class", "icon": "🎯",
     "methods": ["update", "predict", "track"]},
    # SpatialMap
    {"id": "SpatialMap", "name": "SpatialMap", "kind": "class", "icon": "🗺",
     "methods": ["add_obstacle", "set_cell", "get_cell",
                 "mark_free_ray", "ray_cast", "occupancy_count", "coverage"]},
    # SonarDisplay
    {"id": "SonarDisplay", "name": "SonarDisplay", "kind": "class", "icon": "🖥",
     "methods": ["radar_sweep", "occupancy_map", "tracker_overlay"]},
]

# The Quilt IDE extension: the cannonball + cameras
CANNONBALL = [
    {"id": "cell-0", "depth": 0, "color": "#58a6ff", "name": "Surface cell"},
    {"id": "cell-5", "depth": 5, "color": "#39c5cf", "name": "Shallow cell"},
    {"id": "cell-10", "depth": 10, "color": "#3fb950", "name": "Mid cell"},
    {"id": "cell-15", "depth": 15, "color": "#a371f7", "name": "Deep cell"},
    {"id": "cell-20", "depth": 20, "color": "#f0883e", "name": "Deeper cell"},
    {"id": "cell-25", "depth": 25, "color": "#f85149", "name": "Bottom cell"},
]

CAMERAS = [
    {"id": "cam-1", "name": "GoPro 12 Black", "specs": "5.3K · 240fps · low-light"},
    {"id": "cam-2", "name": "Sony A7S III", "specs": "4K · 120fps · full-frame"},
    {"id": "cam-3", "name": "Insta360 X4", "specs": "5.7K · 360° · waterproof"},
    {"id": "cam-4", "name": "Olympus TG-7", "specs": "4K · macro · 15m depth"},
    {"id": "cam-5", "name": "Nikon Z9", "specs": "8K · 120fps · flagship"},
    {"id": "cam-6", "name": "Garmin VIRB", "specs": "4K · rugged · action"},
]

# The 3 confidence tiers
TIERS = [
    {"id": 1, "name": "trigger review on everything",
     "description": "Low confidence — every event is flagged for human review"},
    {"id": 2, "name": "trigger review with predicted answer",
     "description": "Medium confidence — ML prediction shown alongside review request"},
    {"id": 3, "name": "review only the unusual few",
     "description": "High confidence — only low-confidence events surface to human"},
]

SPECIES = ["cod", "haddock", "pollock", "halibut", "flounder", "lumpfish", "shark", "mackerel"]


def build_sheet():
    cells = []
    edges = []
    rooms = []

    # 1. Pipeline cells (the 5 stages)
    for i, p in enumerate(PIPELINE):
        cells.append({
            "address": f"pipeline.{p['id']}.name",
            "kind": "string",
            "value": p['name'],
        })
        cells.append({
            "address": f"pipeline.{p['id']}.description",
            "kind": "string",
            "value": p['description'],
        })
    # Pipeline edges
    for i in range(len(PIPELINE) - 1):
        edges.append({
            "from": f"pipeline.{PIPELINE[i]['id']}",
            "to": f"pipeline.{PIPELINE[i + 1]['id']}",
            "kind": "flows_to",
        })

    # 2. Component cells (the classes)
    for c in COMPONENTS:
        cells.append({
            "address": f"component.{c['id']}.name",
            "kind": "string",
            "value": c['name'],
        })
        cells.append({
            "address": f"component.{c['id']}.n_methods",
            "kind": "usize",
            "value": len(c['methods']),
        })
        for j, m in enumerate(c['methods']):
            cells.append({
                "address": f"component.{c['id']}.method[{j}]",
                "kind": "string",
                "value": m,
            })
    # Component → pipeline mapping
    edges.append({"from": "component.Sonar", "to": "pipeline.ping", "kind": "implements"})
    edges.append({"from": "component.Sonar", "to": "pipeline.propagation", "kind": "implements"})
    edges.append({"from": "component.Sonar", "to": "pipeline.echo", "kind": "implements"})
    edges.append({"from": "component.Signal", "to": "pipeline.echo", "kind": "filters"})
    edges.append({"from": "component.ObjectTracker", "to": "pipeline.tracker", "kind": "implements"})
    edges.append({"from": "component.SpatialMap", "to": "pipeline.map", "kind": "implements"})
    edges.append({"from": "component.SonarDisplay", "to": "pipeline.map", "kind": "renders"})

    # 3. The cannonball (depth cells)
    for cell in CANNONBALL:
        cells.append({
            "address": f"cannonball.{cell['id']}.depth",
            "kind": "f64",
            "value": cell['depth'],
        })
        cells.append({
            "address": f"cannonball.{cell['id']}.name",
            "kind": "string",
            "value": cell['name'],
        })
    # Connect cannonball to pipeline
    for cell in CANNONBALL:
        edges.append({
            "from": f"cannonball.{cell['id']}",
            "to": "pipeline.detection",
            "kind": "feeds",
        })

    # 4. Cameras
    for cam in CAMERAS:
        for dim in ["name", "specs"]:
            cells.append({
                "address": f"camera.{cam['id']}.{dim}",
                "kind": "string",
                "value": cam[dim],
            })

    # 5. Confidence tiers
    for t in TIERS:
        cells.append({
            "address": f"tier.{t['id']}.name",
            "kind": "string",
            "value": t['name'],
        })
        cells.append({
            "address": f"tier.{t['id']}.description",
            "kind": "string",
            "value": t['description'],
        })

    # 6. Species (for predictions)
    for i, s in enumerate(SPECIES):
        cells.append({
            "address": f"species.{i}",
            "kind": "string",
            "value": s,
        })

    # 7. Stats
    stats = [
        ("pipeline_stages", len(PIPELINE)),
        ("components", len(COMPONENTS)),
        ("cannonball_cells", len(CANNONBALL)),
        ("cameras", len(CAMERAS)),
        ("tiers", len(TIERS)),
        ("species", len(SPECIES)),
        ("total_methods", sum(len(c['methods']) for c in COMPONENTS)),
        ("polyformalism_ports", 12),  # the Quilt patterns
        ("now", time.time()),
    ]
    for name, val in stats:
        cells.append({
            "address": f"stats.{name}",
            "kind": "f64" if isinstance(val, float) else "usize",
            "value": val,
        })

    # 8. Rooms
    rooms = [
        {"id": "pipeline", "name": "📡 Sonar pipeline (5 stages)", "cell_count": len(PIPELINE) * 2},
        {"id": "component", "name": "🧩 Components (5 classes)", "cell_count": sum(2 + len(c['methods']) for c in COMPONENTS)},
        {"id": "cannonball", "name": "⚓ The cannonball (6 depth cells)", "cell_count": len(CANNONBALL) * 2},
        {"id": "camera", "name": "📷 Cameras (6)", "cell_count": len(CAMERAS) * 2},
        {"id": "tier", "name": "📊 Confidence tiers (3)", "cell_count": len(TIERS) * 2},
        {"id": "species", "name": "🐟 Species (8)", "cell_count": len(SPECIES)},
    ]

    return {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "Sonar-Vision as Quilt sheet",
            "description": (
                "The sonar-vision project (pure-Python active sonar simulation, signal "
                "processing, multi-object tracking, spatial mapping) ported to Quilt. The "
                "5-stage pipeline is a cell chain. The components are cells. The cannonball "
                "is a vertical column of depth cells. The cameras are draggable assets. The "
                "ML training uses the camera daisy chain as supervised data. The STT input "
                "is human supervision. The confidence tiers progress from trigger-everything "
                "to trigger-only-unusual. This is what the Quilt IDE for sonar-vision looks like."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "sonarvision",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "pipeline_stages": len(PIPELINE),
            "components": len(COMPONENTS),
            "cannonball_cells": len(CANNONBALL),
            "cameras": len(CAMERAS),
        },
    }


def main():
    sheet = build_sheet()
    out_path = Path("/workspace/superinstance-website/bridges/sonar-vision-quilt.qzt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(sheet, f, indent=2)
    print(f"✓ Wrote {out_path}")
    s = sheet["stats"]
    print(f"  pipeline: {s['pipeline_stages']} stages")
    print(f"  components: {s['components']}")
    print(f"  cannonball: {s['cannonball_cells']} cells")
    print(f"  cameras: {s['cameras']}")
    print(f"  total: {s['total_cells']} cells, {s['total_edges']} edges")


if __name__ == "__main__":
    main()
