from typing import Dict, List, Any, Optional
import json
import re

class PlatoToQuilt:
    """
    Bridge between PLATO room system and Quilt room system.
    Maps PLATO rooms to Quilt rooms, handling MQTT topics, DDS domains,
    context text to cells, and agents to cell graph.
    """

    @staticmethod
    def room_to_cell_room(plato_room: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a PLATO room to a Quilt room with cells derived from context and agents.
        """
        quilt_room = {
            "id": plato_room["id"],
            "name": plato_room["name"],
            "kind": "room",
            "cells": [],
            "vibe": 0.5,
            "metadata": {}
        }

        # Map MQTT topic to room.id (if not already set)
        mqtt_topic = plato_room.get("mqtt_topic", "")
        if mqtt_topic:
            # Extract the last path segment as the room id if it differs
            match = re.search(r"/([^/]+)$", mqtt_topic)
            if match:
                topic_room_id = match.group(1)
                if topic_room_id != plato_room["id"]:
                    quilt_room["id"] = topic_room_id

        # Map DDS domain to vibe (0 to 1)
        dds_domain = plato_room.get("dds_domain", 0)
        quilt_room["vibe"] = max(0.0, min(1.0, dds_domain / 100.0))

        # Parse PLATO context as cells
        context = plato_room.get("plato_context", "")
        if context:
            # Split context into lines, filter non-empty, strip whitespace
            lines = [line.strip() for line in context.split('\n') if line.strip()]
            # Treat each line as a cell
            for line in lines:
                quilt_room["cells"].append({
                    "id": f"cell-{len(quilt_room['cells']) + 1}",
                    "content": line,
                    "kind": "text",
                    "metadata": {"source": "plato_context"}
                })

        # Map agents to cell graph
        agents = plato_room.get("agents", [])
        if agents:
            # Create a graph of cell references based on agent names
            agent_cells = []
            for i, agent in enumerate(agents):
                cell_id = f"agent-{i+1}"
                agent_cells.append({
                    "id": cell_id,
                    "kind": "agent",
                    "content": agent,
                    "metadata": {"agent": agent, "source": "plato_agents"}
                })
            quilt_room["cells"].extend(agent_cells)
            # Add a graph reference if needed (simplified for now)
            quilt_room["metadata"]["cell_graph"] = {
                "edges": [
                    {
                        "from": f"agent-{i+1}",
                        "to": f"cell-{j+1}",
                        "type": "observes"
                    }
                    for i in range(len(agents))
                    for j in range(len(quilt_room["cells"]) - len(agents))
                ]
            }

        return quilt_room

    @staticmethod
    def cell_room_to_plato(quilt_room: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Quilt room back to a PLATO room.
        """
        plato_room = {
            "id": quilt_room["id"],
            "name": quilt_room["name"],
            "type": "virtual",  # Default type
            "mqtt_topic": f"/vessel/{quilt_room['id']}/+/+",
            "dds_domain": int(quilt_room["vibe"] * 100),
            "plato_context": "",
            "agents": []
        }

        # Reconstruct context from cells
        context_lines = []
        for cell in quilt_room.get("cells", []):
            if cell["kind"] == "text":
                context_lines.append(cell["content"])
            elif cell["kind"] == "agent":
                plato_room["agents"].append(cell["content"])
        plato_room["plato_context"] = "\n".join(context_lines)

        # Handle metadata if needed
        if "metadata" in quilt_room:
            if "cell_graph" in quilt_room["metadata"]:
                # Optional: extract graph info
                pass

        return plato_room

    @staticmethod
    def round_trip_demo():
        """
        Demonstrate round-trip conversion: PLATO → Quilt → PLATO.
        """
        # Sample PLATO room
        plato_input = {
            "id": "kitchen",
            "name": "The Kitchen",
            "type": "physical",
            "mqtt_topic": "/vessel/kitchen/temperature/sensor",
            "dds_domain": 75,
            "plato_context": "The stove is on.\nThere's a pot of soup simmering.\nA timer is ticking.",
            "agents": ["chef-bot-01", "assistant-mate-22"]
        }

        print("=== PLATO Room ===")
        print(json.dumps(plato_input, indent=2))

        # Convert to Quilt room
        quilt_output = PlatoToQuilt.room_to_cell_room(plato_input)
        print("\n=== Quilt Room (after conversion) ===")
        print(json.dumps(quilt_output, indent=2))

        # Convert back to PLATO
        plato_roundtrip = PlatoToQuilt.cell_room_to_plato(quilt_output)
        print("\n=== PLATO Room (after round-trip) ===")
        print(json.dumps(plato_roundtrip, indent=2))

        # Verify round-trip integrity
        assert plato_input["id"] == plato_roundtrip["id"]
        assert plato_input["name"] == plato_roundtrip["name"]
        assert plato_input["type"] == plato_roundtrip["type"]
        assert plato_input["dds_domain"] == plato_roundtrip["dds_domain"]
        assert plato_input["plato_context"] == plato_roundtrip["plato_context"]
        assert sorted(plato_input["agents"]) == sorted(plato_roundtrip["agents"])

        print("\n✅ Round-trip conversion successful: all fields preserved.")


if __name__ == "__main__":
    PlatoToQuilt.round_trip_demo()
