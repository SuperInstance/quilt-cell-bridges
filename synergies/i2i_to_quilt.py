"""
I2I (Iron-to-Iron) Bottle ↔ Quilt Cell Bridge

The SuperInstance fleet uses I2I bottles as its inter-agent protocol.
Quilt uses cells. This bridge makes them wire-compatible.

A bottle IS a cell. A cell IS a bottle.

The I2I bottle format (from a2a-adapter):
{
  "from": "edge-agent",
  "to": "cloud-agent",
  "subject": "ask: status check",
  "body": "What is the current system load?",
  "vessel": "primary",  # the routing context
  "priority": "normal",
  "timestamp": "2026-08-22T00:00:00Z",
  "id": "msg-uuid-001",
  "parent": "msg-uuid-000",  # for threading
  "metadata": {
    "intent": "query",
    "confidence": 0.95,
    "tags": ["status", "monitoring"]
  }
}

The Quilt cell format:
{
  "id": "msg-uuid-001",
  "kind": "string",
  "value": "What is the current system load?",
  "subject": "ask: status check",
  "from": "edge-agent",
  "to": "cloud-agent",
  "vessel": "primary",
  "parent": "msg-uuid-000",
  "room": "monitoring",
  "vibe": 0.95,  # confidence
  "gamma": 0.5,  # influence
  "metadata": {
    "intent": "query",
    "priority": "normal",
    "tags": ["status", "monitoring"],
    "timestamp": "2026-08-22T00:00:00Z"
  }
}

The mapping:
- bottle.body → cell.value
- bottle.subject → cell.subject (formula could evaluate it)
- bottle.from → cell.from (Z_in source)
- bottle.to → cell.to (Z_out target)
- bottle.vessel → cell.room
- bottle.parent → cell.parent (creates a thread edge)
- bottle.metadata.confidence → cell.vibe
- bottle.metadata.tags → cell.room tags
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional


def bottle_to_cell(bottle: Dict) -> Dict:
    """Convert an I2I bottle to a Quilt cell."""
    cell = {
        "id": bottle.get("id", str(uuid.uuid4())),
        "kind": "string",
        "value": bottle.get("body", ""),
        "subject": bottle.get("subject", ""),
        "from": bottle.get("from", "unknown"),
        "to": bottle.get("to", "unknown"),
        "vessel": bottle.get("vessel", "default"),
        "room": bottle.get("vessel", "default"),
        "vibe": bottle.get("metadata", {}).get("confidence", 0.5),
        "gamma": 0.5,  # default
        "metadata": {
            "intent": bottle.get("metadata", {}).get("intent", ""),
            "priority": bottle.get("priority", "normal"),
            "tags": bottle.get("metadata", {}).get("tags", []),
            "timestamp": bottle.get("timestamp", datetime.utcnow().isoformat() + "Z"),
        }
    }
    if "parent" in bottle:
        cell["parent"] = bottle["parent"]
    return cell


def cell_to_bottle(cell: Dict) -> Dict:
    """Convert a Quilt cell back to an I2I bottle."""
    bottle = {
        "id": cell.get("id", str(uuid.uuid4())),
        "from": cell.get("from", "unknown"),
        "to": cell.get("to", "unknown"),
        "subject": cell.get("subject", ""),
        "body": cell.get("value", ""),
        "vessel": cell.get("vessel", cell.get("room", "default")),
        "priority": cell.get("metadata", {}).get("priority", "normal"),
        "timestamp": cell.get("metadata", {}).get("timestamp", datetime.utcnow().isoformat() + "Z"),
        "metadata": {
            "intent": cell.get("metadata", {}).get("intent", ""),
            "confidence": cell.get("vibe", 0.5),
            "tags": cell.get("metadata", {}).get("tags", []),
        }
    }
    if "parent" in cell:
        bottle["parent"] = cell["parent"]
    return bottle


def cells_to_fleet_sheet(cells: List[Dict], name: str = "fleet") -> Dict:
    """
    Convert a list of I2I bottles (as cells) into a Quilt sheet.
    
    Creates a sheet with:
    - One cell per bottle
    - Edges between cells based on parent/child threading
    - Rooms based on vessel
    """
    # Group by room
    rooms = {}
    for cell in cells:
        room = cell.get("room", "default")
        rooms.setdefault(room, []).append(cell)
    
    # Build edges
    edges = []
    for cell in cells:
        if "parent" in cell:
            edges.append({
                "from": cell["parent"],
                "to": cell["id"],
                "kind": "thread",
            })
        # Cross-room edges (e.g., from→to different vessels)
        if cell.get("from") and cell.get("to"):
            edges.append({
                "from": cell["id"],
                "to": cell["to"],
                "kind": "intent",
            })
    
    return {
        "name": name,
        "version": "0.1.0",
        "kind": "fleet-sheet",
        "rooms": list(rooms.keys()),
        "cells": cells,
        "edges": edges,
        "metadata": {
            "source": "i2i",
            "created": datetime.utcnow().isoformat() + "Z",
            "count": len(cells),
        }
    }


def i2i_message_to_quilt_agent(message: Dict, agent_name: str = "watchman") -> Dict:
    """
    Convert an I2I message into a Quilt agent.
    
    The agent is a "watchman" that subscribes to cells matching
    certain patterns (e.g., vessel=monitoring, intent=query).
    """
    return {
        "name": agent_name,
        "kind": "watchman",
        "subscribes_to": [
            f"vessel:{message.get('vessel', 'default')}",
            f"intent:{message.get('metadata', {}).get('intent', 'any')}",
        ],
        "ratio": {
            "explore": 0.3,
            "exploit": 0.5,
            "prior": 0.2,
        },
        "mode": "watcher",
        "signal_dim": 16,
        "metadata": {
            "source": "i2i",
            "message_id": message.get("id", ""),
        }
    }


# Demonstration
if __name__ == "__main__":
    # Sample I2I bottle
    bottle = {
        "id": "msg-001",
        "from": "edge-agent",
        "to": "cloud-agent",
        "subject": "ask: status check",
        "body": "What is the current system load?",
        "vessel": "monitoring",
        "priority": "normal",
        "timestamp": "2026-08-22T00:00:00Z",
        "parent": "msg-000",
        "metadata": {
            "intent": "query",
            "confidence": 0.95,
            "tags": ["status", "monitoring"]
        }
    }
    
    # Convert
    cell = bottle_to_cell(bottle)
    print("BOTTLE → CELL:")
    print(json.dumps(cell, indent=2))
    
    # Round-trip
    bottle2 = cell_to_bottle(cell)
    print("\nCELL → BOTTLE (round-trip):")
    print(json.dumps(bottle2, indent=2))
    
    # Sheet
    sheet = cells_to_fleet_sheet([cell, bottle_to_cell({
        "id": "msg-002",
        "from": "cloud-agent",
        "to": "edge-agent",
        "subject": "reply: status check",
        "body": "Load is 23%",
        "vessel": "monitoring",
        "parent": "msg-001",
        "metadata": {"intent": "respond", "confidence": 0.99, "tags": ["status"]}
    })])
    print("\nFLEET SHEET:")
    print(json.dumps(sheet, indent=2))
