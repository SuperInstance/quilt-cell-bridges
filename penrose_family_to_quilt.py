#!/usr/bin/env python3
"""
Convert the Penrose family (12 repos) to a Quilt sheet.
Output: /workspace/superinstance-website/bridges/penrose-family-quilt.qzt
"""

import json
import os
from typing import Dict, List, Any

def build_sheet() -> Dict[str, Any]:
    """Build the Quilt sheet for the Penrose family."""
    
    # Define all 12 repos with their metadata
    repos = [
        {
            "name": "penrose-memory",
            "language": "Rust + Python",
            "core_idea": "Aperiodic memory palace with golden-ratio hashing and 3-coloring",
            "cells": [
                "Golden-ratio hash function",
                "3-coloring algorithm",
                "Aperiodic memory palace data structure",
                "Fibonacci sequence generator"
            ],
            "edges": [
                "penrose-lattice",
                "lau-penrose",
                "penrose-memory-palace-early-version"
            ]
        },
        {
            "name": "penrose-lattice",
            "language": "Rust",
            "core_idea": "Penrose tilings as spectral graphs with Fibonacci substitution",
            "cells": [
                "Penrose tiling generator",
                "Spectral graph construction",
                "Fibonacci substitution system",
                "Eigenvalue computation"
            ],
            "edges": [
                "penrose-memory",
                "lau-penrose",
                "lau-penrose-v2"
            ]
        },
        {
            "name": "lau-penrose",
            "language": "Rust",
            "core_idea": "Base Penrose tiling implementation with golden ratio geometry",
            "cells": [
                "Penrose tile primitives",
                "Golden ratio constants",
                "Tiling composition rules",
                "Decomposition algorithm"
            ],
            "edges": [
                "penrose-memory",
                "penrose-lattice",
                "lau-penrose-v2",
                "lau-penrose-growth"
            ]
        },
        {
            "name": "lau-twistor-agents",
            "language": "Makefile",
            "core_idea": "Penrose's twistor theory applied to multi-agent systems",
            "cells": [
                "Twistor space representation",
                "Agent interaction rules",
                "Conformal geometry primitives",
                "Light ray propagation"
            ],
            "edges": [
                "lau-penrose",
                "tensor-penrose",
                "plato-tour-guide"
            ]
        },
        {
            "name": "tensor-penrose",
            "language": "Python",
            "core_idea": "Tensor-based Penrose tiling extracted from forgemaster",
            "cells": [
                "Tensor operations",
                "Penrose tiling matrices",
                "Numerical solvers",
                "Pattern matching algorithms"
            ],
            "edges": [
                "lau-penrose",
                "lau-twistor-agents",
                "plato-midi-bridge-rs"
            ]
        },
        {
            "name": "lau-penrose-v2",
            "language": "Rust",
            "core_idea": "Version 2 of Penrose tiling with enhanced performance and features",
            "cells": [
                "Optimized tile generation",
                "Parallel processing",
                "Advanced substitution rules",
                "Memory-efficient storage"
            ],
            "edges": [
                "lau-penrose",
                "penrose-lattice",
                "lau-penrose-growth"
            ]
        },
        {
            "name": "plato-midi-bridge-rs",
            "language": "Rust",
            "core_idea": "Eisenstein lattices + Penrose tilings for multi-scale musical generation",
            "cells": [
                "Eisenstein lattice generator",
                "MIDI note mapping",
                "Multi-scale rhythm patterns",
                "Penrose-based harmony"
            ],
            "edges": [
                "tensor-penrose",
                "lau-penrose",
                "plato-tour-guide"
            ]
        },
        {
            "name": "lau-penrose-growth",
            "language": "Rust",
            "core_idea": "Growth patterns in Penrose tilings with Fibonacci scaling",
            "cells": [
                "Growth simulation",
                "Fibonacci scaling factors",
                "Expansion algorithms",
                "Pattern evolution tracking"
            ],
            "edges": [
                "lau-penrose",
                "lau-penrose-v2",
                "fibonacci-growth"
            ]
        },
        {
            "name": "fibonacci-growth",
            "language": "Rust",
            "core_idea": "Fibonacci team growth with CR = 1/φ. Penrose outward, Mandelbrot inward",
            "cells": [
                "Fibonacci sequence calculator",
                "Golden ratio convergence",
                "Mandelbrot set generator",
                "Growth rate analysis"
            ],
            "edges": [
                "lau-penrose-growth",
                "penrose-memory",
                "penrose-lattice"
            ]
        },
        {
            "name": "plato-tour-guide",
            "language": "Python",
            "core_idea": "Wayfinding and Penrose scoping for navigation through the family",
            "cells": [
                "Path finding algorithms",
                "Penrose scope definitions",
                "Navigation graph",
                "Context mapping"
            ],
            "edges": [
                "lau-twistor-agents",
                "plato-midi-bridge-rs",
                "penrose-memory"
            ]
        },
        {
            "name": "penrose-memory-palace-early-version",
            "language": "HTML",
            "core_idea": "Archived early version of the memory palace concept",
            "cells": [
                "HTML/CSS layout",
                "Basic memory palace structure",
                "Visual representation",
                "Legacy code preservation"
            ],
            "edges": [
                "penrose-memory",
                "memory-crystal-early-version"
            ]
        },
        {
            "name": "memory-crystal-early-version",
            "language": "Rust",
            "core_idea": "Archived early version of memory crystal with Rust implementation",
            "cells": [
                "Crystal structure primitives",
                "Memory storage patterns",
                "Early hash functions",
                "Legacy algorithms"
            ],
            "edges": [
                "penrose-memory-palace-early-version",
                "penrose-memory"
            ]
        }
    ]
    
    # Build the Quilt sheet structure (using standard .qzt schema)
    cells = []
    edges = []
    rooms = []

    # Add a stats cell
    import time
    cells.append({
        "address": "stats.total_repos",
        "kind": "usize",
        "value": len(repos),
    })
    cells.append({
        "address": "stats.languages",
        "kind": "usize",
        "value": len(set(r["language"] for r in repos)),
    })
    cells.append({
        "address": "stats.generated",
        "kind": "f64",
        "value": time.time(),
    })
    # The Penrose family's math
    cells.append({
        "address": "math.phi",
        "kind": "f64",
        "value": 1.618033988749895,
    })
    cells.append({
        "address": "math.inv_phi",
        "kind": "f64",
        "value": 0.618033988749895,
    })
    cells.append({
        "address": "math.cut_and_project",
        "kind": "string",
        "value": "5D integer lattice → 2D plane with golden-angle rotation; perpendicular window accepts tiles",
    })
    cells.append({
        "address": "math.substitution",
        "kind": "string",
        "value": "L → LS, S → L; eigenvalues are φ and -1/φ",
    })
    cells.append({
        "address": "thesis.family",
        "kind": "string",
        "value": "Aperiodic order is the right substrate for AI agent systems; φ is its universal constant",
    })

    # Convert each repo to a room with cells and edges
    for repo in repos:
        room_id = repo["name"].replace("-", "_")
        rooms.append({
            "id": room_id,
            "name": f"🔯 {repo['name']} ({repo['language']})",
            "cell_count": 2 + len(repo["cells"]),
        })
        # Room cells: name, language, core idea
        cells.append({
            "address": f"repo.{room_id}.name",
            "kind": "string",
            "value": repo["name"],
        })
        cells.append({
            "address": f"repo.{room_id}.language",
            "kind": "string",
            "value": repo["language"],
        })
        cells.append({
            "address": f"repo.{room_id}.core_idea",
            "kind": "string",
            "value": repo["core_idea"],
        })
        # Component cells
        for j, comp in enumerate(repo["cells"]):
            cells.append({
                "address": f"repo.{room_id}.cell[{j}]",
                "kind": "string",
                "value": comp,
            })
        # Edges to other repos
        for target in repo["edges"]:
            target_id = target.replace("-", "_")
            edges.append({
                "from": f"repo.{room_id}",
                "to": f"repo.{target_id}",
                "kind": "connects_to",
            })

    sheet = {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "Penrose family as Quilt sheet",
            "description": (
                "The Penrose family — 12 repos expressing the same aperiodic substrate. "
                "Aperiodic order is the right substrate for AI agent systems. φ is the "
                "universal constant. The cut-and-project (5D→2D), the substitution rules "
                "(L→LS, S→L), the spectral graph theory, the twistor geometry, the "
                "Eisenstein lattices, the tensor computations — all are different windows "
                "onto the same mathematics."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "penrose",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "total_repos": len(repos),
            "languages": len(set(r["language"] for r in repos)),
        },
    }
    return sheet

def main():
    """Main entry point - build and save the Quilt sheet."""
    
    # Build the sheet
    sheet = build_sheet()
    
    # Ensure output directory exists
    output_dir = "/workspace/superinstance-website/bridges"
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file path
    output_file = os.path.join(output_dir, "penrose-family-quilt.qzt")
    
    # Write the sheet to file
    with open(output_file, "w") as f:
        json.dump(sheet, f, indent=2)
    
    print(f"Penrose family quilt created successfully at {output_file}")
    s = sheet['stats']
    print(f"  total cells: {s['total_cells']}")
    print(f"  total rooms: {s['total_rooms']}")
    print(f"  total edges: {s['total_edges']}")
    print(f"  total repos: {s['total_repos']}")
    print(f"  languages: {s['languages']}")

if __name__ == "__main__":
    main()
