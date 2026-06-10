"""Estructuras pequeñas para el siguiente paso de migracion.

Todavia no reemplazan el render principal, pero dejan definido el vocabulario
que Vulkan necesitara: comandos de dibujo independientes del backend.
"""

from dataclasses import dataclass
from typing import Any, Tuple


@dataclass(frozen=True)
class DrawChunkCommand:
    coord: Tuple[int, int]
    handle: Any
    lod: str = "detail"


@dataclass(frozen=True)
class DrawEntityCommand:
    kind: str
    entity_ref: Any
    distance_sq: float = 0.0


class RenderQueue:
    def __init__(self):
        self.chunks = []
        self.entities = []

    def clear(self):
        self.chunks.clear()
        self.entities.clear()

    def add_chunk(self, coord, handle, lod="detail"):
        self.chunks.append(DrawChunkCommand(coord=coord, handle=handle, lod=lod))

    def add_entity(self, kind, entity_ref, distance_sq=0.0):
        self.entities.append(DrawEntityCommand(kind=kind, entity_ref=entity_ref, distance_sq=distance_sq))
