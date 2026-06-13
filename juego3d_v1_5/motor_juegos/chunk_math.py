"""Utilidades compartidas para coordenadas y anillos de chunks."""

from __future__ import annotations

import math
from typing import List, Tuple


ChunkCoord = Tuple[int, int]

# Margen visual para que el anillo circular no corte diagonales utiles.
CHUNK_RING_CULL_MARGIN = 0.35


def chunk_coord(value: float, chunk_size: float) -> int:
    return int(math.floor(float(value) / max(1.0, float(chunk_size))))


def generate_square_chunk_ring(center: ChunkCoord, radius: int) -> List[ChunkCoord]:
    cx, cz = center
    radius = max(1, int(radius))
    coords: List[ChunkCoord] = []
    for dz in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            coords.append((cx + dx, cz + dz))
    return sorted(coords, key=lambda c: (abs(c[0] - cx) + abs(c[1] - cz), c[1], c[0]))


def passes_chunk_ring_cull(coord: ChunkCoord, center: ChunkCoord, radius: int) -> bool:
    dx = coord[0] - center[0]
    dz = coord[1] - center[1]
    return math.sqrt(float(dx * dx + dz * dz)) <= float(max(1, int(radius))) + CHUNK_RING_CULL_MARGIN


def generate_visible_chunk_ring(center: ChunkCoord, radius: int) -> List[ChunkCoord]:
    return [
        coord
        for coord in generate_square_chunk_ring(center, radius)
        if passes_chunk_ring_cull(coord, center, radius)
    ]
