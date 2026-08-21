#!/usr/bin/env python3
"""
Federated Artifact Store to Quilt Sheet Converter

This script converts a federated content-addressable store into a Quilt sheet
format. The Quilt sheet represents the distributed storage topology with:
- Artifact cells (content-addressable data)
- Node cells (federation nodes)
- Edge cells (connections between artifacts and nodes)
- Replication factor cells (copy counts)
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

class FederatedArtifactStore:
    """Represents a federated content-addressable store."""
    
    def __init__(self):
        self.artifacts = []
        self.nodes = []
        self.edges = []
        self.replication_factors = []
        
    def generate_artifact(self, content: bytes, content_type: str) -> Dict[str, Any]:
        """Generate an artifact cell with hash, content type, size, and timestamp."""
        artifact_hash = hashlib.sha256(content).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        artifact = {
            "type": "artifact",
            "hash": artifact_hash,
            "content_type": content_type,
            "size": len(content),
            "timestamp": timestamp,
            "content_preview": content[:50].decode('utf-8', errors='replace') + "..."
        }
        self.artifacts.append(artifact)
        return artifact
    
    def generate_node(self, node_id: str, region: str, capacity: int) -> Dict[str, Any]:
        """Generate a federation node cell."""
        node = {
            "type": "node",
            "node_id": node_id,
            "region": region,
            "capacity": capacity,
            "status": "active",
            "last_heartbeat": datetime.now(timezone.utc).isoformat()
        }
        self.nodes.append(node)
        return node
    
    def add_edge(self, source: str, target: str, edge_type: str) -> Dict[str, Any]:
        """Add an edge between artifacts and nodes or between nodes."""
        edge = {
            "type": "edge",
            "source": source,
            "target": target,
            "edge_type": edge_type,
            "weight": 1.0
        }
        self.edges.append(edge)
        return edge
    
    def add_replication_factor(self, artifact_hash: str, copies: int) -> Dict[str, Any]:
        """Add replication factor information for an artifact."""
        replication = {
            "type": "replication",
            "artifact_hash": artifact_hash,
            "copies": copies,
            "min_copies": 2,
            "max_copies": 5,
            "current_copies": copies
        }
        self.replication_factors.append(replication)
        return replication
    
    def to_quilt_sheet(self) -> Dict[str, Any]:
        """Convert the store to a Quilt sheet format."""
        return {
            "format_version": "1.0",
            "sheet_type": "federated_artifact_store",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "statistics": {
                "total_artifacts": len(self.artifacts),
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "total_replication_factors": len(self.replication_factors),
                "total_cells": len(self.artifacts) + len(self.nodes) + len(self.edges) + len(self.replication_factors)
            },
            "cells": {
                "artifacts": self.artifacts,
                "nodes": self.nodes,
                "edges": self.edges,
                "replication_factors": self.replication_factors
            }
        }

def create_federated_store() -> FederatedArtifactStore:
    """Create a sample federated artifact store with the specified structure."""
    store = FederatedArtifactStore()
    
    # Sample content for artifacts
    sample_contents = [
        (b"user-profile-data-v1", "application/json"),
        (b"image-thumbnail-001", "image/jpeg"),
        (b"video-metadata-002", "application/json"),
        (b"search-index-part-3", "application/octet-stream"),
        (b"model-weights-epoch-10", "application/octet-stream"),
        (b"transaction-log-2024", "application/json"),
        (b"user-avatar-045", "image/png"),
        (b"document-embedding-128d", "application/octet-stream"),
        (b"cache-invalidation-batch", "application/json"),
        (b"analytics-aggregate-daily", "application/json"),
        (b"feature-vector-batch-7", "application/octet-stream"),
        (b"notification-template-v2", "text/plain"),
        (b"geo-location-index", "application/octet-stream"),
        (b"session-data-export", "application/json"),
        (b"recommendation-model-v3", "application/octet-stream"),
        (b"audit-log-2024-q1", "application/json"),
        (b"content-hash-table", "application/octet-stream"),
        (b"user-preference-store", "application/json"),
        (b"ml-training-dataset-5", "application/octet-stream"),
        (b"system-config-snapshot", "application/json")
    ]
    
    # Generate 20 artifact cells
    print("Generating 20 artifact cells...")
    for content, content_type in sample_contents:
        store.generate_artifact(content, content_type)
    
    # Generate 8 node cells
    print("Generating 8 node cells...")
    node_configs = [
        ("node-us-east-1", "us-east-1", 1000000),
        ("node-us-west-2", "us-west-2", 800000),
        ("node-eu-west-1", "eu-west-1", 750000),
        ("node-ap-southeast-1", "ap-southeast-1", 600000),
        ("node-sa-east-1", "sa-east-1", 500000),
        ("node-ca-central-1", "ca-central-1", 450000),
        ("node-ap-northeast-1", "ap-northeast-1", 700000),
        ("node-eu-central-1", "eu-central-1", 650000)
    ]
    
    for node_id, region, capacity in node_configs:
        store.generate_node(node_id, region, capacity)
    
    # Generate 32 edges
    print("Generating 32 edges...")
    node_ids = [node["node_id"] for node in store.nodes]
    artifact_hashes = [artifact["hash"] for artifact in store.artifacts]
    
    # Edge type 1: Artifact -> Node (primary storage location)
    # 20 edges: each artifact assigned to a primary node
    for i, artifact_hash in enumerate(artifact_hashes):
        primary_node = node_ids[i % len(node_ids)]
        store.add_edge(artifact_hash, primary_node, "stored_on")
    
    # Edge type 2: Node -> Node (replication links)
    # 12 edges: create a mesh network between nodes
    import random
    random.seed(42)  # For reproducibility
    for i in range(12):
        source_node = node_ids[random.randint(0, len(node_ids) - 1)]
        target_node = node_ids[random.randint(0, len(node_ids) - 1)]
        if source_node != target_node:
            store.add_edge(source_node, target_node, "replicates_to")
    
    # Generate 4 replication factor cells
    print("Generating 4 replication factor cells...")
    replication_configs = [
        (artifact_hashes[0], 3),
        (artifact_hashes[5], 4),
        (artifact_hashes[10], 2),
        (artifact_hashes[15], 5)
    ]
    
    for artifact_hash, copies in replication_configs:
        store.add_replication_factor(artifact_hash, copies)
    
    return store

def main():
    """Main execution function."""
    print("=" * 60)
    print("Federated Artifact Store to Quilt Sheet Converter")
    print("=" * 60)
    
    # Create the federated store
    store = create_federated_store()
    
    # Convert to Quilt sheet format
    quilt_sheet = store.to_quilt_sheet()
    
    # Ensure output directory exists
    output_dir = "/workspace/superinstance-website/bridges"
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file path
    output_file = os.path.join(output_dir, "federated-artifact-quilt.qzt")
    
    # Write the Quilt sheet to file
    print(f"\nWriting Quilt sheet to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(quilt_sheet, f, indent=2)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Quilt Sheet Generation Complete!")
    print("=" * 60)
    print(f"Artifacts: {len(store.artifacts)}")
    print(f"Nodes: {len(store.nodes)}")
    print(f"Edges: {len(store.edges)}")
    print(f"Replication Factors: {len(store.replication_factors)}")
    print(f"Total Cells: {quilt_sheet['statistics']['total_cells']}")
    print(f"Output File: {output_file}")
    print(f"File Size: {os.path.getsize(output_file):,} bytes")
    
    # Display sample of the structure
    print("\nSample Artifact Cell:")
    print(json.dumps(store.artifacts[0], indent=2))
    
    print("\nSample Node Cell:")
    print(json.dumps(store.nodes[0], indent=2))
    
    print("\nSample Edge Cell:")
    print(json.dumps(store.edges[0], indent=2))
    
    print("\nSample Replication Factor Cell:")
    print(json.dumps(store.replication_factors[0], indent=2))

if __name__ == "__main__":
    main()
