"""Recursos GPU neutrales previos a Vulkan.

Stage31 Pre-U:
- Define handles de malla/textura/buffer sin depender directamente de OpenGL.
- OpenGL sigue usando display lists internamente, pero el juego recibe objetos neutrales.
- Vulkan podra reemplazar backend_handle por VkBuffer/VkImage/VkDescriptor/etc.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import itertools

_resource_ids = itertools.count(1)


@dataclass(frozen=True)
class NeutralBufferDesc:
    kind: str = "vertex_index"
    vertex_count: int = 0
    index_count: int = 0
    byte_size: int = 0
    material_batches: int = 0
    transparent: bool = False


@dataclass
class NeutralMeshHandle:
    """Handle neutral para una malla subida al backend.

    En OpenGL `backend_handle` es normalmente una display list.
    En Vulkan seria un paquete de buffers/descriptor sets.
    """
    backend: str
    backend_handle: Any
    desc: NeutralBufferDesc
    resource_id: int = field(default_factory=lambda: next(_resource_ids))
    label: str = "mesh"
    coord: Optional[Tuple[int, int]] = None
    lod: str = "detail"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def byte_size(self) -> int:
        return int(self.desc.byte_size)

    @property
    def vertex_count(self) -> int:
        return int(self.desc.vertex_count)

    @property
    def index_count(self) -> int:
        return int(self.desc.index_count)

    @property
    def raw(self) -> Any:
        return self.backend_handle

    def __hash__(self) -> int:
        return int(self.resource_id)


@dataclass
class NeutralTextureHandle:
    backend: str
    backend_handle: Any
    width: int = 0
    height: int = 0
    resource_id: int = field(default_factory=lambda: next(_resource_ids))
    label: str = "texture"


@dataclass
class ResourceFrameStats:
    live_meshes: int = 0
    live_mesh_bytes: int = 0
    created_meshes: int = 0
    released_meshes: int = 0
