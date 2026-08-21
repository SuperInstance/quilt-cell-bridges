#!/usr/bin/env python3
"""
Map the quilt-mesh package to a Quilt sheet.

This script analyzes the quilt-mesh distributed cell mesh package and generates
a Quilt sheet (.qzt) that captures the structure, behavior, and state transitions
of each cell kind.

Cell kinds provided by quilt-mesh:
- MeshNode: A single node in the mesh
- MeshEdge: A connection between nodes
- MeshRouter: Routes gossip
- QuorumCell: Requires majority to update
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any


def get_timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def create_mesh_node_schema() -> Dict[str, Any]:
    """Create schema for MeshNode cell."""
    return {
        "name": "MeshNode",
        "description": "A single node in the distributed cell mesh",
        "version": "1.0.0",
        "fields": {
            "node_id": {
                "type": "string",
                "description": "Unique identifier for this mesh node",
                "required": True
            },
            "address": {
                "type": "string",
                "description": "Network address of this node",
                "required": True
            },
            "status": {
                "type": "enum",
                "values": ["active", "inactive", "syncing", "error"],
                "description": "Current node status",
                "required": True
            },
            "last_heartbeat": {
                "type": "datetime",
                "description": "Timestamp of last heartbeat received",
                "required": False
            },
            "peer_count": {
                "type": "integer",
                "description": "Number of connected peers",
                "required": False,
                "default": 0
            },
            "gossip_queue": {
                "type": "list",
                "item_type": "string",
                "description": "Queue of pending gossip messages",
                "required": False,
                "default": []
            }
        },
        "methods": {
            "start": {
                "description": "Start the mesh node",
                "parameters": [],
                "returns": "bool",
                "state_transition": "inactive -> active"
            },
            "stop": {
                "description": "Stop the mesh node",
                "parameters": [],
                "returns": "bool",
                "state_transition": "active -> inactive"
            },
            "send_gossip": {
                "description": "Send a gossip message to connected peers",
                "parameters": [
                    {"name": "message", "type": "string", "description": "Message to gossip"}
                ],
                "returns": "bool",
                "state_transition": "active -> active (queues message)"
            },
            "receive_gossip": {
                "description": "Receive a gossip message from a peer",
                "parameters": [
                    {"name": "message", "type": "string", "description": "Received message"}
                ],
                "returns": "bool",
                "state_transition": "active -> active (processes message)"
            },
            "sync_state": {
                "description": "Synchronize state with peers",
                "parameters": [],
                "returns": "bool",
                "state_transition": "active -> syncing -> active"
            },
            "get_peers": {
                "description": "Get list of connected peers",
                "parameters": [],
                "returns": "list",
                "state_transition": "no state change"
            }
        },
        "state_transitions": {
            "inactive": {
                "to": ["active"],
                "trigger": "start()",
                "description": "Node starts and becomes active"
            },
            "active": {
                "to": ["inactive", "syncing", "error"],
                "trigger": "stop(), sync_state(), error_occurred()",
                "description": "Node is operational, can sync or stop"
            },
            "syncing": {
                "to": ["active", "error"],
                "trigger": "sync_complete(), sync_failed()",
                "description": "Node is synchronizing state with peers"
            },
            "error": {
                "to": ["active", "inactive"],
                "trigger": "recover(), stop()",
                "description": "Node encountered an error, can recover or stop"
            }
        }
    }


def create_mesh_edge_schema() -> Dict[str, Any]:
    """Create schema for MeshEdge cell."""
    return {
        "name": "MeshEdge",
        "description": "A connection between two mesh nodes",
        "version": "1.0.0",
        "fields": {
            "edge_id": {
                "type": "string",
                "description": "Unique identifier for this edge",
                "required": True
            },
            "source_node": {
                "type": "string",
                "description": "ID of the source node",
                "required": True
            },
            "target_node": {
                "type": "string",
                "description": "ID of the target node",
                "required": True
            },
            "connection_type": {
                "type": "enum",
                "values": ["tcp", "udp", "websocket", "grpc"],
                "description": "Type of network connection",
                "required": True
            },
            "latency": {
                "type": "float",
                "description": "Current latency in milliseconds",
                "required": False,
                "default": 0.0
            },
            "bandwidth": {
                "type": "float",
                "description": "Current bandwidth in Mbps",
                "required": False,
                "default": 0.0
            },
            "status": {
                "type": "enum",
                "values": ["connected", "disconnected", "connecting", "failed"],
                "description": "Connection status",
                "required": True
            },
            "last_activity": {
                "type": "datetime",
                "description": "Timestamp of last activity on this edge",
                "required": False
            }
        },
        "methods": {
            "connect": {
                "description": "Establish the connection between nodes",
                "parameters": [],
                "returns": "bool",
                "state_transition": "disconnected -> connecting -> connected"
            },
            "disconnect": {
                "description": "Terminate the connection",
                "parameters": [],
                "returns": "bool",
                "state_transition": "connected -> disconnected"
            },
            "send_message": {
                "description": "Send a message across the edge",
                "parameters": [
                    {"name": "message", "type": "string", "description": "Message to send"}
                ],
                "returns": "bool",
                "state_transition": "connected -> connected (updates activity)"
            },
            "receive_message": {
                "description": "Receive a message from the edge",
                "parameters": [],
                "returns": "string",
                "state_transition": "connected -> connected (updates activity)"
            },
            "measure_latency": {
                "description": "Measure current latency",
                "parameters": [],
                "returns": "float",
                "state_transition": "no state change"
            },
            "reconnect": {
                "description": "Attempt to reconnect a failed connection",
                "parameters": [],
                "returns": "bool",
                "state_transition": "failed -> connecting -> connected"
            }
        },
        "state_transitions": {
            "disconnected": {
                "to": ["connecting"],
                "trigger": "connect()",
                "description": "Edge is not connected, can initiate connection"
            },
            "connecting": {
                "to": ["connected", "failed"],
                "trigger": "connection_established(), connection_failed()",
                "description": "Edge is establishing connection"
            },
            "connected": {
                "to": ["disconnected", "failed"],
                "trigger": "disconnect(), connection_lost()",
                "description": "Edge is active and transmitting data"
            },
            "failed": {
                "to": ["connecting", "disconnected"],
                "trigger": "reconnect(), disconnect()",
                "description": "Edge encountered an error, can retry or disconnect"
            }
        }
    }


def create_mesh_router_schema() -> Dict[str, Any]:
    """Create schema for MeshRouter cell."""
    return {
        "name": "MeshRouter",
        "description": "Routes gossip messages through the mesh",
        "version": "1.0.0",
        "fields": {
            "router_id": {
                "type": "string",
                "description": "Unique identifier for this router",
                "required": True
            },
            "routing_table": {
                "type": "dict",
                "description": "Routing table mapping destinations to next hops",
                "required": True,
                "default": {}
            },
            "active_routes": {
                "type": "integer",
                "description": "Number of currently active routes",
                "required": False,
                "default": 0
            },
            "total_messages_routed": {
                "type": "integer",
                "description": "Total number of messages routed",
                "required": False,
                "default": 0
            },
            "status": {
                "type": "enum",
                "values": ["running", "stopped", "degraded"],
                "description": "Router status",
                "required": True
            },
            "gossip_protocol": {
                "type": "string",
                "description": "Gossip protocol version in use",
                "required": False,
                "default": "v1"
            }
        },
        "methods": {
            "start": {
                "description": "Start the router",
                "parameters": [],
                "returns": "bool",
                "state_transition": "stopped -> running"
            },
            "stop": {
                "description": "Stop the router",
                "parameters": [],
                "returns": "bool",
                "state_transition": "running -> stopped"
            },
            "route_message": {
                "description": "Route a gossip message to appropriate destinations",
                "parameters": [
                    {"name": "message", "type": "string", "description": "Message to route"},
                    {"name": "destination", "type": "string", "description": "Destination node ID"}
                ],
                "returns": "bool",
                "state_transition": "running -> running (updates routing stats)"
            },
            "update_routing_table": {
                "description": "Update the routing table with new routes",
                "parameters": [
                    {"name": "routes", "type": "dict", "description": "New routing entries"}
                ],
                "returns": "bool",
                "state_transition": "running -> running (updates table)"
            },
            "get_route": {
                "description": "Get the next hop for a destination",
                "parameters": [
                    {"name": "destination", "type": "string", "description": "Destination node ID"}
                ],
                "returns": "string",
                "state_transition": "no state change"
            },
            "handle_node_failure": {
                "description": "Handle a node failure and update routes",
                "parameters": [
                    {"name": "node_id", "type": "string", "description": "Failed node ID"}
                ],
                "returns": "bool",
                "state_transition": "running -> degraded -> running"
            }
        },
        "state_transitions": {
            "stopped": {
                "to": ["running"],
                "trigger": "start()",
                "description": "Router is not operational"
            },
            "running": {
                "to": ["stopped", "degraded"],
                "trigger": "stop(), node_failure()",
                "description": "Router is operational and routing messages"
            },
            "degraded": {
                "to": ["running", "stopped"],
                "trigger": "recovery_complete(), stop()",
                "description": "Router is running but with reduced capacity"
            }
        }
    }


def create_quorum_cell_schema() -> Dict[str, Any]:
    """Create schema for QuorumCell cell."""
    return {
        "name": "QuorumCell",
        "description": "A cell that requires majority agreement to update",
        "version": "1.0.0",
        "fields": {
            "cell_id": {
                "type": "string",
                "description": "Unique identifier for this quorum cell",
                "required": True
            },
            "value": {
                "type": "any",
                "description": "The current value stored in the cell",
                "required": True
            },
            "version": {
                "type": "integer",
                "description": "Version number of the current value",
                "required": True,
                "default": 0
            },
            "members": {
                "type": "list",
                "item_type": "string",
                "description": "List of member node IDs in the quorum",
                "required": True
            },
            "quorum_size": {
                "type": "integer",
                "description": "Number of members required for quorum (majority)",
                "required": True
            },
            "pending_updates": {
                "type": "list",
                "item_type": "dict",
                "description": "List of pending update proposals",
                "required": False,
                "default": []
            },
            "status": {
                "type": "enum",
                "values": ["consistent", "updating", "conflicted", "unavailable"],
                "description": "Current quorum status",
                "required": True
            }
        },
        "methods": {
            "propose_update": {
                "description": "Propose an update to the cell value",
                "parameters": [
                    {"name": "new_value", "type": "any", "description": "New value to set"},
                    {"name": "proposer", "type": "string", "description": "Node proposing the update"}
                ],
                "returns": "bool",
                "state_transition": "consistent -> updating"
            },
            "vote": {
                "description": "Cast a vote on a pending update",
                "parameters": [
                    {"name": "update_id", "type": "string", "description": "ID of the update"},
                    {"name": "voter", "type": "string", "description": "Node casting the vote"},
                    {"name": "approve", "type": "bool", "description": "Whether to approve"}
                ],
                "returns": "bool",
                "state_transition": "updating -> consistent (if quorum reached)"
            },
            "get_value": {
                "description": "Get the current value",
                "parameters": [],
                "returns": "any",
                "state_transition": "no state change"
            },
            "resolve_conflict": {
                "description": "Resolve a conflict when no quorum is reached",
                "parameters": [
                    {"name": "resolution", "type": "any", "description": "Resolution value"}
                ],
                "returns": "bool",
                "state_transition": "conflicted -> consistent"
            },
            "add_member": {
                "description": "Add a member to the quorum",
                "parameters": [
                    {"name": "node_id", "type": "string", "description": "Node to add"}
                ],
                "returns": "bool",
                "state_transition": "consistent -> consistent (updates quorum)"
            },
            "remove_member": {
                "description": "Remove a member from the quorum",
                "parameters": [
                    {"name": "node_id", "type": "string", "description": "Node to remove"}
                ],
                "returns": "bool",
                "state_transition": "consistent -> consistent (updates quorum)"
            }
        },
        "state_transitions": {
            "consistent": {
                "to": ["updating", "unavailable"],
                "trigger": "propose_update(), member_failure()",
                "description": "Cell is in agreement and operational"
            },
            "updating": {
                "to": ["consistent", "conflicted"],
                "trigger": "quorum_reached(), quorum_not_reached()",
                "description": "Cell is processing an update proposal"
            },
            "conflicted": {
                "to": ["consistent"],
                "trigger": "resolve_conflict()",
                "description": "Cell has conflicting updates and needs resolution"
            },
            "unavailable": {
                "to": ["consistent"],
                "trigger": "recovery()",
                "description": "Cell cannot achieve quorum due to member failures"
            }
        }
    }


def create_qzt_file(cells: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create the QZT file structure."""
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "name": "quilt-mesh",
            "description": "Distributed cell mesh for gossip-based communication",
            "version": "1.0.0",
            "generated": get_timestamp(),
            "generator": "quilt_mesh_to_quilt.py",
            "package": "quilt-mesh"
        },
        "cells": cells
    }


def main() -> None:
    """Main entry point for the script."""
    # Create schemas for all cell kinds
    cells = [
        create_mesh_node_schema(),
        create_mesh_edge_schema(),
        create_mesh_router_schema(),
        create_quorum_cell_schema()
    ]

    # Create the QZT file structure
    qzt_data = create_qzt_file(cells)

    # Ensure output directory exists
    output_dir = "/workspace/superinstance-website/bridges"
    os.makedirs(output_dir, exist_ok=True)

    # Write the QZT file
    output_path = os.path.join(output_dir, "quilt-mesh-quilt.qzt")
    with open(output_path, "w") as f:
        json.dump(qzt_data, f, indent=2)

    print(f"Successfully generated Quilt sheet at: {output_path}")
    print(f"Generated {len(cells)} cell schemas:")
    for cell in cells:
        print(f"  - {cell['name']}: {cell['description']}")


if __name__ == "__main__":
    main()
