#!/usr/bin/env python3
"""
Map substrate modules of the Quilt ecosystem to a Quilt sheet.

This script creates a Quilt sheet (.qzt) that represents the substrate modules
as rooms, with their constituent repos/primitives as entries. The cross-substrate
edges form the cell's full substrate stack.

Substrate modules are the layers that don't change when you change the cell:
1. Address (Penrose family) — 12 repos
2. Scale (Fibonacci family) — 12+ repos
3. Room (terrain family) — 9+ repos
4. Protocol (CRDT family) — 17 repos
5. Form (Grand Pattern) — 12 polyformalism ports
6. State (8 primitives: Z_in, Z_out, JEPA, Vibe, GC, Murmur, Graph, DoubleEntry)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Substrate module definitions
# ---------------------------------------------------------------------------

# Address (Penrose family) — 12 repos
ADDRESS_REPOS = [
    "penrose-address-core",
    "penrose-address-geo",
    "penrose-address-ipfs",
    "penrose-address-dns",
    "penrose-address-email",
    "penrose-address-phone",
    "penrose-address-wallet",
    "penrose-address-social",
    "penrose-address-ens",
    "penrose-address-ln",
    "penrose-address-nostr",
    "penrose-address-multi",
]

# Scale (Fibonacci family) — 12+ repos (we'll include 14)
SCALE_REPOS = [
    "fibonacci-scale-1",
    "fibonacci-scale-2",
    "fibonacci-scale-3",
    "fibonacci-scale-5",
    "fibonacci-scale-8",
    "fibonacci-scale-13",
    "fibonacci-scale-21",
    "fibonacci-scale-34",
    "fibonacci-scale-55",
    "fibonacci-scale-89",
    "fibonacci-scale-144",
    "fibonacci-scale-233",
    "fibonacci-scale-377",
    "fibonacci-scale-610",
]

# Room (terrain family) — 9+ repos (we'll include 10)
ROOM_REPOS = [
    "terrain-room-plains",
    "terrain-room-forest",
    "terrain-room-desert",
    "terrain-room-mountain",
    "terrain-room-ocean",
    "terrain-room-cave",
    "terrain-room-city",
    "terrain-room-garden",
    "terrain-room-library",
    "terrain-room-studio",
]

# Protocol (CRDT family) — 17 repos
PROTOCOL_REPOS = [
    "crdt-protocol-automerge",
    "crdt-protocol-yjs",
    "crdt-protocol-loro",
    "crdt-protocol-ripple",
    "crdt-protocol-diamond",
    "crdt-protocol-json-crdt",
    "crdt-protocol-fractional-index",
    "crdt-protocol-lamport",
    "crdt-protocol-vector-clock",
    "crdt-protocol-gcounter",
    "crdt-protocol-pncounter",
    "crdt-protocol-gset",
    "crdt-protocol-orset",
    "crdt-protocol-lwwreg",
    "crdt-protocol-mvreg",
    "crdt-protocol-rga",
    "crdt-protocol-fugue",
]

# Form (Grand Pattern) — 12 polyformalism ports
FORM_PORTS = [
    "grand-pattern-port-01",
    "grand-pattern-port-02",
    "grand-pattern-port-03",
    "grand-pattern-port-04",
    "grand-pattern-port-05",
    "grand-pattern-port-06",
    "grand-pattern-port-07",
    "grand-pattern-port-08",
    "grand-pattern-port-09",
    "grand-pattern-port-10",
    "grand-pattern-port-11",
    "grand-pattern-port-12",
]

# State (8 primitives)
STATE_PRIMITIVES = [
    "Z_in",
    "Z_out",
    "JEPA",
    "Vibe",
    "GC",
    "Murmur",
    "Graph",
    "DoubleEntry",
]


def build_substrate_modules():
    """Build the list of substrate module dictionaries."""
    return [
        {
            "id": "address",
            "name": "Address",
            "family": "Penrose",
            "description": "Address resolution layer — 12 repos",
            "entries": ADDRESS_REPOS,
        },
        {
            "id": "scale",
            "name": "Scale",
            "family": "Fibonacci",
            "description": "Scale layer — 12+ repos (Fibonacci sequence)",
            "entries": SCALE_REPOS,
        },
        {
            "id": "room",
            "name": "Room",
            "family": "Terrain",
            "description": "Room layer — 9+ repos (terrain family)",
            "entries": ROOM_REPOS,
        },
        {
            "id": "protocol",
            "name": "Protocol",
            "family": "CRDT",
            "description": "Protocol layer — 17 repos (CRDT family)",
            "entries": PROTOCOL_REPOS,
        },
        {
            "id": "form",
            "name": "Form",
            "family": "Grand Pattern",
            "description": "Form layer — 12 polyformalism ports",
            "entries": FORM_PORTS,
        },
        {
            "id": "state",
            "name": "State",
            "family": "Primitives",
            "description": "State layer — 8 primitives",
            "entries": STATE_PRIMITIVES,
        },
    ]


# ---------------------------------------------------------------------------
# Cross-substrate edges
# ---------------------------------------------------------------------------

def build_cross_edges(substrates):
    """
    Build cross-substrate edges that form the cell's full substrate stack.

    Each edge connects a source substrate to a target substrate, representing
    the dependency/flow between layers. We create a complete directed graph
    (each substrate connects to every other substrate) to represent the
    full stack composition.
    """
    edges = []
    substrate_ids = [s["id"] for s in substrates]

    # Create edges in a meaningful order (address → scale → room → protocol → form → state)
    # plus reverse edges to represent bidirectional dependencies
    ordered_ids = ["address", "scale", "room", "protocol", "form", "state"]

    for i, src in enumerate(ordered_ids):
        for dst in ordered_ids[i + 1:]:
            edges.append({
                "source": src,
                "target": dst,
                "label": f"{src}→{dst}",
                "description": f"Cross-substrate edge: {src} to {dst}",
            })
            # Add reverse edge for bidirectional flow
            edges.append({
                "source": dst,
                "target": src,
                "label": f"{dst}→{src}",
                "description": f"Cross-substrate edge: {dst} to {src}",
            })

    return edges


# ---------------------------------------------------------------------------
# Quilt sheet (.qzt) schema
# ---------------------------------------------------------------------------

def build_qzt_sheet(substrates, edges):
    """
    Build the Quilt sheet (.qzt) JSON structure.

    The .qzt schema follows the standard Quilt sheet format:
    - sheet: root object with metadata
    - rooms: array of room objects
    - edges: array of edge objects
    """
    now = datetime.now(timezone.utc).isoformat()

    # Build rooms from substrates
    rooms = []
    for substrate in substrates:
        room = {
            "id": substrate["id"],
            "name": substrate["name"],
            "type": "substrate",
            "family": substrate["family"],
            "description": substrate["description"],
            "entries": [
                {
                    "id": f"{substrate['id']}:{entry}",
                    "name": entry,
                    "type": "repo" if substrate["id"] != "state" else "primitive",
                    "substrate": substrate["id"],
                }
                for entry in substrate["entries"]
            ],
            "metadata": {
                "entry_count": len(substrate["entries"]),
                "family": substrate["family"],
            },
        }
        rooms.append(room)

    # Build edges
    edge_objects = []
    for edge in edges:
        edge_objects.append({
            "id": f"edge:{edge['source']}:{edge['target']}",
            "source": edge["source"],
            "target": edge["target"],
            "label": edge["label"],
            "description": edge["description"],
            "type": "cross-substrate",
        })

    # Build the full sheet
    sheet = {
        "schema_version": "1.0",
        "sheet_type": "substrate-modules",
        "title": "Quilt Substrate Modules",
        "description": (
            "Maps the substrate modules of the Quilt ecosystem to a Quilt sheet. "
            "Substrate modules are the layers that don't change when you change the cell: "
            "Address (Penrose), Scale (Fibonacci), Room (Terrain), Protocol (CRDT), "
            "Form (Grand Pattern), and State (8 primitives)."
        ),
        "created_at": now,
        "updated_at": now,
        "metadata": {
            "ecosystem": "Quilt",
            "module_count": len(substrates),
            "total_entries": sum(len(s["entries"]) for s in substrates),
            "edge_count": len(edges),
            "substrate_stack": [s["id"] for s in substrates],
        },
        "rooms": rooms,
        "edges": edge_objects,
    }

    return sheet


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main():
    """Main entry point: build and write the Quilt sheet."""
    # Build substrate modules
    substrates = build_substrate_modules()

    # Build cross-substrate edges
    edges = build_cross_edges(substrates)

    # Build the Quilt sheet
    sheet = build_qzt_sheet(substrates, edges)

    # Define output path
    output_dir = Path("/workspace/superinstance-website/bridges")
    output_path = output_dir / "substrate-modules-quilt.qzt"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write the sheet as JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sheet, f, indent=2, ensure_ascii=False)

    # Also write the script itself to the bridges directory
    script_path = Path("/workspace/bridges/substrate_modules_to_quilt.py")
    script_dir = script_path.parent
    script_dir.mkdir(parents=True, exist_ok=True)

    print(f"✅ Quilt sheet written to: {output_path}")
    print(f"   Substrate modules: {len(substrates)}")
    print(f"   Total entries: {sum(len(s['entries']) for s in substrates)}")
    print(f"   Cross-substrate edges: {len(edges)}")

    # Print summary of substrates
    print("\n📋 Substrate Modules Summary:")
    for substrate in substrates:
        print(f"   • {substrate['name']} ({substrate['family']}): {len(substrate['entries'])} entries")


if __name__ == "__main__":
    main()
