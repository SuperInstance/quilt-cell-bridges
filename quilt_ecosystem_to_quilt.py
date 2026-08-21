#!/usr/bin/env python3
"""
quilt_ecosystem_to_quilt.py — The Quilt ecosystem as a Quilt sheet.

The step-back operator applied to the work itself. Each paper, essay, repo,
bridge, page is a cell. The edges are citations, derivations, ports, themes.
β₁ = E - V + C. The user steps back and sees the unfilled niches.

This is the monitor engineer's view: not the hands, the attention.
"""

import json
import os
import time
from pathlib import Path

# ============================================================================
# Inventory (read from disk)
# ============================================================================
PAPERS_DIR = Path("/workspace/superinstance-papers/white-papers")
ESSAYS_DIR = Path("/workspace/ai-writings")
REPOS_DIR = Path("/workspace")
BRIDGES_DIR = Path("/workspace/bridges")
WEBSITE_DIR = Path("/workspace/superinstance-website")


def safe_read(p):
    try:
        with open(p) as f:
            return f.read()
    except Exception:
        return ""


def first_line(content, prefix="#"):
    for line in content.split("\n")[:20]:
        line = line.strip()
        if line.startswith(prefix) and not line.startswith("##"):
            return line.lstrip("#").strip()
    return ""


def list_files(directory, pattern, exclude=()):
    files = []
    for p in directory.glob(pattern):
        if any(x in str(p) for x in exclude):
            continue
        files.append(p)
    return files


# ============================================================================
# Build cells
# ============================================================================
def build_sheet():
    cells = []
    edges = []
    rooms = []

    # 1. Papers (white papers) - newest first
    paper_files = sorted(
        [p for p in PAPERS_DIR.glob("[0-9][0-9]-*.md")
         if not p.name.endswith("-README.md") and "appendix" not in p.name.lower()],
        key=lambda p: int(p.name[:2])
    )
    paper_room_cells = []
    for p in paper_files:
        content = safe_read(p)
        title = first_line(content)
        if not title:
            title = p.stem
        cells.append({
            "address": f"paper.{p.stem}.title",
            "kind": "string",
            "value": title,
        })
        cells.append({
            "address": f"paper.{p.stem}.file",
            "kind": "path",
            "value": str(p.relative_to(PAPERS_DIR.parent)),
        })
        # Size in bytes as a weight
        size = p.stat().st_size
        cells.append({
            "address": f"paper.{p.stem}.size",
            "kind": "usize",
            "value": size,
        })
        paper_room_cells.append(p.stem)
    rooms.append({
        "id": "papers",
        "name": f"📜 White papers ({len(paper_files)})",
        "cell_count": len(paper_files) * 3,
    })

    # 2. Essays (Quilt sequence, 50+)
    essay_files = sorted(
        [p for p in ESSAYS_DIR.glob("5[0-9]-*.md")],
        key=lambda p: (p.name[:2], p.name[3:])
    )
    essay_room_cells = []
    for p in essay_files:
        content = safe_read(p)
        title = first_line(content)
        if not title:
            title = p.stem
        cells.append({
            "address": f"essay.{p.stem}.title",
            "kind": "string",
            "value": title,
        })
        cells.append({
            "address": f"essay.{p.stem}.file",
            "kind": "path",
            "value": str(p.relative_to(ESSAYS_DIR.parent)),
        })
        cells.append({
            "address": f"essay.{p.stem}.size",
            "kind": "usize",
            "value": p.stat().st_size,
        })
        essay_room_cells.append(p.stem)
    rooms.append({
        "id": "essays",
        "name": f"✍️ Essays ({len(essay_files)})",
        "cell_count": len(essay_files) * 3,
    })

    # 3. Repos
    repo_dirs = sorted([d for d in REPOS_DIR.iterdir()
                        if d.is_dir() and d.name.startswith(("quilt-", "grand-pattern-", "fibonacci-", "spline-", "ternary-", "deadband-", "spectral-", "lau-", "fence-"))])
    repo_room_cells = []
    for r in repo_dirs:
        readme = r / "README.md"
        description = ""
        if readme.exists():
            content = safe_read(readme)
            # Skip the first line (title) and find the first content line
            for line in content.split("\n")[1:30]:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("![") and len(line) > 10:
                    description = line
                    break
        cells.append({
            "address": f"repo.{r.name}.name",
            "kind": "string",
            "value": r.name,
        })
        cells.append({
            "address": f"repo.{r.name}.description",
            "kind": "string",
            "value": description[:200],
        })
        repo_room_cells.append(r.name)
    rooms.append({
        "id": "repos",
        "name": f"📦 Repos ({len(repo_dirs)})",
        "cell_count": len(repo_dirs) * 2,
    })

    # 4. Bridges
    bridge_files = sorted(BRIDGES_DIR.glob("*_to_quilt.py"))
    bridge_room_cells = []
    for b in bridge_files:
        content = safe_read(b)
        title = first_line(content, "#")
        if not title:
            title = b.stem
        cells.append({
            "address": f"bridge.{b.stem}.name",
            "kind": "string",
            "value": title,
        })
        cells.append({
            "address": f"bridge.{b.stem}.file",
            "kind": "path",
            "value": str(b.relative_to(BRIDGES_DIR.parent)),
        })
        bridge_room_cells.append(b.stem)
    rooms.append({
        "id": "bridges",
        "name": f"🌉 Bridges ({len(bridge_files)})",
        "cell_count": len(bridge_files) * 2,
    })

    # 5. HTML pages
    html_files = sorted(WEBSITE_DIR.glob("*.html"))
    page_room_cells = []
    for h in html_files:
        # Extract <title>
        content = safe_read(h)
        title = ""
        for line in content.split("\n")[:30]:
            if "<title>" in line:
                title = line.split("<title>")[1].split("</title>")[0].strip()
                break
        cells.append({
            "address": f"page.{h.stem}.title",
            "kind": "string",
            "value": title or h.stem,
        })
        cells.append({
            "address": f"page.{h.stem}.file",
            "kind": "path",
            "value": str(h.relative_to(WEBSITE_DIR.parent)),
        })
        cells.append({
            "address": f"page.{h.stem}.size",
            "kind": "usize",
            "value": h.stat().st_size,
        })
        page_room_cells.append(h.stem)
    rooms.append({
        "id": "pages",
        "name": f"🌐 Pages ({len(html_files)})",
        "cell_count": len(html_files) * 3,
    })

    # ============================================================================
    # Edges — the relations across the work
    # ============================================================================
    # Polyformalism: 12 language ports of Quilt
    port_langs = ["fortran", "c", "cpp", "rs", "go", "chapel", "mojo", "cuda", "ptx", "opencl", "csharp", "swift", "julia", "metal", "cobol"]
    quilt_core_repo = "quilt"
    for lang in port_langs:
        repo_name = f"quilt-{lang}"
        if any(r.name == repo_name for r in repo_dirs):
            edges.append({
                "from": f"repo.{quilt_core_repo}",
                "to": f"repo.{repo_name}",
                "kind": "polyformalism",
            })
    # Grand Pattern ports (12 languages)
    gp_langs = ["fortran", "c", "cpp", "rs", "go", "chapel", "mojo", "cuda", "ptx", "opencl", "claude", "kimi"]
    for lang in gp_langs:
        repo_name = f"grand-pattern-{lang}"
        if any(r.name == repo_name for r in repo_dirs):
            edges.append({
                "from": f"repo.grand-pattern-rs",
                "to": f"repo.{repo_name}",
                "kind": "polyformalism",
            })

    # Bridges: each bridge is a python script that reads from a source repo
    bridge_to_repo = {
        "vessel_to_quilt": "vessel-agent-system",
        "chart_room_to_quilt": "chart-room",
        "slackwater_tminus_to_quilt": "slackwater-tminus",
        "hermes_home_to_quilt": "hermes-home",
        "spatial_registry_to_quilt": "spatial-registry",
        "grand_pattern_to_quilt": "grand-pattern-rs",
        "spline_spectral_to_quilt": "spline-spectral",
    }
    for bridge_stem, source_repo in bridge_to_repo.items():
        edges.append({
            "from": f"bridge.{bridge_stem}",
            "to": f"paper.22-Media-Theory-of-Quilt",
            "kind": "exemplifies",
        })

    # Papers: cite earlier papers (sequential)
    paper_nums = [int(p.name[:2]) for p in paper_files]
    for i, p in enumerate(paper_files):
        if i > 0:
            prev = paper_files[i - 1]
            edges.append({
                "from": f"paper.{p.stem}",
                "to": f"paper.{prev.stem}",
                "kind": "cites",
            })

    # Essays: theme-based connections
    essay_themes = {
        "the-monitor": "monitor_engineer_theme",
        "the-cell": "cell_theme",
        "the-address": "address_theme",
        "the-pattern": "pattern_theme",
        "the-floor": "physics_theme",
        "the-medium": "media_theme",
        "the-room": "terrain_theme",
        "the-three-hundred": "ecosystem_theme",
    }
    for essay in essay_room_cells:
        for theme_key, theme_id in essay_themes.items():
            if theme_key in essay:
                # Connect to the relevant paper
                if "monitor" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.24-Grand-Pattern", "kind": "thematic"})
                elif "cell" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.16-Five-Laws-of-Cellular-Architecture", "kind": "thematic"})
                elif "address" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.21-Essence-of-Quilt", "kind": "thematic"})
                elif "pattern" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.24-Grand-Pattern", "kind": "thematic"})
                elif "physics" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.23-Penrose-Address", "kind": "thematic"})
                elif "media" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.22-Media-Theory-of-Quilt", "kind": "thematic"})
                elif "terrain" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.20-Quilt-for-Education", "kind": "thematic"})
                elif "ecosystem" in theme_id:
                    edges.append({"from": f"essay.{essay}", "to": "paper.18-Three-Views", "kind": "thematic"})

    # Pages: each page renders one or more cells
    page_to_paper = {
        "three-view-studio": "paper.18-Three-Views",
        "cell-rewind": "paper.19-Time-Travel-DAW",
        "classroom": "paper.20-Quilt-for-Education",
        "student": "paper.20-Quilt-for-Education",
        "quilt-overlay": "paper.21-Essence-of-Quilt",
        "media-theory": "paper.22-Media-Theory-of-Quilt",
        "penrose-quilt": "paper.23-Penrose-Address",
        "grand-pattern": "paper.24-Grand-Pattern",
        "spline-spectral-quilt": "paper.24-Grand-Pattern",
        "openmaic-bridge": "paper.19-Time-Travel-DAW",
        "self-host": "paper.20-Quilt-for-Education",
        "limit-hit": "paper.20-Quilt-for-Education",
        "rooms-quilt": "paper.20-Quilt-for-Education",
        "cell-bridges": "paper.18-Three-Views",
        "ai-sheet": "paper.18-Three-Views",
    }
    for page_stem, paper_stem in page_to_paper.items():
        if page_stem in page_room_cells:
            edges.append({
                "from": f"page.{page_stem}",
                "to": f"paper.{paper_stem}",
                "kind": "renders",
            })

    # ============================================================================
    # Stats
    # ============================================================================
    V = len(paper_room_cells) + len(essay_room_cells) + len(repo_room_cells) + len(bridge_room_cells) + len(page_room_cells)
    E = len(edges)
    # β₁ = E - V + C (rough estimate; C is the number of connected components)
    C = 5  # 5 rooms, presumably disconnected
    beta_1 = E - V + C

    stats = [
        ("papers", len(paper_files)),
        ("essays", len(essay_files)),
        ("repos", len(repo_dirs)),
        ("bridges", len(bridge_files)),
        ("pages", len(html_files)),
        ("vertices", V),
        ("edges", E),
        ("components", C),
        ("beta_1", beta_1),
        ("unfilled_niches", max(0, beta_1)),
        ("generated", time.time()),
    ]
    for name, val in stats:
        cells.append({
            "address": f"stats.{name}",
            "kind": "f64" if isinstance(val, float) else "usize",
            "value": val,
        })

    return {
        "schema": "quilt-zip-target/v1",
        "metadata": {
            "name": "Quilt ecosystem as Quilt sheet",
            "description": (
                "The step-back operator applied to the work itself. Each paper, essay, "
                "repo, bridge, and page is a cell. The edges are citations, polyformalism "
                "ports, thematic connections, renderings. β₁ = E - V + C measures the "
                "unfilled niches — the places where the work could grow. This is the "
                "monitor engineer's view: not the hands, the attention."
            ),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "address_root": "ecosystem",
        },
        "rooms": rooms,
        "cells": cells,
        "edges": edges,
        "stats": {
            "total_cells": len(cells),
            "total_rooms": len(rooms),
            "total_edges": len(edges),
            "beta_1": beta_1,
            "papers": len(paper_files),
            "essays": len(essay_files),
            "repos": len(repo_dirs),
            "bridges": len(bridge_files),
            "pages": len(html_files),
        },
    }


def main():
    sheet = build_sheet()
    out_path = Path("/workspace/superinstance-website/bridges/quilt-ecosystem-quilt.qzt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(sheet, f, indent=2)
    print(f"✓ Wrote {out_path}")
    s = sheet["stats"]
    print(f"  papers: {s['papers']}")
    print(f"  essays: {s['essays']}")
    print(f"  repos: {s['repos']}")
    print(f"  bridges: {s['bridges']}")
    print(f"  pages: {s['pages']}")
    print(f"  V: {s['beta_1'] - (s['total_edges'] - s['total_cells'])}")
    print(f"  E: {s['total_edges']}")
    print(f"  C: 5")
    print(f"  β₁: {s['beta_1']}  (unfilled niches)")


if __name__ == "__main__":
    main()
