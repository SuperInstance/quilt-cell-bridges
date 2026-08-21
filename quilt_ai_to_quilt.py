#!/usr/bin/env python3
"""
Convert @quilt/ai and @quilt/rag packages to a Quilt sheet (.qzt format).
Creates a comprehensive cell graph representing LLM providers, core cell kinds,
and RAG pipeline stages.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any

class QuiltSheetBuilder:
    """Builds a Quilt sheet from package definitions."""
    
    def __init__(self):
        self.cells = []
        self.edges = []
        self.rooms = []
        self.metadata = {}
        self.stats = {
            "total_cells": 0,
            "total_edges": 0,
            "total_rooms": 0,
            "cell_types": {},
            "edge_types": {}
        }
        
    def add_cell(self, cell_id: str, cell_type: str, name: str, 
                 description: str, properties: Dict[str, Any], 
                 room_id: str = "main") -> str:
        """Add a cell to the sheet."""
        cell = {
            "id": cell_id,
            "type": cell_type,
            "name": name,
            "description": description,
            "properties": properties,
            "room_id": room_id,
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        }
        self.cells.append(cell)
        
        # Update stats
        self.stats["total_cells"] += 1
        self.stats["cell_types"][cell_type] = self.stats["cell_types"].get(cell_type, 0) + 1
        
        return cell_id
    
    def add_edge(self, source_id: str, target_id: str, 
                 edge_type: str = "connection", 
                 properties: Dict[str, Any] = None) -> None:
        """Add an edge between two cells."""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "properties": properties or {}
        }
        self.edges.append(edge)
        
        # Update stats
        self.stats["total_edges"] += 1
        self.stats["edge_types"][edge_type] = self.stats["edge_types"].get(edge_type, 0) + 1
    
    def add_room(self, room_id: str, name: str, description: str = "") -> None:
        """Add a room to organize cells."""
        room = {
            "id": room_id,
            "name": name,
            "description": description
        }
        self.rooms.append(room)
        self.stats["total_rooms"] += 1
    
    def build_sheet(self) -> Dict[str, Any]:
        """Build the complete Quilt sheet."""
        return {
            "schema": "quilt-sheet-v1.0",
            "metadata": {
                "title": "Quilt AI & RAG Integration Sheet",
                "description": "Comprehensive Quilt sheet combining LLM providers, core cell kinds, and RAG pipeline",
                "version": "1.0.0",
                "created": datetime.now(timezone.utc).isoformat(),
                "author": "Quilt Bridge Generator",
                "packages": ["@quilt/ai", "@quilt/rag", "@quilt/core"]
            },
            "rooms": self.rooms,
            "cells": self.cells,
            "edges": self.edges,
            "stats": self.stats
        }
    
    def save(self, filepath: str) -> None:
        """Save the sheet to a file."""
        sheet = self.build_sheet()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(sheet, f, indent=2)
        print(f"Quilt sheet saved to {filepath}")
        print(f"Total cells: {self.stats['total_cells']}")
        print(f"Total edges: {self.stats['total_edges']}")
        print(f"Total rooms: {self.stats['total_rooms']}")

def build_quilt_ai_rag_sheet() -> QuiltSheetBuilder:
    """Build the complete Quilt sheet for AI and RAG packages."""
    
    builder = QuiltSheetBuilder()
    
    # Add rooms for organization
    builder.add_room("llm_providers", "LLM Providers", "Integration cells for various LLM providers")
    builder.add_room("core_kinds", "Core Cell Kinds", "The 8 fundamental cell types in Quilt")
    builder.add_room("rag_pipeline", "RAG Pipeline", "Retrieval-Augmented Generation pipeline stages")
    builder.add_room("main", "Main", "Main room for general connections")
    
    # ============================================
    # 1. LLM Provider Cells (4 providers)
    # ============================================
    providers = [
        {
            "id": "provider_openai",
            "name": "OpenAI Provider",
            "description": "Integration with OpenAI's GPT models",
            "properties": {
                "provider": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "endpoint": "https://api.openai.com/v1",
                "capabilities": ["chat", "completion", "embedding", "vision"],
                "api_key_required": True,
                "rate_limit": "5000 req/min"
            }
        },
        {
            "id": "provider_anthropic",
            "name": "Anthropic Provider",
            "description": "Integration with Anthropic's Claude models",
            "properties": {
                "provider": "Anthropic",
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "endpoint": "https://api.anthropic.com/v1",
                "capabilities": ["chat", "completion", "vision"],
                "api_key_required": True,
                "rate_limit": "1000 req/min"
            }
        },
        {
            "id": "provider_deepseek",
            "name": "DeepSeek Provider",
            "description": "Integration with DeepSeek's models",
            "properties": {
                "provider": "DeepSeek",
                "models": ["deepseek-chat", "deepseek-coder"],
                "endpoint": "https://api.deepseek.com/v1",
                "capabilities": ["chat", "completion", "code"],
                "api_key_required": True,
                "rate_limit": "2000 req/min"
            }
        },
        {
            "id": "provider_zai",
            "name": "Z.ai Provider",
            "description": "Integration with Z.ai's models",
            "properties": {
                "provider": "Z.ai",
                "models": ["zai-chat", "zai-vision"],
                "endpoint": "https://api.z.ai/v1",
                "capabilities": ["chat", "completion", "vision"],
                "api_key_required": True,
                "rate_limit": "1500 req/min"
            }
        }
    ]
    
    for provider in providers:
        builder.add_cell(
            cell_id=provider["id"],
            cell_type="llm_provider",
            name=provider["name"],
            description=provider["description"],
            properties=provider["properties"],
            room_id="llm_providers"
        )
    
    # ============================================
    # 2. Core Cell Kinds (8 cells)
    # ============================================
    core_kinds = [
        {
            "id": "kind_number",
            "name": "Number Cell",
            "description": "Numeric value cell",
            "properties": {
                "kind": "number",
                "data_type": "float",
                "validation": "numeric"
            }
        },
        {
            "id": "kind_string",
            "name": "String Cell",
            "description": "Text string cell",
            "properties": {
                "kind": "string",
                "data_type": "string",
                "validation": "text"
            }
        },
        {
            "id": "kind_boolean",
            "name": "Boolean Cell",
            "description": "True/False value cell",
            "properties": {
                "kind": "boolean",
                "data_type": "boolean",
                "validation": "true/false"
            }
        },
        {
            "id": "kind_array",
            "name": "Array Cell",
            "description": "Collection of values cell",
            "properties": {
                "kind": "array",
                "data_type": "array",
                "validation": "list"
            }
        },
        {
            "id": "kind_object",
            "name": "Object Cell",
            "description": "Key-value pair structure cell",
            "properties": {
                "kind": "object",
                "data_type": "object",
                "validation": "key-value"
            }
        },
        {
            "id": "kind_formula",
            "name": "Formula Cell",
            "description": "Computed value cell",
            "properties": {
                "kind": "formula",
                "data_type": "computed",
                "validation": "expression"
            }
        },
        {
            "id": "kind_cell",
            "name": "Cell Reference",
            "description": "Reference to another cell",
            "properties": {
                "kind": "cell",
                "data_type": "reference",
                "validation": "cell-id"
            }
        },
        {
            "id": "kind_sheet",
            "name": "Sheet Cell",
            "description": "Nested sheet container cell",
            "properties": {
                "kind": "sheet",
                "data_type": "container",
                "validation": "nested-sheet"
            }
        }
    ]
    
    for kind in core_kinds:
        builder.add_cell(
            cell_id=kind["id"],
            cell_type="core_kind",
            name=kind["name"],
            description=kind["description"],
            properties=kind["properties"],
            room_id="core_kinds"
        )
    
    # ============================================
    # 3. RAG Pipeline Stages (7 cells)
    # ============================================
    rag_stages = [
        {
            "id": "rag_ingest",
            "name": "Ingest Stage",
            "description": "Document ingestion and preprocessing",
            "properties": {
                "stage": "ingest",
                "order": 1,
                "input": "raw_documents",
                "output": "processed_chunks",
                "processors": ["text_extraction", "chunking", "normalization"]
            }
        },
        {
            "id": "rag_embed",
            "name": "Embed Stage",
            "description": "Generate embeddings for text chunks",
            "properties": {
                "stage": "embed",
                "order": 2,
                "input": "processed_chunks",
                "output": "embeddings",
                "model": "text-embedding-3-small",
                "dimensions": 1536
            }
        },
        {
            "id": "rag_store",
            "name": "Store Stage",
            "description": "Store embeddings in vector database",
            "properties": {
                "stage": "store",
                "order": 3,
                "input": "embeddings",
                "output": "vector_store",
                "database": "pinecone",
                "index_type": "cosine"
            }
        },
        {
            "id": "rag_query",
            "name": "Query Stage",
            "description": "Process user queries",
            "properties": {
                "stage": "query",
                "order": 4,
                "input": "user_query",
                "output": "query_embedding",
                "query_processing": ["normalization", "embedding"]
            }
        },
        {
            "id": "rag_retrieve",
            "name": "Retrieve Stage",
            "description": "Retrieve relevant documents",
            "properties": {
                "stage": "retrieve",
                "order": 5,
                "input": "query_embedding",
                "output": "relevant_chunks",
                "top_k": 5,
                "similarity_threshold": 0.7
            }
        },
        {
            "id": "rag_augment",
            "name": "Augment Stage",
            "description": "Augment context with retrieved documents",
            "properties": {
                "stage": "augment",
                "order": 6,
                "input": "relevant_chunks",
                "output": "augmented_prompt",
                "augmentation": ["context_addition", "prompt_engineering"]
            }
        },
        {
            "id": "rag_generate",
            "name": "Generate Stage",
            "description": "Generate final response using LLM",
            "properties": {
                "stage": "generate",
                "order": 7,
                "input": "augmented_prompt",
                "output": "final_response",
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
    ]
    
    for stage in rag_stages:
        builder.add_cell(
            cell_id=stage["id"],
            cell_type="rag_stage",
            name=stage["name"],
            description=stage["description"],
            properties=stage["properties"],
            room_id="rag_pipeline"
        )
    
    # ============================================
    # 4. Connections (Cell Graph)
    # ============================================
    
    # Connect LLM providers to core kinds (providers can use all core kinds)
    provider_ids = [p["id"] for p in providers]
    kind_ids = [k["id"] for k in core_kinds]
    
    for provider_id in provider_ids:
        for kind_id in kind_ids:
            builder.add_edge(
                source_id=provider_id,
                target_id=kind_id,
                edge_type="uses",
                properties={"description": f"{provider_id} uses {kind_id}"}
            )
    
    # Connect RAG pipeline stages in sequence
    rag_stage_ids = [s["id"] for s in rag_stages]
    for i in range(len(rag_stage_ids) - 1):
        builder.add_edge(
            source_id=rag_stage_ids[i],
            target_id=rag_stage_ids[i + 1],
            edge_type="pipeline",
            properties={
                "description": f"Stage {i+1} → Stage {i+2}",
                "order": i + 1
            }
        )
    
    # Connect RAG stages to LLM providers (generation uses providers)
    builder.add_edge(
        source_id="rag_generate",
        target_id="provider_openai",
        edge_type="uses",
        properties={"description": "Generation uses OpenAI by default"}
    )
    builder.add_edge(
        source_id="rag_generate",
        target_id="provider_anthropic",
        edge_type="uses",
        properties={"description": "Generation can use Anthropic"}
    )
    
    # Connect RAG stages to core kinds
    rag_core_connections = [
        ("rag_ingest", "kind_string", "processes"),
        ("rag_ingest", "kind_array", "produces"),
        ("rag_embed", "kind_array", "produces"),
        ("rag_store", "kind_object", "stores"),
        ("rag_query", "kind_string", "processes"),
        ("rag_retrieve", "kind_array", "produces"),
        ("rag_augment", "kind_object", "produces"),
        ("rag_generate", "kind_string", "produces")
    ]
    
    for source, target, edge_type in rag_core_connections:
        builder.add_edge(
            source_id=source,
            target_id=target,
            edge_type=edge_type,
            properties={"description": f"{source} {edge_type} {target}"}
        )
    
    # Add cross-connections between providers and RAG stages
    provider_rag_connections = [
        ("provider_openai", "rag_embed", "provides_embedding"),
        ("provider_openai", "rag_generate", "provides_generation"),
        ("provider_anthropic", "rag_generate", "provides_generation"),
        ("provider_deepseek", "rag_generate", "provides_generation"),
        ("provider_zai", "rag_generate", "provides_generation")
    ]
    
    for source, target, edge_type in provider_rag_connections:
        builder.add_edge(
            source_id=source,
            target_id=target,
            edge_type=edge_type,
            properties={"description": f"{source} {edge_type} {target}"}
        )
    
    return builder

def main():
    """Main execution function."""
    print("Building Quilt AI & RAG integration sheet...")
    
    # Build the sheet
    builder = build_quilt_ai_rag_sheet()
    
    # Save to file
    output_path = "/workspace/superinstance-website/bridges/quilt-ai-quilt.qzt"
    builder.save(output_path)
    
    # Print summary
    print("\nSheet structure:")
    print(f"  - {len(builder.rooms)} rooms")
    print(f"  - {len(builder.cells)} cells")
    print(f"  - {len(builder.edges)} edges")
    
    # Print cell breakdown
    print("\nCell breakdown:")
    for cell_type, count in builder.stats["cell_types"].items():
        print(f"  - {cell_type}: {count}")
    
    print("\nEdge breakdown:")
    for edge_type, count in builder.stats["edge_types"].items():
        print(f"  - {edge_type}: {count}")

if __name__ == "__main__":
    main()
