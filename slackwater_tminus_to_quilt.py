#!/usr/bin/env python3
"""
slackwater_tminus_to_quilt.py — Port slackwater-tminus to a Quilt sheet.

slackwater-tminus is "Time-shaped coordination primitives for swarm-anchor:
predict-and-confirm, deadlines, BPM clocks, cron." It's a temporal coordination
system — perfect as a Quilt SIDE view (timeline).

This bridge models the t-minus coordination protocol as a cell graph where:
  - DeadlineCell emits a signal at time T
  - CronCell emits a signal at intervals
  - BPMSyncCell synchronizes multiple cells to a tempo
  - SwarmAnchorCell is the shared state
  - ConfirmCell confirms that a deadline was met

Author: Mavis
Date: 2026-08-20
"""
import json
import math
from datetime import datetime, timezone, timedelta


def slackwater_tminus_to_quilt(
    duration_s: float = 3600.0,
    bpm: float = 60.0,
) -> dict:
    """
    Build a Quilt sheet from slackwater-tminus coordination primitives.

    Cell regions:
      - clock.*       — the master clock (BPM)
      - deadline.*    — T-minus deadlines
      - cron.*        — repeating triggers
      - swarm.*       — swarm state
      - confirm.*     — confirm cells
      - tracks.*      — agent tracks on the timeline
    """
    cells = []
    beat_period = 60.0 / bpm  # seconds per beat
    n_beats = int(duration_s / beat_period) + 1

    # Master clock
    cells.append({"path": "clock.bpm", "kind": "value", "value": bpm})
    cells.append({"path": "clock.period_s", "kind": "value", "value": beat_period})
    cells.append({"path": "clock.start", "kind": "value", "value": datetime.now(timezone.utc).isoformat()})

    # Beat cells — one per beat in the duration
    beats = []
    for i in range(n_beats):
        t = i * beat_period
        beats.append({
            "time": round(t, 3),
            "beat": i,
            "phase": (i % 4),  # 4/4 time
            "measure": i // 4,
        })
    cells.append({"path": "clock.beats", "kind": "value", "value": beats})

    # Deadline cells — T-minus countdowns
    deadlines = [
        {"id": "deploy_window", "deadline_at_s": 600, "name": "Deploy window opens", "owner": "platform"},
        {"id": "fish_set_complete", "deadline_at_s": 1200, "name": "Fish set complete", "owner": "deckhand"},
        {"id": "course_correction", "deadline_at_s": 1800, "name": "Course correction due", "owner": "nav"},
        {"id": "shift_change", "deadline_at_s": 2400, "name": "Shift change", "owner": "crew"},
        {"id": "lunch", "deadline_at_s": 3000, "name": "Lunch", "owner": "cook"},
    ]
    for dl in deadlines:
        cells.append({"path": f"deadline.{dl['id']}.name", "kind": "value", "value": dl["name"]})
        cells.append({"path": f"deadline.{dl['id']}.at_s", "kind": "value", "value": dl["deadline_at_s"]})
        cells.append({"path": f"deadline.{dl['id']}.owner", "kind": "value", "value": dl["owner"]})
        cells.append({"path": f"deadline.{dl['id']}.remaining_s", "kind": "program",
                      "value": f"at_s - clock.now"})
        cells.append({"path": f"deadline.{dl['id']}.fired", "kind": "value", "value": False})

    # Cron cells — repeating triggers
    crons = [
        {"id": "heartbeat", "period_s": 30, "name": "Agent heartbeat"},
        {"id": "metrics", "period_s": 300, "name": "Metrics collection"},
        {"id": "log_rotate", "period_s": 900, "name": "Log rotation"},
    ]
    for cr in crons:
        cells.append({"path": f"cron.{cr['id']}.period_s", "kind": "value", "value": cr["period_s"]})
        cells.append({"path": f"cron.{cr['id']}.name", "kind": "value", "value": cr["name"]})
        cells.append({"path": f"cron.{cr['id']}.fired_count", "kind": "value", "value": 0})

    # Swarm state cells
    cells.append({"path": "swarm.anchor.version", "kind": "value", "value": 1})
    cells.append({"path": "swarm.anchor.last_write", "kind": "value", "value": None})
    cells.append({"path": "swarm.agents", "kind": "value", "value": ["nav", "eng", "deck", "cook"]})

    # Confirm cells (predict-and-confirm protocol)
    confirms = [
        {"id": "depth_safety", "predicted_at_s": 120, "actual_at_s": 125},
        {"id": "course_safe", "predicted_at_s": 480, "actual_at_s": 478},
        {"id": "fuel_sufficient", "predicted_at_s": 720, "actual_at_s": 725},
        {"id": "crew_fresh", "predicted_at_s": 1500, "actual_at_s": 1505},
    ]
    for cf in confirms:
        cells.append({"path": f"confirm.{cf['id']}.predicted_s", "kind": "value", "value": cf["predicted_at_s"]})
        cells.append({"path": f"confirm.{cf['id']}.actual_s", "kind": "value", "value": cf["actual_at_s"]})
        cells.append({"path": f"confirm.{cf['id']}.drift_ms", "kind": "program",
                      "value": "(actual_s - predicted_s) * 1000"})

    # Tracks — one per agent (for the side view DAW)
    tracks = []
    for agent in ["nav", "eng", "deck", "cook"]:
        # Generate 3-5 events per agent
        n_ev = 3 + (hash(agent) % 3)
        events = []
        for j in range(n_ev):
            t = (j + 1) * (duration_s / (n_ev + 1))
            events.append({
                "time": round(t, 1),
                "duration": round(beat_period * 2, 1),
                "kind": ["commit", "report", "ack", "alert", "info"][j % 5],
                "text": f"{agent} event {j+1} at t={t:.0f}s",
            })
        tracks.append({
            "name": agent,
            "character": agent,
            "voice": ["deep", "warm", "neutral", "bright"][["nav", "eng", "deck", "cook"].index(agent)],
            "events": events,
        })

    cells.append({"path": "tracks", "kind": "value", "value": tracks})

    return {
        "format": "quilt-z/1.0",
        "name": f"Slackwater T-Minus — {bpm} BPM Coordination",
        "description": "slackwater-tminus ported to a Quilt sheet. Time-shaped coordination as cells: deadlines, cron, BPM sync, predict-and-confirm.",
        "source": "https://github.com/SuperInstance/slackwater-tminus",
        "tags": ["temporal", "side-view", "coordination", "slackwater", "tminus"],
        "cells": cells,
        "tracks": tracks,
        "metadata": {
            "sampled_at": datetime.now(timezone.utc).isoformat(),
            "duration_s": duration_s,
            "bpm": bpm,
            "n_beats": n_beats,
        },
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description="slackwater-tminus → Quilt bridge")
    p.add_argument("--out", default="/tmp/slackwater-tminus-quilt.json")
    p.add_argument("--duration-min", type=float, default=60)
    p.add_argument("--bpm", type=float, default=60)
    args = p.parse_args()

    sheet = slackwater_tminus_to_quilt(args.duration_min * 60, args.bpm)
    out = args.out if args.out.endswith(".qzt") else args.out + ".qzt"
    with open(out, "w") as f:
        json.dump(sheet, f, indent=2)

    print(f"slackwater-tminus → Quilt bridge")
    print(f"  Source: slackwater-tminus (temporal coordination)")
    print(f"  Output: {out}")
    print(f"  Cells: {len(sheet['cells'])}")
    print(f"  BPM: {args.bpm}, beats: {sheet['metadata']['n_beats']}")
    print(f"  Tracks: {len(tracks := sheet['tracks'])}")
    for t in tracks:
        print(f"    - {t['name']}: {len(t['events'])} events")


if __name__ == "__main__":
    main()
