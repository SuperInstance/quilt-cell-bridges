"""
compress_family_to_quilt.py

A bridge for the compress substrate that transforms a family of compressible data into a quilt structure.

This module implements a family-to-quilt compression transformation using the 8 core primitives defined in the compress substrate.
The transformation is lossless, deterministic, and designed for efficiency and simplicity.

Primitives:
1. `pack`: Converts a sequence of values into a packed binary representation.
2. `unpack`: Reverses `pack`, restoring original values.
3. `encode`: Compresses data using a dictionary-based encoding scheme.
4. `decode`: Reverses `encode`, restoring original data.
5. `chunk`: Splits data into fixed-size chunks for parallel processing.
6. `reassemble`: Combines chunks back into a single stream.
7. `hash`: Generates a deterministic hash of data for integrity checking.
8. `verify`: Validates data integrity using a provided hash.

The bridge maps a family of data (e.g., a list of dictionaries) into a quilt—a structured, compressed, and verifiable format.

Usage:
    from bridges.compress_family_to_quilt import compress_family_to_quilt, decompress_quilt_to_family

    data_family = [
        {"id": 1, "name": "Alice", "score": 85.5},
        {"id": 2, "name": "Bob", "score": 92.0},
        {"id": 3, "name": "Charlie", "score": 78.3}
    ]

    quilt = compress_family_to_quilt(data_family)
    recovered_family = decompress_quilt_to_family(quilt)

    assert data_family == recovered_family
"""

import json
import hashlib
import struct
from typing import List, Dict, Any, Tuple, Optional


# === PRIMITIVE 1: pack ===
def pack(values: List[Any]) -> bytes:
    """
    Packs a list of values into a binary format using type tags and length prefixes.
    Supports: int, float, str, bool, None.

    Format:
        - 1 byte: type tag (0=INT, 1=FLOAT, 2=STR, 3=BOOL, 4=NULL)
        - For strings: length (4 bytes) + data
        - For ints: 8 bytes (big-endian)
        - For floats: 8 bytes (big-endian)
        - For bool: 1 byte (0=False, 1=True)
        - For None: no data
    """
    result = bytearray()
    for val in values:
        if val is None:
            result.append(4)
        elif isinstance(val, int):
            result.append(0)
            result.extend(struct.pack('>q', val))
        elif isinstance(val, float):
            result.append(1)
            result.extend(struct.pack('>d', val))
        elif isinstance(val, str):
            result.append(2)
            data = val.encode('utf-8')
            result.extend(struct.pack('>I', len(data)))
            result.extend(data)
        elif isinstance(val, bool):
            result.append(3)
            result.append(1 if val else 0)
        else:
            raise TypeError(f"Unsupported type: {type(val)}")
    return bytes(result)


# === PRIMITIVE 2: unpack ===
def unpack(data: bytes) -> List[Any]:
    """
    Unpacks binary data into original values using the format defined in `pack`.
    """
    result = []
    i = 0
    while i < len(data):
        t = data[i]
        i += 1

        if t == 4:  # None
            result.append(None)
        elif t == 0:  # int
            val = struct.unpack('>q', data[i:i+8])[0]
            result.append(val)
            i += 8
        elif t == 1:  # float
            val = struct.unpack('>d', data[i:i+8])[0]
            result.append(val)
            i += 8
        elif t == 2:  # str
            length = struct.unpack('>I', data[i:i+4])[0]
            i += 4
            s = data[i:i+length].decode('utf-8')
            result.append(s)
            i += length
        elif t == 3:  # bool
            result.append(bool(data[i]))
            i += 1
        else:
            raise ValueError(f"Unknown type tag: {t}")
    return result


# === PRIMITIVE 3: encode ===
def encode(data: bytes) -> bytes:
    """
    Compresses data using simple dictionary encoding (LZ-like, but deterministic).

    Strategy: build a dictionary of repeated 4-byte sequences and replace them with indices.
    This is a minimal encoding for deterministic compression.

    Output format:
        - 4 bytes: dictionary size (number of entries)
        - For each entry: 4 bytes (sequence) + 4 bytes (index)
        - Then: encoded data stream where each 4-byte block is replaced by index (if present)
    """
    if not data:
        return b''

    # Build dictionary of 4-byte sequences and their first occurrence index
    dictionary = {}
    pattern_to_idx = {}
    idx = 0

    for start in range(len(data) - 3):
        chunk = data[start:start+4]
        if chunk not in pattern_to_idx:
            pattern_to_idx[chunk] = idx
            dictionary[idx] = chunk
            idx += 1

    # Build encoded stream
    encoded = bytearray()
    i = 0
    while i < len(data):
        if i + 4 <= len(data):
            chunk = data[i:i+4]
            if chunk in pattern_to_idx:
                idx = pattern_to_idx[chunk]
                encoded.extend(struct.pack('>I', idx))
                i += 4
                continue
        # If not in dict, emit as literal
        encoded.extend(data[i:i+1])
        i += 1

    # Encode dictionary size and entries
    dict_bytes = struct.pack('>I', len(dictionary))
    for k, v in dictionary.items():
        dict_bytes += struct.pack('>I', k)
        dict_bytes += v

    return dict_bytes + encoded


# === PRIMITIVE 4: decode ===
def decode(data: bytes) -> bytes:
    """
    Reverses `encode`. Reconstructs original data from encoded bytes.
    """
    if not data:
        return b''

    # Parse dictionary size
    dict_size = struct.unpack('>I', data[:4])[0]
    offset = 4
    dictionary = {}

    # Read dictionary entries
    for _ in range(dict_size):
        idx = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        chunk = data[offset:offset+4]
        offset += 4
        dictionary[idx] = chunk

    # Decode data stream
    result = bytearray()
    while offset < len(data):
        idx = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        if idx in dictionary:
            result.extend(dictionary[idx])
        else:
            # Literal byte
            result.append(idx)  # Since idx is byte-sized

    return bytes(result)


# === PRIMITIVE 5: chunk ===
def chunk(data: bytes, size: int) -> List[bytes]:
    """
    Splits data into chunks of specified size. Last chunk may be shorter.
    """
    chunks = []
    for i in range(0, len(data), size):
        chunks.append(data[i:i+size])
    return chunks


# === PRIMITIVE 6: reassemble ===
def reassemble(chunks: List[bytes]) -> bytes:
    """
    Combines a list of chunks into a single byte stream.
    """
    return b''.join(chunks)


# === PRIMITIVE 7: hash ===
def hash(data: bytes) -> str:
    """
    Returns a SHA-256 hex digest of the data.
    """
    return hashlib.sha256(data).hexdigest()


# === PRIMITIVE 8: verify ===
def verify(data: bytes, expected_hash: str) -> bool:
    """
    Returns True if data's hash matches expected_hash.
    """
    return hash(data) == expected_hash


# === CORE BRIDGE FUNCTIONS ===

def compress_family_to_quilt(family: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Transforms a family (list of dictionaries) into a quilt—a compressed, structured, verifiable format.

    Steps:
        1. Serialize each dict to JSON string.
        2. Pack the strings into a single binary blob.
        3. Encode (compress) the blob.
        4. Chunk the encoded blob.
        5. Generate a hash of the entire quilt content.
        6. Return a quilt dictionary with:
            - 'chunks': list of chunked, encoded bytes
            - 'hash': SHA-256 hash of quilt content
            - 'metadata': schema version, encoding type, etc.
    """
    # Step 1: Serialize each dict to JSON string
    json_strings = [json.dumps(item, separators=(',', ':')) for item in family]

    # Step 2: Pack the strings into binary
    packed = pack(json_strings)

    # Step 3: Encode (compress) the packed data
    encoded = encode(packed)

    # Step 4: Chunk the encoded data
    chunks = chunk(encoded, 1024)  # 1KB chunks

    # Step 5: Compute hash of quilt content
    quilt_content = reassemble(chunks)
    quilt_hash = hash(quilt_content)

    # Step 6: Return quilt dictionary
    return {
        "version": "1.0",
        "encoding": "compress_family_to_quilt",
        "chunks": [chunk.hex() for chunk in chunks],
        "hash": quilt_hash,
        "metadata": {
            "family_size": len(family),
            "chunk_size": 1024,
            "packed_size": len(packed),
            "encoded_size": len(encoded)
        }
    }


def decompress_quilt_to_family(quilt: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Reverses `compress_family_to_quilt`. Recovers the original family.

    Steps:
        1. Reassemble chunks from quilt.
        2. Verify hash.
        3. Decode the data.
        4. Unpack the binary.
        5. Parse JSON strings into dictionaries.

    Raises:
        ValueError if hash verification fails.
    """
    # Step 1: Reassemble chunks
    chunks = [bytes.fromhex(chunk) for chunk in quilt["chunks"]]
    reassembled = reassemble(chunks)

    # Step 2: Verify hash
    computed_hash = hash(reassembled)
    expected_hash = quilt["hash"]
    if computed_hash != expected_hash:
        raise ValueError(f"Quilt hash mismatch: expected {expected_hash}, got {computed_hash}")

    # Step 3: Decode (decompress)
    decoded = decode(reassembled)

    # Step 4: Unpack
    json_strings = unpack(decoded)

    # Step 5: Parse JSON
    return [json.loads(s) for s in json_strings]


# === TESTS ===

def test_pack_unpack():
    """Test that pack and unpack are inverses."""
    test_data = [
        123,
        456.789,
        "hello",
        True,
        False,
        None,
        0,
        -999
    ]
    packed = pack(test_data)
    unpacked = unpack(packed)
    assert test_data == unpacked, f"Failed to round-trip: {test_data} -> {unpacked}"


def test_encode_decode():
    """Test that encode and decode are inverses."""
    test_data = b"ABCDABCDABCD" * 10
    encoded = encode(test_data)
    decoded = decode(encoded)
    assert test_data == decoded, f"Encode/decode failed: {test_data[:10]} -> {decoded[:10]}"


def test_compress_decompress_quilt():
    """Test full family-to-quilt round-trip."""
    family = [
        {"id": 1, "name": "Alice", "score": 85.5},
        {"id": 2, "name": "Bob", "score": 92.0},
        {"id": 3, "name": "Charlie", "score": 78.3}
    ]

    quilt = compress_family_to_quilt(family)
    recovered = decompress_quilt_to_family(quilt)

    assert family == recovered, f"Failed round-trip: {family} != {recovered}"


def test_invalid_hash():
    """Test that invalid hash raises ValueError."""
    family = [{"id": 1, "name": "Alice"}]
    quilt = compress_family_to_quilt(family)
    quilt["hash"] = "invalid_hash"

    try:
        decompress_quilt_to_family(quilt)
        assert False, "Expected ValueError on invalid hash"
    except ValueError:
        pass  # Expected


if __name__ == "__main__":
    # Run tests
    test_pack_unpack()
    test_encode_decode()
    test_compress_decompress_quilt()
    test_invalid_hash()
    print("All tests passed.")
