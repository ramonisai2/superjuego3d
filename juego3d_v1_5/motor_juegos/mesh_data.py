"""Datos de malla independientes de OpenGL para preparar migracion a Vulkan.

Stage31 Pre-I:
- El mundo empieza a producir ChunkMeshData en vez de depender solo de display lists.
- OpenGL aun convierte estos datos a display list.
- Vulkan despues podra convertir los mismos datos a vertex/index buffers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from .materials import get_material

Vec3 = Tuple[float, float, float]
Color3 = Tuple[float, float, float]
Color4 = Tuple[float, float, float, float]


@dataclass
class MeshBatch:
    name: str
    primitive: str = "quads"  # quads | triangles
    vertices: List[Vec3] = field(default_factory=list)
    colors: List[Tuple[float, ...]] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    alpha: float = 1.0
    material: str = "default"
    sort_order: int = 100
    blend: bool = False
    depth_write: bool = True

    def __post_init__(self):
        info = get_material(self.material)
        self.sort_order = int(info.sort_order)
        self.blend = bool(info.blend)
        self.depth_write = bool(info.depth_write)
        if self.alpha == 1.0:
            self.alpha = float(info.alpha)

    def add_quad(self, color, v0, v1, v2, v3):
        col = tuple(float(c) for c in color)
        base = len(self.vertices)
        self.vertices.extend([tuple(v0), tuple(v1), tuple(v2), tuple(v3)])
        self.colors.extend([col, col, col, col])
        # Vulkan preferira triangulos indexados. OpenGL actual sigue dibujando quads,
        # pero dejamos indices listos para buffers futuros.
        self.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    def add_triangle(self, color, v0, v1, v2):
        col = tuple(float(c) for c in color)
        base = len(self.vertices)
        self.vertices.extend([tuple(v0), tuple(v1), tuple(v2)])
        self.colors.extend([col, col, col])
        self.indices.extend([base, base + 1, base + 2])

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def index_count(self) -> int:
        return len(self.indices)

    @property
    def quad_count(self) -> int:
        return len(self.vertices) // 4 if self.primitive == "quads" else 0

    @property
    def triangle_count(self) -> int:
        return len(self.vertices) // 3 if self.primitive == "triangles" else 0

    def byte_estimate(self) -> int:
        # Posicion vec3 + color rgba aproximado + indice uint32.
        return self.vertex_count * (3 * 4 + 4 * 4) + self.index_count * 4

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "material": self.material,
            "primitive": self.primitive,
            "vertices": self.vertex_count,
            "indices": self.index_count,
            "quads": self.quad_count,
            "triangles": self.triangle_count,
            "bytes": self.byte_estimate(),
            "blend": self.blend,
            "sort_order": self.sort_order,
        }


@dataclass
class ChunkMeshData:
    coord: Tuple[int, int]
    size: float
    lod: str = "detail"
    batches: Dict[str, MeshBatch] = field(default_factory=dict)
    # Datos legacy que aun usan funciones OpenGL inmediatas dentro de la display list.
    # Los iremos migrando en etapas posteriores.
    legacy_rocks: List[Any] = field(default_factory=list)
    legacy_deco: List[Any] = field(default_factory=list)
    height_map: Any = None

    def batch(self, name: str, primitive: str = "quads", material: str = "default", alpha: float = 1.0) -> MeshBatch:
        if name not in self.batches:
            self.batches[name] = MeshBatch(name=name, primitive=primitive, material=material, alpha=alpha)
        return self.batches[name]

    @property
    def vertex_count(self) -> int:
        return sum(batch.vertex_count for batch in self.batches.values())

    @property
    def quad_count(self) -> int:
        return sum(batch.quad_count for batch in self.batches.values())

    @property
    def triangle_count(self) -> int:
        return sum(batch.triangle_count for batch in self.batches.values())

    @property
    def index_count(self) -> int:
        return sum(batch.index_count for batch in self.batches.values())

    def byte_estimate(self) -> int:
        return sum(batch.byte_estimate() for batch in self.batches.values())

    def sorted_batches(self) -> List[MeshBatch]:
        return sorted(self.batches.values(), key=lambda b: (b.sort_order, b.material, b.name))

    def material_summary(self) -> Dict[str, Dict[str, int]]:
        info: Dict[str, Dict[str, int]] = {}
        for batch in self.batches.values():
            row = info.setdefault(batch.material, {"batches": 0, "vertices": 0, "indices": 0, "bytes": 0})
            row["batches"] += 1
            row["vertices"] += batch.vertex_count
            row["indices"] += batch.index_count
            row["bytes"] += batch.byte_estimate()
        return info

    def summary(self) -> Dict[str, int]:
        return {
            "batches": len(self.batches),
            "vertices": self.vertex_count,
            "indices": self.index_count,
            "quads": self.quad_count,
            "triangles": self.triangle_count,
            "bytes": self.byte_estimate(),
            "rocks_legacy": len(self.legacy_rocks),
            "deco_legacy": len(self.legacy_deco),
        }
