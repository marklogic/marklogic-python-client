# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


"""
Supports encoding and decoding vectors using the same approach as the vec:base64-encode and vec:base64-decode
functions supported by the MarkLogic server.
"""

import base64
import struct
from typing import List


def base64_encode(vector: List[float]) -> str:
    """
    Encodes a list of floats as a base64 string compatible with MarkLogic's vec:base64-encode.
    """
    dimensions = len(vector)
    # version (int32, 0) + dimensions (int32) + floats (little-endian)
    buffer = struct.pack("<ii", 0, dimensions) + struct.pack(
        "<" + "f" * dimensions, *vector
    )
    return base64.b64encode(buffer).decode("ascii")


def base64_decode(encoded_vector: str) -> List[float]:
    """
    Decodes a base64 string to a list of floats compatible with MarkLogic's vec:base64-decode.
    """
    buffer = base64.b64decode(encoded_vector)
    if len(buffer) < 8:
        raise ValueError("Buffer is too short to contain version and dimensions.")
    version, dimensions = struct.unpack("<ii", buffer[:8])
    if version != 0:
        raise ValueError(f"Unsupported vector version: {version}")
    expected_length = 8 + 4 * dimensions
    if len(buffer) < expected_length:
        raise ValueError(
            f"Buffer is too short for the specified dimensions: expected {expected_length}, got {len(buffer)}"
        )
    floats = struct.unpack("<" + "f" * dimensions, buffer[8 : 8 + 4 * dimensions])
    return list(floats)
