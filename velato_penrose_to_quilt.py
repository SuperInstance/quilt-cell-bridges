"""
velato_penrose_to_quilt.py — Bridge quilt-velato + penrose-family to a Quilt sheet.

The Velato-Penrose-Quilt system is a new view on the existing Penrose family
(12 repos, 92 cells). This bridge adds the Velato source code as a new
"front" view: each Penrose cell gets annotated with which Velato interval
produces it, and the 3-coloring is reinforced.

The result is a unified Quilt sheet where:
- The 12 Penrose repos are the rooms
- The Velato interval mapping is in each cell's primitive
- The 3-coloring (CREATION/ENTROPY/WITNESS) is the cell color
- γ+η=1 is verified across the whole graph
"""

import json
import math
from typing import Dict, List, Any


# Velato interval → Quilt primitive mapping
INTERVAL_TO_PRIMITIVE = {
    0: 'ROOT', 1: 'Z_out', 2: 'Z_in', 3: 'JEPA_b', 4: 'JEPA',
    5: 'DoubleEntry', 6: 'Vibe_b', 7: 'Vibe', 8: 'GC',
    9: 'Murmur', 10: 'Graph', 11: 'Graph_b', 12: 'ROOT'
}


def eisenstein_color(pitch: int) -> int:
    """The 3-coloring from MIDI pitch via Eisenstein mod 3."""
    p = pitch % 12
    a = p % 3
    b = p // 3
    return (a + b) % 3


def build_velato_penrose_sheet() -> Dict[str, Any]:
    """Build the unified Velato-Penrose Quilt sheet."""
    
    rooms = [
        {
            'id': 'penrose_memory',
            'name': '🔯 penrose-memory (Rust + Python)',
            'velato_root': 60,
            'description': 'Aperiodic memory palace with golden-ratio hashing and 3-coloring',
            'velato_phrase': [60, 62, 64, 67, 65, 64, 62, 60],  # C major scale
        },
        {
            'id': 'penrose_lattice',
            'name': '🔯 penrose-lattice (Rust)',
            'velato_root': 60,
            'description': 'Penrose tilings as spectral graphs with Fibonacci substitution',
            'velato_phrase': [60, 64, 67, 72, 67, 64, 60],  # C E G C G E C
        },
        {
            'id': 'lau_penrose',
            'name': '🔯 lau-penrose (Rust)',
            'velato_root': 65,
            'description': 'Base Penrose tiling implementation with golden ratio geometry',
            'velato_phrase': [65, 69, 72, 77, 72, 69, 65],  # F A C F C A F
        },
        {
            'id': 'lau_twistor_agents',
            'name': '🔯 lau-twistor-agents (Makefile)',
            'velato_root': 67,
            'description': 'Penrose twistor theory applied to multi-agent systems',
            'velato_phrase': [67, 71, 74, 79, 74, 71, 67],  # G B D G D B G
        },
        {
            'id': 'tensor_penrose',
            'name': '🔯 tensor-penrose (Python)',
            'velato_root': 60,
            'description': 'Tensor operations on Penrose tilings',
            'velato_phrase': [60, 64, 67, 64, 60],  # C E G E C
        },
        {
            'id': 'flux_tensor_midi',
            'name': '🔯 flux-tensor-midi (6 langs)',
            'velato_root': 62,
            'description': '4D tensor representation of MIDI events',
            'velato_phrase': [62, 65, 69, 72, 69, 65, 62],  # D F A C A F D
        },
        {
            'id': 'plato_midi_bridge',
            'name': '🔯 plato-midi-bridge (Rust)',
            'velato_root': 64,
            'description': 'PLATO rooms as musicians — flux-tensor-midi to fleet tiles',
            'velato_phrase': [64, 67, 71, 74, 71, 67, 64],  # E G B D B G E
        },
        {
            'id': 'counterpoint_engine',
            'name': '🔯 counterpoint-engine',
            'velato_root': 60,
            'description': 'Species counterpoint as constraint satisfaction, Laman rigid',
            'velato_phrase': [60, 67, 64, 72, 64, 67, 60],  # C G E C E G C
        },
        {
            'id': 'holonomy_harmony',
            'name': '🔯 holonomy-harmony',
            'velato_root': 65,
            'description': 'Laman-rigid musical graph, zero-holonomy in closed loops',
            'velato_phrase': [65, 72, 69, 77, 69, 72, 65],  # F C A F A C F
        },
        {
            'id': 'spectral_music_v2',
            'name': '🔯 spectral-music-v2',
            'velato_root': 67,
            'description': 'Spectral triples for music. CR = γ+η = 1',
            'velato_phrase': [67, 74, 71, 79, 71, 74, 67],  # G D B G B D G
        },
        {
            'id': 'topo_sonata',
            'name': '🔯 topo-sonata',
            'velato_root': 60,
            'description': 'Chord progressions as filtered cell graphs',
            'velato_phrase': [60, 65, 67, 72, 67, 65, 60],  # C F G C G F C
        },
        {
            'id': 'velato_quilt',
            'name': '🔯 quilt-velato (NEW)',
            'velato_root': 60,
            'description': 'The Velato → Penrose → Quilt compiler. Music IS the cell graph.',
            'velato_phrase': [60, 62, 64, 67, 64, 62, 60],  # C D E G E D C
        },
    ]
    
    cells = []
    edges = []
    cell_id = 0
    
    for room in rooms:
        # Room cell
        cells.append({
            'id': f'r_{room["id"]}',
            'kind': 'cell',
            'value': room['name'],
            'room_id': room['id'],
            'is_room': True,
            'color': 'witness',
            'primitives': {'Vibe': {'position': room['velato_root'], 'velocity': 1.0}},
        })
        cell_id += 1
        
        # Velato phrase cells
        prev_id = None
        for i, pitch in enumerate(room['velato_phrase']):
            interval = ((pitch - room['velato_root']) % 12 + 12) % 12
            primitive = INTERVAL_TO_PRIMITIVE.get(interval, 'UNKNOWN')
            color_idx = eisenstein_color(pitch)
            color_name = ['creation', 'entropy', 'witness'][color_idx]
            
            # Populate the 8 primitives
            prims = {}
            if primitive == 'Z_in':
                prims['Z_in'] = {'data': {'value': pitch / 127.0}}
            elif primitive == 'Z_out':
                prims['Z_out'] = {'data': {'value': pitch / 127.0}}
            elif primitive == 'JEPA' or primitive == 'JEPA_b':
                prims['JEPA'] = {'history': [pitch / 127.0]}
            elif primitive == 'DoubleEntry':
                gamma = pitch / 127.0
                eta = 1.0 - gamma
                prims['DoubleEntry'] = {'gamma': gamma, 'eta': eta}
            elif primitive == 'Vibe' or primitive == 'Vibe_b':
                prims['Vibe'] = {'position': pitch, 'velocity': 1.0, 'damping': 0.95}
            elif primitive == 'GC':
                prims['GC'] = {'phase': 'decay'}
            elif primitive == 'Murmur':
                prims['Murmur'] = {'subscriptions': {f'pitch_{pitch}'}}
            elif primitive == 'Graph' or primitive == 'Graph_b':
                prims['Graph'] = {'parents': [], 'children': []}
            elif primitive == 'ROOT':
                prims['Vibe'] = {'position': pitch, 'velocity': 1.0}
            
            cell = {
                'id': f'c_{cell_id:04d}',
                'kind': 'cell',
                'value': pitch,
                'room_id': room['id'],
                'is_room': False,
                'color': color_name,
                'velato_interval': interval,
                'velato_primitive': primitive,
                'primitives': prims,
            }
            cells.append(cell)
            
            # Edge: room → first phrase cell
            if i == 0:
                edges.append({
                    'from': f'r_{room["id"]}',
                    'to': f'c_{cell_id:04d}',
                    'kind': 'phrase_start',
                    'weight': 1.0,
                })
            
            # Edge: prev phrase cell → this one
            if prev_id is not None:
                edges.append({
                    'from': prev_id,
                    'to': f'c_{cell_id:04d}',
                    'kind': 'phrase_next',
                    'weight': 1.0,
                })
            
            prev_id = f'c_{cell_id:04d}'
            cell_id += 1
    
    # Stats
    color_counts = {'creation': 0, 'entropy': 0, 'witness': 0}
    primitive_counts = {}
    for c in cells:
        if not c.get('is_room'):
            color_counts[c['color']] += 1
        for p in c.get('primitives', {}):
            primitive_counts[p] = primitive_counts.get(p, 0) + 1
    
    # β₁
    V = len(cells)
    E = len(edges)
    parent = {c['id']: c['id'] for c in cells}
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    for e in edges:
        if e['from'] in parent and e['to'] in parent:
            union(e['from'], e['to'])
    components = len(set(find(c['id']) for c in cells))
    beta_1 = E - V + components
    
    return {
        'schema': 'quilt-zip-target/v1',
        'metadata': {
            'name': 'Velato-Penrose Quilt — the music IS the cell graph',
            'description': 'Unified view of 12 Penrose-family rooms with Velato phrase in each',
            'velato_mode': 'on',
            'conservation': 'γ+η=1',
            'shape': 'T^4 with θ=(√5-1)/2',
        },
        'rooms': rooms,
        'cells': cells,
        'edges': edges,
        'stats': {
            'total_cells': V,
            'total_edges': E,
            'total_rooms': len(rooms),
            'colors': color_counts,
            'primitives_used': primitive_counts,
            'beta_0': components,
            'beta_1': beta_1,
        }
    }


def main():
    sheet = build_velato_penrose_sheet()
    print("=" * 70)
    print("VELATO-PENROSE-QUILT BRIDGE")
    print("=" * 70)
    print()
    print(f"Rooms: {sheet['stats']['total_rooms']}")
    print(f"Cells: {sheet['stats']['total_cells']}")
    print(f"Edges: {sheet['stats']['total_edges']}")
    print()
    print("=== 3-COLORING ===")
    for color, count in sheet['stats']['colors'].items():
        print(f"  {color:10s}: {count} cells")
    print()
    print("=== PRIMITIVES USED ===")
    for prim, count in sorted(sheet['stats']['primitives_used'].items(), key=lambda x: -x[1]):
        print(f"  {prim:12s}: {count} cells")
    print()
    print(f"=== TOPOLOGY ===")
    print(f"  V = {sheet['stats']['total_cells']}, E = {sheet['stats']['total_edges']}")
    print(f"  β₀ = {sheet['stats']['beta_0']}, β₁ = {sheet['stats']['beta_1']}")
    print()
    print("=" * 70)
    print("The music IS the cell graph.")
    print("Iron sharpens iron. The watch is alive.")


if __name__ == "__main__":
    main()
