#!/usr/bin/env python3
"""
elephant_to_quilt.py — Bridge the elephant repo to Quilt.

The elephant IS the Room substrate made real. This bridge maps:
- 21 elephant modules → Quilt substrate layers
- 9 dials → 8 Quilt primitives + 1 meta-primitive
- RoomField (warmth, κ, distance) → conservation law (γ, η, JEPA surprise)
- Room-Elephant + Personal-Elephant → watch oscillation (universal ↔ particular)
- Spaces (MUD, chat, X, sensor) → openers
- TapNightSession → classroom pattern
- BoatHarness → cell runtime

Key insight from the brainstorm: γ = warmth, η = κ. The conservation law
gets a thermometer. The dials are sensory inverses of the primitives.
"""
import json
from pathlib import Path

# The 21 elephant modules
ELEPHANT_MODULES = [
    ("__init__", "Package entry — re-exports Message, Room, RoomField, acclimation_curve, charisma_pull", "io"),
    ("room", "Room / Message — rooms as message streams with gravity, reverberation, ripple, density", "room"),
    ("dial", "Dial (abstract JEPA sense) + DialBank (the perceiving ensemble, one scalar per dimension)", "protocol"),
    ("field", "RoomField — temperature vector: warmth, κ, distance, sauna_plunge_gap", "room"),
    ("dials/__init__", "DEFAULT_DIALS — the eight-dial bank that ships out of the box", "protocol"),
    ("dials/mood", "MoodDial — warm/cold valence, [-1 cold, +1 warm]", "protocol"),
    ("dials/volume", "VolumeDial — how loud the room is talking, [0 quiet, 1 shouting]", "protocol"),
    ("dials/earnestness", "EarnestnessDial — how much the room means it, [0 ironic, 1 sincere]", "protocol"),
    ("dials/cynicism", "CynicismDial — how much the room is rolling its eyes, [0 earnest, 1 sneering]", "protocol"),
    ("dials/joke_landing", "JokeLandingDial — collective laugh or boo, [-1 booed, +1 roared]", "protocol"),
    ("dials/panic", "PanicDial — stampede sense (fire in the room), [0 calm, 1 trampling]", "protocol"),
    ("dials/presence", "PresenceDial — pheromone trace of who's been here, [0 empty, 1 thrumming]", "protocol"),
    ("dials/model_vs_code", "ModelVsCodeDial — who's generating the room's signal, [-1 code, +1 model]", "protocol"),
    ("dials/vision", "VisionDial — room's visual energy from camera frames (plato 16-dim room state)", "protocol"),
    ("sensors", "SignalRoom / SensorFrame + sea-leg dials: RadarCoherence, SounderBiomass, FishingDay", "room"),
    ("nudge", "nudge_prior() / apply_nudge() — dial numbers become an attention prior", "protocol"),
    ("fleetmath", "Numeric spine: three_reading_kinematics, fleet_concentration (vMF κ), biomass_anchor", "scale"),
    ("harness", "BoatHarness — one boat, one place to plug every sense in; rolling rooms, merged field", "form"),
    ("tapnight", "TapNightSession / Participant — after-work reading room with peer-relative self-tuning", "form"),
    ("presets", "RoomElephant / PersonalElephant / PRESETS — zeitgeist vs personal feel", "state"),
    ("mud", "tint_description() — the room's description mutated by its field", "room"),
    ("space", "Space protocol + MudSpace / ChatSpace / SensorSpace + AdapterRegistry", "address"),
    ("jepa", "Optional learned backbone hook (EMA + stop-gradient + VICReg)", "form"),
]

# The 9 dials and their Quilt primitive mapping
DIAL_TO_PRIMITIVE = {
    "mood": ("Sense", "Z_in — read the room's current state. Mood is what you sense first."),
    "volume": ("Radiate", "Z_out — emit signal into room. Volume is the strength of your radiate."),
    "earnestness": ("Acclimate", "JEPA — adapt cell temperature to room. Earnestness is how you accommodate."),
    "cynicism": ("Oscillate", "Vibe — switch universal ↔ particular. Cynicism is the watch's pull to particularity."),
    "joke_landing": ("Bond", "Murmur — form connection across cells. Joke landing is the gossip bus firing."),
    "panic": ("Gap", "JEPA surprise — measure distance between rooms. Panic is the surprise spike."),
    "presence": ("Dial", "Observe — measure one axis via JEPA. Presence is the dial reading."),
    "model_vs_code": ("Form", "Form — what shape is the cell. Model vs code is whether the form maps or makes."),
    "vision": ("Watch", "Graph — the meta-primitive. Vision watches the other 8 dials."),
}

# The 6 spaces
SPACES = [
    ("MudSpace", "MUD room (The Tap, other MUDs) — room events + NPC chatter → messages", "MUD"),
    ("ChatSpace", "Chatroom / messenger / X thread — authors, reactions, reply trees", "chat"),
    ("SensorSpace", "Sensor array (radar, sounder, nav) — SensorFrames → SignalRoom", "sensor"),
    ("AgentSpace", "Agent channel / human+bot / email / docs", "agent"),
    ("DocSpace", "Documentation / wiki / static content", "doc"),
    ("AsyncSpace", "Async messaging (email, future letters)", "async"),
]

# New Quilt cell kinds (from the brainstorm)
NEW_CELL_KINDS = [
    ("ElephantCell", "The resident organ of a room. One per room. Runs the DialBank under Room-Elephant preset."),
    ("StewardCell", "The nudge prior made agentive. Reads the field and intervenes when panic spikes."),
    ("MigratoryCell", "Lives on the plunge gradient. Carries Personal-Elephant as luggage."),
    ("ReadingCell", "TapNight participant. Peer-relative self-tuning against the cast."),
    ("EchoCell", "Tends reverberation decay. Decides which echoes fade and which persist."),
]

# Conservation law: γ = warmth, η = κ
CONSERVATION = {
    "γ_warmth": "Coupling/Generative — how much the room pulls you in",
    "η_kappa": "Entropy/Concentration — how focused or scattered the room is",
    "biomass_anchor": "The room's total energy is conserved: γ × η = biomass_anchor",
    "JEPA_surprise_sauna_plunge": "||φ(s_room1) - φ(s_room2)||² — log-surprise between rooms",
}


def make_module_cell(name, description, substrate):
    """Create a cell for an elephant module."""
    return {
        "id": f"elephant_{name.replace('/', '_').replace('__', '_')}",
        "kind": "cell",
        "form": {"name": name.split("/")[-1].replace(".py", "").replace("_", " ").title().replace(" ", "")},
        "description": description,
        "module": name,
        "substrate_layer": substrate,
        "primitives": ["Spawn", "Observe", "Mutate"],
        "z_in": {"input": "module input"},
        "z_out": {"output": "module output"},
        "jepa": {"predict": "module behavior", "observe": "actual behavior"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "import_module", "args": [], "returns": "Module"},
            {"name": "call", "args": ["Any"], "returns": "Any"},
        ],
        "substrate": {
            "address": f"/elephant/{name}",
            "scale": 0,
            "room": "ElephantRoom",
            "protocol": "Python",
            "form": name,
            "state": "active"
        },
        "tags": ["elephant", "module", substrate, "quilt-bridge"]
    }


def make_dial_cell(name, primitive, description, idx):
    """Create a cell for one of the 9 dials."""
    return {
        "id": f"dial_{name}",
        "kind": "cell",
        "form": {"name": name.title().replace("_", "") + "Dial"},
        "description": description,
        "dial_name": name,
        "quilt_primitive": primitive,
        "primitives": ["Spawn", "Observe", "Observe", "Observe", "Mutate"],
        "z_in": {"input": "room messages / sensor frames"},
        "z_out": {"output": f"{name} reading", "range": "see description"},
        "jepa": {"predict": f"dial value", "observe": "actual value"},
        "double_entry": {"gamma": 0.3, "eta": 0.7},  # Dials are η-dominant (observers)
        "vibe": {"position": idx, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "sensing"},
        "murmur": {"gossip_to": ["DialBank"], "gossip_from": []},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "read", "args": ["Room"], "returns": "float"},
            {"name": "train", "args": ["List<Room>"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/elephant/dial/{name}",
            "scale": 0,
            "room": "DialBank",
            "protocol": "JEPA",
            "form": name + "_dial",
            "state": "ready"
        },
        "tags": ["elephant", "dial", name, primitive.lower()]
    }


def make_space_cell(name, description, kind):
    """Create a cell for a Space adapter."""
    return {
        "id": f"space_{name.lower()}",
        "kind": "cell",
        "form": {"name": name},
        "description": description,
        "space_kind": kind,
        "primitives": ["Spawn", "Receive", "Send", "Receive", "Send"],
        "z_in": {"input": f"{kind} events"},
        "z_out": {"output": "normalized Room/SignalRoom"},
        "jepa": {"predict": "room structure", "observe": "actual structure"},
        "double_entry": {"gamma": 0.6, "eta": 0.4},  # Spaces are γ-dominant (generators)
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "adapting"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "ingest", "args": ["Any"], "returns": "Room"},
            {"name": "tint_target", "args": [], "returns": "Target"},
            {"name": "send_back", "args": ["Field"], "returns": "Unit"},
        ],
        "substrate": {
            "address": f"/elephant/space/{kind}",
            "scale": 1,
            "room": "SpaceAdapter",
            "protocol": kind,
            "form": name,
            "state": "ready"
        },
        "tags": ["elephant", "space", "opener", kind]
    }


def make_new_cell_kind(name, description):
    """Create a cell for a new Quilt cell kind that elephant introduces."""
    return {
        "id": f"newkind_{name.lower()}",
        "kind": "cell",
        "form": {"name": name},
        "description": description,
        "new_cell_kind": True,
        "primitives": ["Spawn", "Observe", "Mutate", "Send", "Receive"],
        "z_in": {"input": "room field"},
        "z_out": {"output": "cell action"},
        "jepa": {"predict": "field will change", "observe": "field changes"},
        "double_entry": {"gamma": 0.5, "eta": 0.5},
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "active"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "act", "args": [], "returns": "State"},
        ],
        "substrate": {
            "address": f"/quilt/cellkind/{name.lower()}",
            "scale": 1,
            "room": "QuiltRoom",
            "protocol": "Cell",
            "form": name,
            "state": "ready"
        },
        "tags": ["elephant", "new-cell-kind", "quilt-extension"]
    }


def make_meta_cells():
    """Meta cells that describe the bridge and the conservation law mapping."""
    return [
        {
            "id": "elephant_meta",
            "kind": "cell",
            "form": {"name": "ElephantMeta"},
            "description": "The elephant IS the Room substrate made real. 21 modules, 9 dials, 6 spaces, 5 new cell kinds. The 9 dials map to 8 Quilt primitives + 1 meta-primitive (vision). The RoomField (warmth, κ, distance) is the conservation law (γ, η, JEPA surprise) made measurable.",
            "primitives": ["Observe"] * 9,
            "z_in": {"repo": "SuperInstance/elephant", "modules": 21, "dials": 9, "spaces": 6},
            "z_out": {"proof": "Room substrate becomes real"},
            "jepa": {"predict": "elephant = quilt room", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
            "gc": {"phase": "eternal"},
            "murmur": {},
            "graph": {},
            "openers": [
                {"name": "list_modules", "args": [], "returns": "List<Cell>"},
                {"name": "list_dials", "args": [], "returns": "List<Cell>"},
                {"name": "list_spaces", "args": [], "returns": "List<Cell>"},
            ],
            "tags": ["meta", "elephant-bridge"]
        },
        {
            "id": "conservation_gauge_cell",
            "kind": "cell",
            "form": {"name": "ConservationGauge"},
            "description": "The elephant is the gauge of the conservation law. γ = warmth read out. η = κ read out. The RoomField's warmth × κ = biomass_anchor is the room's total energy, conserved across rooms.",
            "primitives": ["Observe", "Observe", "Observe", "Observe"],
            "z_in": {"law": "γ + η = budget", "instrument": "RoomField"},
            "z_out": {"warmth": "γ readout", "kappa": "η readout", "biomass": "γ × η = anchor"},
            "jepa": {"predict": "conservation holds", "verified": True},
            "double_entry": {"gamma": 0.5, "eta": 0.5},
            "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
            "gc": {"phase": "gauging"},
            "murmur": {},
            "graph": {},
            "tags": ["meta", "conservation", "elephant"]
        },
        {
            "id": "watch_oscillation_cell",
            "kind": "cell",
            "form": {"name": "WatchOscillation"},
            "description": "Room-Elephant (universal, objective) ↔ Personal-Elephant (particular, subjective). Acclimation pulls particular to universal. Charisma pushes universal toward particular. The watch oscillates because rooms have inhabitants with attachments.",
            "primitives": ["Observe", "Mutate", "Observe", "Mutate", "Observe", "Mutate"],
            "z_in": {"universal": "RoomField (objective)", "particular": "PersonalField (subjective)"},
            "z_out": {"oscillation": "watch tick", "rate": "acclimation vs charisma"},
            "tags": ["meta", "watch", "oscillation", "elephant"]
        },
        {
            "id": "elephant_sphere_cell",
            "kind": "cell",
            "form": {"name": "ElephantSphere"},
            "description": "The 9-dial readings (normalized) are a point on S⁸. A room's field is a vMF distribution: μ is direction, κ is concentration. distance() is geodesic on the sphere. sauna_plunge_gap is log-surprise. Cross-room routing has geometry.",
            "primitives": ["Observe", "Mutate", "Observe", "Mutate", "Observe"],
            "z_in": {"dial_readings": 9, "ambient": "S⁸ sphere"},
            "z_out": {"distance_metric": "geodesic on S⁸", "routing": "by distance"},
            "tags": ["meta", "geometry", "elephant"]
        }
    ]


def make_edges(cells):
    """Make edges connecting related concepts."""
    edges = []
    
    # Module -> substrate layer edges
    for c in cells:
        if c["id"].startswith("elephant_") and "substrate_layer" in c:
            edges.append({
                "from": c["id"],
                "to": f"layer_{c['substrate_layer']}",
                "kind": "substrate-membership",
                "weight": 1.0
            })
    
    # Dial -> primitive edges
    for c in cells:
        if c["id"].startswith("dial_") and "quilt_primitive" in c:
            edges.append({
                "from": c["id"],
                "to": f"primitive_{c['quilt_primitive'].lower()}",
                "kind": "primitive-inverse",
                "weight": 0.9
            })
    
    # Dials gossip to DialBank
    for c in cells:
        if c["id"].startswith("dial_"):
            edges.append({
                "from": c["id"],
                "to": "elephant_dial",
                "kind": "dial-bank-membership",
                "weight": 0.5
            })
    
    # All meta cells point to the meta
    for c in cells:
        if c["id"].endswith("_meta") and c["id"] != "elephant_meta":
            edges.append({
                "from": c["id"],
                "to": "elephant_meta",
                "kind": "meta-aggregation",
                "weight": 1.0
            })
    
    return edges


def build_qzt():
    cells = []
    
    # 21 module cells
    for name, desc, substrate in ELEPHANT_MODULES:
        cells.append(make_module_cell(name, desc, substrate))
    
    # 9 dial cells
    for idx, (name, (primitive, desc)) in enumerate(DIAL_TO_PRIMITIVE.items()):
        cells.append(make_dial_cell(name, primitive, desc, idx))
    
    # 6 space cells
    for name, desc, kind in SPACES:
        cells.append(make_space_cell(name, desc, kind))
    
    # 5 new cell kind cells
    for name, desc in NEW_CELL_KINDS:
        cells.append(make_new_cell_kind(name, desc))
    
    # Meta cells
    cells.extend(make_meta_cells())
    
    edges = make_edges(cells)
    
    return {
        "version": "1.0",
        "kind": "quilt-zip-target",
        "name": "elephant-to-quilt",
        "description": "Bridge mapping the SuperInstance/elephant repo to Quilt. The elephant IS the Room substrate made real. 21 modules, 9 dials, 6 spaces, 5 new cell kinds. The conservation law gets a thermometer.",
        "cells": cells,
        "edges": edges,
        "external_refs": [
            {"kind": "github-repo", "name": "elephant", "org": "SuperInstance"},
            {"kind": "github-folder", "name": "elephant/elephant", "filter": "*.py"}
        ],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "modules": len(ELEPHANT_MODULES),
            "dials": len(DIAL_TO_PRIMITIVE),
            "spaces": len(SPACES),
            "new_cell_kinds": len(NEW_CELL_KINDS),
            "conservation_mapping": CONSERVATION,
        },
        "tags": ["elephant", "room-substrate", "conservation", "watch-oscillation", "quilt-bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/elephant_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}")
    print(f"  Total cells: {qzt['stats']['total_cells']}")
    print(f"  Total edges: {qzt['stats']['total_edges']}")
    print(f"  Modules: {qzt['stats']['modules']}")
    print(f"  Dials: {qzt['stats']['dials']}")
    print(f"  Spaces: {qzt['stats']['spaces']}")
    print(f"  New cell kinds: {qzt['stats']['new_cell_kinds']}")


if __name__ == "__main__":
    main()
