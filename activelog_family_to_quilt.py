"""
activelog_family_to_quilt.py

This bridge translates data from the ActivityLog family substrate into the Quilt data model.
The ActivityLog substrate represents user actions and system events as a stream of records.
The Quilt model organizes these records into structured, versioned datasets.

The bridge implements the 8 core primitives of the Quilt system:
1. Dataset (versioned collection of data)
2. File (atomic unit of data)
3. Manifest (index of files and metadata)
4. Version (snapshot of a dataset at a point in time)
5. Blob (raw data content, stored externally)
6. Ref (named pointer to a version)
7. Patch (incremental change to a dataset)
8. Schema (structure of data in a file)

The bridge processes ActivityLog records, extracts relevant metadata and content,
and constructs Quilt-compatible artifacts. It assumes the ActivityLog substrate
exposes a stream of dictionaries with keys: 'timestamp', 'event_type', 'user', 'data'.

Usage:
    from bridges.activelog_family_to_quilt import ActivelogToQuiltBridge

    bridge = ActivelogToQuiltBridge()
    dataset = bridge.process(activelog_records)
"""

import json
import hashlib
import time
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache


# === 8 Primitives ===

@dataclass
class Blob:
    """Raw data stored externally. Identifiable by SHA-256 hash."""
    content: bytes
    hash: str = None

    def __post_init__(self):
        if self.hash is None:
            self.hash = hashlib.sha256(self.content).hexdigest()


@dataclass
class File:
    """Atomic unit of data with metadata."""
    name: str
    blob: Blob
    size: int
    mime_type: str = "application/octet-stream"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.size = len(self.blob.content)


@dataclass
class Manifest:
    """Index of files and metadata for a dataset version."""
    files: Dict[str, File]  # name -> File
    metadata: Dict[str, Any]
    created_at: float
    version_id: str

    def __post_init__(self):
        self.created_at = self.created_at or time.time()
        if not self.version_id:
            self.version_id = hashlib.sha256(
                str(self.metadata).encode()
            ).hexdigest()[:16]


@dataclass
class Version:
    """Snapshot of a dataset at a point in time."""
    manifest: Manifest
    ref_name: str = None  # e.g., "main", "v1.0"
    description: str = ""
    parent_version_id: str = None

    def get_manifest(self) -> Manifest:
        return self.manifest


@dataclass
class Ref:
    """Named pointer to a version."""
    name: str
    version_id: str
    created_at: float
    description: str = ""

    def __post_init__(self):
        self.created_at = self.created_at or time.time()


@dataclass
class Patch:
    """Incremental change to a dataset."""
    changes: List[Dict[str, Any]]  # e.g., [{"op": "add", "path": "/files/foo.json", "value": file}]
    metadata: Dict[str, Any]
    version_id: str
    parent_version_id: str

    def __post_init__(self):
        self.version_id = self.version_id or hashlib.sha256(
            str(self.metadata).encode()
        ).hexdigest()[:16]


@dataclass
class Schema:
    """Structure of data in a file."""
    fields: List[Dict[str, Any]]  # list of {name: str, type: str, nullable: bool}
    version: str = "1.0"
    description: str = ""

    def __post_init__(self):
        for field in self.fields:
            if 'nullable' not in field:
                field['nullable'] = True


# === Bridge Implementation ===

class ActivelogToQuiltBridge:
    """
    Translates ActivityLog substrate records into Quilt datasets.
    
    Input: List[Dict] with keys: 'timestamp', 'event_type', 'user', 'data'
    Output: Quilt-compatible Dataset object (composed of Version, Manifest, etc.)
    
    The bridge processes events by type:
        - 'data_upload': create new File
        - 'schema_update': update Schema
        - 'dataset_create': initialize new dataset
        - 'version_commit': create new Version
        - 'ref_create': create new Ref
        - 'patch_apply': apply Patch
        - 'file_delete': remove file from manifest
        - 'data_update': update file content
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._current_version: Optional[Version] = None
        self._version_stack: List[Version] = []
        self._refs: Dict[str, Ref] = {}
        self._manifest: Optional[Manifest] = None
        self._schema: Optional[Schema] = None
        self._dataset_id: str = None
        self._base_dir: str = "/tmp/quilt_data"

    def _normalize_timestamp(self, ts: Any) -> float:
        """Convert various timestamp types to float (seconds since epoch)."""
        if isinstance(ts, (int, float)):
            return float(ts)
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except:
                pass
        return time.time()

    def _generate_file_id(self, name: str, content: bytes) -> str:
        """Generate unique file ID from name and content."""
        key = f"{name}:{hashlib.sha256(content).hexdigest()}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _get_schema_from_data(self, data: Dict[str, Any]) -> Schema:
        """Extract schema from data structure."""
        fields = []
        for k, v in data.items():
            if isinstance(v, (int, float)):
                t = "number"
            elif isinstance(v, str):
                t = "string"
            elif isinstance(v, bool):
                t = "boolean"
            elif isinstance(v, dict):
                t = "object"
            elif isinstance(v, list):
                t = "array"
            else:
                t = "unknown"
            fields.append({"name": k, "type": t, "nullable": True})
        return Schema(fields=fields, version="1.0")

    def _process_data_upload(self, record: Dict[str, Any]) -> None:
        """Create a new File from data and add to manifest."""
        data = record.get("data", {})
        name = record.get("data", {}).get("name", "unknown.json")
        content = json.dumps(data, indent=2).encode("utf-8")

        blob = Blob(content=content)
        file = File(
            name=name,
            blob=blob,
            size=len(content),
            mime_type="application/json",
            metadata={"source": "activelog", "event_id": record.get("id")}
        )

        if self._manifest is None:
            self._manifest = Manifest(
                files={},
                metadata={"created_by": record.get("user"), "source": "activelog"},
                created_at=self._normalize_timestamp(record.get("timestamp")),
                version_id="initial"
            )

        file_id = self._generate_file_id(name, content)
        self._manifest.files[name] = file

    def _process_schema_update(self, record: Dict[str, Any]) -> None:
        """Update the dataset schema."""
        new_schema = record.get("data", {})
        self._schema = Schema(
            fields=new_schema.get("fields", []),
            version=new_schema.get("version", "1.0"),
            description=new_schema.get("description", "")
        )

    def _process_dataset_create(self, record: Dict[str, Any]) -> None:
        """Initialize a new dataset."""
        name = record.get("data", {}).get("name", "dataset")
        self._dataset_id = record.get("data", {}).get("id", hashlib.sha256(name.encode()).hexdigest()[:8])
        self._manifest = Manifest(
            files={},
            metadata={
                "name": name,
                "id": self._dataset_id,
                "created_by": record.get("user"),
                "source": "activelog"
            },
            created_at=self._normalize_timestamp(record.get("timestamp")),
            version_id="initial"
        )
        self._schema = Schema(fields=[], version="1.0")

    def _process_version_commit(self, record: Dict[str, Any]) -> None:
        """Create a new version snapshot."""
        version_id = record.get("data", {}).get("version_id", None)
        parent_id = record.get("data", {}).get("parent_id", None)

        if self._manifest is None:
            return

        version = Version(
            manifest=self._manifest,
            ref_name=record.get("data", {}).get("ref_name"),
            description=record.get("data", {}).get("description", ""),
            parent_version_id=parent_id
        )

        self._current_version = version
        self._version_stack.append(version)

        # Update refs if specified
        ref_name = record.get("data", {}).get("ref_name")
        if ref_name:
            self._refs[ref_name] = Ref(
                name=ref_name,
                version_id=version_id or version.manifest.version_id,
                created_at=self._normalize_timestamp(record.get("timestamp")),
                description=record.get("data", {}).get("description", "")
            )

    def _process_ref_create(self, record: Dict[str, Any]) -> None:
        """Create a named reference to a version."""
        ref_name = record.get("data", {}).get("name")
        version_id = record.get("data", {}).get("version_id")
        if not ref_name or not version_id:
            return

        self._refs[ref_name] = Ref(
            name=ref_name,
            version_id=version_id,
            created_at=self._normalize_timestamp(record.get("timestamp")),
            description=record.get("data", {}).get("description", "")
        )

    def _process_patch_apply(self, record: Dict[str, Any]) -> None:
        """Apply a patch to the current manifest."""
        patch_data = record.get("data", {})
        changes = patch_data.get("changes", [])
        parent_id = patch_data.get("parent_version_id")

        # In a real system, we'd apply these changes
        # For now, just record
        patch = Patch(
            changes=changes,
            metadata=patch_data.get("metadata", {}),
            version_id=patch_data.get("version_id"),
            parent_version_id=parent_id
        )

    def _process_file_delete(self, record: Dict[str, Any]) -> None:
        """Remove a file from the manifest."""
        file_name = record.get("data", {}).get("name")
        if self._manifest and file_name in self._manifest.files:
            del self._manifest.files[file_name]

    def _process_data_update(self, record: Dict[str, Any]) -> None:
        """Update existing file content."""
        data = record.get("data", {})
        file_name = data.get("name")
        new_content = json.dumps(data.get("content"), indent=2).encode("utf-8")

        if self._manifest and file_name in self._manifest.files:
            old_file = self._manifest.files[file_name]
            new_blob = Blob(content=new_content)
            new_file = File(
                name=file_name,
                blob=new_blob,
                size=len(new_content),
                mime_type=old_file.mime_type,
                metadata={**old_file.metadata, "updated_by": record.get("user")}
            )
            self._manifest.files[file_name] = new_file

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main processing method.
        Input: List of ActivityLog records.
        Output: Dictionary containing Quilt dataset structure.
        """
        if not records:
            raise ValueError("No records to process")

        # Initialize
        self._reset_state()

        # Process each record
        for record in records:
            event_type = record.get("event_type")
            if not event_type:
                continue

            handler = getattr(self, f"_process_{event_type.replace('-', '_')}", None)
            if handler:
                try:
                    handler(record)
                except Exception as e:
                    print(f"Error processing {event_type}: {e}")
                    continue
            else:
                print(f"No handler for event type: {event_type}")

        # Finalize
        if self._manifest is None:
            raise ValueError("No manifest created. Dataset not initialized.")

        # Create final version if needed
        if not self._current_version:
            self._process_version_commit({
                "event_type": "version_commit",
                "timestamp": time.time(),
                "user": "system",
                "data": {
                    "version_id": "final",
                    "ref_name": "main"
                }
            })

        # Return dataset structure
        return {
            "dataset_id": self._dataset_id or "unknown",
            "version": self._current_version.manifest.version_id,
            "manifest": self._manifest,
            "refs": self._refs,
            "schema": self._schema,
            "created_at": self._normalize_timestamp(records[0].get("timestamp")),
            "processed_at": time.time(),
            "record_count": len(records)
        }

    def _reset_state(self) -> None:
        """Reset all internal state."""
        self._cache.clear()
        self._current_version = None
        self._version_stack.clear()
        self._refs.clear()
        self._manifest = None
        self._schema = None
        self._dataset_id = None

    def get_latest_version(self) -> Optional[Version]:
        """Return the latest version."""
        return self._current_version or (self._version_stack[-1] if self._version_stack else None)

    def get_ref(self, name: str) -> Optional[Ref]:
        """Get a reference by name."""
        return self._refs.get(name)

    def get_file(self, name: str) -> Optional[File]:
        """Get a file by name."""
        return self._manifest.files.get(name) if self._manifest else None


# === Tests ===

def test_activelog_to_quilt_bridge():
    """Test the bridge with sample data."""
    bridge = ActivelogToQuiltBridge()

    sample_records = [
        {
            "timestamp": "2023-01-01T12:00:00Z",
            "event_type": "dataset_create",
            "user": "alice",
            "data": {
                "name": "test_dataset",
                "id": "test-123"
            }
        },
        {
            "timestamp": "2023-01-01T12:01:00Z",
            "event_type": "schema_update",
            "user": "alice",
            "data": {
                "version": "1.0",
                "description": "Test schema",
                "fields": [
                    {"name": "id", "type": "number", "nullable": False},
                    {"name": "name", "type": "string", "nullable": True}
                ]
            }
        },
        {
            "timestamp": "2023-01-01T12:02:00Z",
            "event_type": "data_upload",
            "user": "alice",
            "data": {
                "name": "users.json",
                "content": {"id": 1, "name": "Alice"}
            }
        },
        {
            "timestamp": "2023-01-01T12:03:00Z",
            "event_type": "version_commit",
            "user": "alice",
            "data": {
                "version_id": "v1.0",
                "ref_name": "main",
                "description": "Initial commit"
            }
        }
    ]

    result = bridge.process(sample_records)

    # Assertions
    assert result["dataset_id"] == "test-123"
    assert result["version"] == "v1.0"
    assert len(result["manifest"].files) == 1
    assert "users.json" in result["manifest"].files
    assert result["manifest"].files["users.json"].name == "users.json"
    assert result["schema"].version == "1.0"
    assert len(result["schema"].fields) == 2
    assert result["refs"]["main"].name == "main"
    assert result["refs"]["main"].version_id == "v1.0"
    assert result["processed_at"] > result["created_at"]


def test_activelog_to_quilt_with_updates():
    """Test update and delete operations."""
    bridge = ActivelogToQuiltBridge()

    records = [
        {
            "timestamp": "2023-01-01T12:00:00Z",
            "event_type": "dataset_create",
            "user": "alice",
            "data": {"name": "test", "id": "test-1"}
        },
        {
            "timestamp": "2023-01-01T12:01:00Z",
            "event_type": "data_upload",
            "user": "alice",
            "data": {"name": "data.json", "content": {"a": 1, "b": 2}}
        },
        {
            "timestamp": "2023-01-01T12:02:00Z",
            "event_type": "data_update",
            "user": "bob",
            "data": {"name": "data.json", "content": {"a": 1, "b": 3}}
        },
        {
            "timestamp": "2023-01-01T12:03:00Z",
            "event_type": "file_delete",
            "user": "charlie",
            "data": {"name": "data.json"}
        }
    ]

    result = bridge.process(records)

    # After delete, file should be gone
    assert "data.json" not in result["manifest"].files

    # Version should still be created
    assert result["version"] is not None
    assert result["record_count"] == len(records)


if __name__ == "__main__":
    # Run tests
    test_activelog_to_quilt_bridge()
    test_activelog_to_quilt_with_updates()
    print("All tests passed.")
