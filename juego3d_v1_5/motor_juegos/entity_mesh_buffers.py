"""Conversion de StaticMesh de entidades a datos de buffer neutrales.

Stage31 Pre-Q:
- Convierte StaticMeshInfo (catalogo de entidades) a MeshData reutilizable.
- Todavia no reemplaza el render visual legacy de entidades.
- Prepara una ruta tipo Vulkan: mesh estatica -> vertices/indices -> upload/cache.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Any

from motor_juegos.mesh_data import MeshBatch
from motor_juegos.entity_mesh_catalog import StaticMeshInfo, StaticBoxPart


@dataclass
class EntityMeshBufferData:
    mesh_id: str
    kind: str
    batches: Dict[str, MeshBatch] = field(default_factory=dict)

    def batch(self, name: str, material: str = "entity") -> MeshBatch:
        if name not in self.batches:
            self.batches[name] = MeshBatch(name=name, primitive="quads", material=material)
        return self.batches[name]

    @property
    def vertex_count(self) -> int:
        return sum(batch.vertex_count for batch in self.batches.values())

    @property
    def index_count(self) -> int:
        return sum(batch.index_count for batch in self.batches.values())

    @property
    def quad_count(self) -> int:
        return sum(batch.quad_count for batch in self.batches.values())

    def byte_estimate(self) -> int:
        return sum(batch.byte_estimate() for batch in self.batches.values())

    def summary(self) -> Dict[str, int]:
        return {
            "entity_mesh_batches": len(self.batches),
            "entity_mesh_vertices": self.vertex_count,
            "entity_mesh_indices": self.index_count,
            "entity_mesh_quads": self.quad_count,
            "entity_mesh_bytes": self.byte_estimate(),
        }


def _shade(color, factor: float):
    return tuple(max(0.0, min(1.0, float(c) * factor)) for c in color)


def _add_static_box(buffer: EntityMeshBufferData, part: StaticBoxPart) -> None:
    cx, cy, cz = part.center
    sx, sy, sz = part.size
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz

    # Un batch por material para que Vulkan pueda ordenar/crear pipelines despues.
    batch = buffer.batch(part.material, material=part.material)
    col = part.color
    front = _shade(col, 1.00)
    back = _shade(col, 0.72)
    side = _shade(col, 0.86)
    top = _shade(col, 1.12)
    bottom = _shade(col, 0.58)

    batch.add_quad(front,  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))
    batch.add_quad(back,   (x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0))
    batch.add_quad(side,   (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0))
    batch.add_quad(side,   (x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1))
    batch.add_quad(top,    (x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0))
    batch.add_quad(bottom, (x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1))


def build_entity_mesh_buffer(static_mesh: StaticMeshInfo) -> EntityMeshBufferData:
    buffer = EntityMeshBufferData(mesh_id=static_mesh.mesh_id, kind=static_mesh.kind)
    for part in static_mesh.parts:
        _add_static_box(buffer, part)
    return buffer


class EntityMeshBufferCache:
    """Cache neutral de buffers de entidad.

    En OpenGL actual solo registra datos y estadisticas. En Vulkan esto sera el
    lugar natural para crear VkBuffer de vertices/indices y conservar handles.
    """

    def __init__(self):
        self.buffers: Dict[str, EntityMeshBufferData] = {}
        self.upload_count = 0

    def get_or_build(self, static_mesh: StaticMeshInfo) -> EntityMeshBufferData:
        if static_mesh.mesh_id not in self.buffers:
            self.buffers[static_mesh.mesh_id] = build_entity_mesh_buffer(static_mesh)
            self.upload_count += 1
        return self.buffers[static_mesh.mesh_id]

    def stats(self) -> Dict[str, int]:
        return {
            "entity_mesh_cached": len(self.buffers),
            "entity_mesh_uploads": self.upload_count,
            "entity_mesh_vertices": sum(b.vertex_count for b in self.buffers.values()),
            "entity_mesh_indices": sum(b.index_count for b in self.buffers.values()),
            "entity_mesh_bytes": sum(b.byte_estimate() for b in self.buffers.values()),
        }
