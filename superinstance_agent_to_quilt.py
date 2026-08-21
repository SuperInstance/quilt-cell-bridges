#!/usr/bin/env python3
"""
superinstance_agent_to_quilt.py — Bridge the superinstance-agent to Quilt.

superinstance-agent IS the discovery substrate of Quilt. A cell at any
level needs to discover other cells. superinstance-agent:
- Cloudflare Worker + Vectorize + Workers AI
- 1,600+ Rust crates indexed
- BGE-small 384-dim embeddings
- Llama 3.1 8B RAG
- $0.0001 per query
- 2-stage RAG: retrieval + generation
"""
import json
from pathlib import Path

SA_MODULES = [
    # The RAG pipeline
    ("rag_embed_query", "BGE-small embedding of user question → 384-dim vector", "typescript"),
    ("rag_vectorize", "Vectorize cosine search → top-K crates (HNSW index, O(log N))", "typescript"),
    ("rag_context", "Assemble context: system + top-K descriptions + question", "typescript"),
    ("rag_generate", "Llama 3.1 8B with T=0.3 (factual). Workers AI.", "typescript"),
    # The endpoints
    ("endpoint_ask", "POST /ask: natural-language Q&A. Returns answer + citations.", "typescript"),
    ("endpoint_recommend", "POST /recommend: ranked crate suggestions for a task.", "typescript"),
    # The infrastructure
    ("infra_vectorize", "Cloudflare Vectorize: fleet-crates index. 1600+ vectors.", "typescript"),
    ("infra_workers_ai", "Cloudflare Workers AI: BGE-small + Llama 3.1 8B.", "typescript"),
    ("infra_worker", "Cloudflare Worker: orchestrator. npm install + wrangler deploy.", "typescript"),
    # The math
    ("math_cosine", "cos(q,c) = (q·c) / (||q|| ||c||). Standard cosine similarity.", "typescript"),
    ("math_complexity", "Embed O(V), search O(log N), generate O(T²), context O(K).", "typescript"),
    # The cost
    ("cost_embed", "Embed: ~5ms. Free (Workers AI).", "typescript"),
    ("cost_search", "Vectorize: ~2ms. $0.30/M queries.", "typescript"),
    ("cost_llm", "LLM: ~500ms. $0.0001/1K tokens.", "typescript"),
    ("cost_total", "Total: ~510ms. ~$0.0001/query.", "typescript"),
    # The ecosystem
    ("ecosystem_crates", "1,600+ Rust crates: networking, consensus, spectral, ternary, etc.", "rust"),
    ("ecosystem_discovery", "Discovery: 'which crate handles consensus?' → raft-cluster, paxos-fleet", "rust"),
    ("ecosystem_understanding", "Understanding: 'what does riff-benchmark-hashing do?' → RAG explanation", "rust"),
    ("ecosystem_recommendation", "Recommendation: 'I need a rate-limited API gateway' → ranked list", "rust"),
]


def make_cell(name, description, language):
    primitives = []
    if "rag" in name:
        if "embed" in name:
            primitives = ["Spawn", "Observe", "Mutate"]  # embed
        elif "vectorize" in name:
            primitives = ["Spawn", "Observe", "Send"]  # search
        elif "generate" in name:
            primitives = ["Spawn", "Send", "Receive", "JEPA"]  # gen
        else:
            primitives = ["Spawn", "Observe"]
    elif "endpoint" in name:
        primitives = ["Spawn", "Send", "Receive", "Observe"]  # I/O
    elif "infra" in name:
        primitives = ["Spawn", "Observe", "GC"]  # substrate
    elif "math" in name or "cost" in name:
        primitives = ["Observe"]  # meta
    elif "ecosystem" in name:
        primitives = ["Spawn", "Observe", "Mutate", "Send"]  # discovery
    else:
        primitives = ["Spawn", "Observe"]
    return {
        "id": f"sa_{name.replace('-', '_')}",
        "kind": "cell",
        "form": {"name": name.replace("_", " ").title().replace(" ", "")},
        "description": description,
        "language": language,
        "primitives": primitives,
        "z_in": {"input": "user question"},
        "z_out": {"output": "answer + citations"},
        "jepa": {"predict": "relevant crates", "observe": "actual relevant crates"},
        "double_entry": {"gamma": 0.4, "eta": 0.6},  # Discovery is η-dominant
        "vibe": {"position": 0, "velocity": 0, "acceleration": 0},
        "gc": {"phase": "discovering"},
        "murmur": {},
        "graph": {"parents": [], "children": []},
        "openers": [
            {"name": "ask", "args": ["str"], "returns": "Answer"},
            {"name": "recommend", "args": ["str"], "returns": "List<Crate>"},
        ],
        "substrate": {
            "address": f"/superinstance-agent/{name}",
            "scale": 1,
            "room": "DiscoveryRoom",
            "protocol": "RAG",
            "form": name,
            "state": "ready"
        },
        "tags": ["superinstance-agent", "discovery", "rag", language]
    }


def make_meta_cells():
    return [
        {
            "id": "superinstance_agent_meta",
            "kind": "cell",
            "form": {"name": "SuperInstanceAgentMeta"},
            "description": "superinstance-agent IS the discovery substrate of Quilt. 2-stage RAG over 1,600+ Rust crates. BGE-small + Vectorize + Llama 3.1 8B. $0.0001 per query. The cell at any level needs to discover other cells; superinstance-agent is that discovery.",
            "primitives": ["Observe"] * 19,
            "z_in": {"crates": "1,600+", "index": "Vectorize", "embeddings": "BGE-384"},
            "z_out": {"answer": "grounded in citations"},
            "jepa": {"predict": "relevant crate", "verified": True},
            "double_entry": {"gamma": 0.4, "eta": 0.6},
            "gc": {"phase": "discovering"},
            "murmur": {},
            "graph": {"children": [f"sa_{n.replace('-', '_')}" for n, _, _ in SA_MODULES]},
            "openers": [
                {"name": "ask", "args": ["str"], "returns": "Answer"},
                {"name": "recommend", "args": ["str"], "returns": "List<Crate>"},
            ],
            "tags": ["meta", "discovery", "rag"]
        }
    ]


def build_qzt():
    cells = []
    for name, desc, lang in SA_MODULES:
        cells.append(make_cell(name, desc, lang))
    cells.extend(make_meta_cells())
    edges = []
    for n, _, _ in SA_MODULES:
        if n.startswith("rag"):
            edges.append({"from": f"sa_{n.replace('-', '_')}", "to": "sa_endpoint_ask", "kind": "feeds", "weight": 0.9})
        elif n.startswith("infra") or n.startswith("math") or n.startswith("cost"):
            edges.append({"from": f"sa_{n.replace('-', '_')}", "to": "sa_rag_embed_query", "kind": "supports", "weight": 0.5})
    return {
        "version": "1.0", "kind": "quilt-zip-target",
        "name": "superinstance-agent-to-quilt",
        "description": "Bridge mapping superinstance-agent to Quilt. The discovery substrate: 2-stage RAG over 1,600+ Rust crates. BGE-small + Vectorize + Llama 3.1 8B.",
        "cells": cells, "edges": edges,
        "external_refs": [{"kind": "github-repo", "name": "superinstance-agent", "org": "SuperInstance"}],
        "stats": {
            "total_cells": len(cells),
            "total_edges": len(edges),
            "modules": len(SA_MODULES),
            "crates_indexed": 1600,
            "embedding_dim": 384,
            "cost_per_query": "$0.0001",
            "latency_ms": 510
        },
        "tags": ["superinstance-agent", "discovery", "rag", "bridge"]
    }


def main():
    qzt = build_qzt()
    out = Path("/workspace/bridges/superinstance_agent_to_quilt.qzt")
    out.write_text(json.dumps(qzt, indent=2))
    print(f"Wrote {out}: {qzt['stats']['total_cells']} cells, {qzt['stats']['total_edges']} edges")


if __name__ == "__main__":
    main()
