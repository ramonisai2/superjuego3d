"""Importador neutral de archivos OBJ.

Stage38 T:
- Carga geometria .obj sin depender de OpenGL.
- Triangula caras n-gon con fan simple.
- Normaliza modelos opcionalmente para que entren en la escala del juego.
- Convierte OBJ a EntityMeshBufferData para la ruta futura OpenGL/Vulkan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import hashlib
import math

from motor_juegos.mesh_data import MeshBatch
from motor_juegos.entity_mesh_buffers import EntityMeshBufferData

Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]
Color = Tuple[float, float, float]


@dataclass(frozen=True)
class ObjFaceVertex:
    vertex: int
    texcoord: Optional[int] = None
    normal: Optional[int] = None


@dataclass(frozen=True)
class ObjTriangle:
    vertices: Tuple[ObjFaceVertex, ObjFaceVertex, ObjFaceVertex]
    material: str = "obj"
    group: str = "default"


@dataclass
class ObjMeshData:
    source_path: str
    vertices: List[Vec3] = field(default_factory=list)
    texcoords: List[Vec2] = field(default_factory=list)
    normals: List[Vec3] = field(default_factory=list)
    triangles: List[ObjTriangle] = field(default_factory=list)
    material_names: List[str] = field(default_factory=list)
    group_names: List[str] = field(default_factory=list)
    normalized: bool = False
    scale_applied: float = 1.0

    @property
    def triangle_count(self) -> int:
        return len(self.triangles)

    @property
    def vertex_count(self) -> int:
        return len(self.triangles) * 3

    @property
    def index_count(self) -> int:
        return len(self.triangles) * 3

    def bounds(self) -> Tuple[Vec3, Vec3]:
        if not self.vertices:
            return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def byte_estimate(self) -> int:
        # Posicion vec3 + normal vec3 + uv vec2 + color rgba + indice uint32.
        return self.vertex_count * (3 * 4 + 3 * 4 + 2 * 4 + 4 * 4) + self.index_count * 4

    def summary(self) -> Dict[str, object]:
        bmin, bmax = self.bounds()
        return {
            "source_path": self.source_path,
            "vertices_source": len(self.vertices),
            "texcoords_source": len(self.texcoords),
            "normals_source": len(self.normals),
            "triangles": self.triangle_count,
            "vertices_expanded": self.vertex_count,
            "indices": self.index_count,
            "materials": len(self.material_names),
            "groups": len(self.group_names),
            "bytes": self.byte_estimate(),
            "normalized": self.normalized,
            "scale_applied": round(float(self.scale_applied), 6),
            "bounds_min": bmin,
            "bounds_max": bmax,
        }


def _resolve_obj_index(raw: str, count: int) -> Optional[int]:
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    if value > 0:
        index = value - 1
    else:
        index = count + value
    if index < 0 or index >= count:
        return None
    return index


def _parse_face_vertex(token: str, vertex_count: int, texcoord_count: int, normal_count: int) -> Optional[ObjFaceVertex]:
    parts = token.split("/")
    vertex = _resolve_obj_index(parts[0], vertex_count) if parts else None
    if vertex is None:
        return None
    texcoord = _resolve_obj_index(parts[1], texcoord_count) if len(parts) >= 2 and parts[1] else None
    normal = _resolve_obj_index(parts[2], normal_count) if len(parts) >= 3 and parts[2] else None
    return ObjFaceVertex(vertex=vertex, texcoord=texcoord, normal=normal)


def _material_color(name: str) -> Color:
    digest = hashlib.sha1(str(name or "obj").encode("utf-8")).digest()
    return (
        0.38 + digest[0] / 255.0 * 0.42,
        0.38 + digest[1] / 255.0 * 0.42,
        0.38 + digest[2] / 255.0 * 0.42,
    )


def _normalize_vertices(vertices: List[Vec3], target_size: float = 1.0, base_on_ground: bool = True) -> Tuple[List[Vec3], float]:
    if not vertices:
        return [], 1.0
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    span = max(max_x - min_x, max_y - min_y, max_z - min_z, 0.0001)
    scale = float(target_size) / span
    center_x = (min_x + max_x) * 0.5
    center_z = (min_z + max_z) * 0.5
    origin_y = min_y if base_on_ground else (min_y + max_y) * 0.5
    normalized = [
        ((x - center_x) * scale, (y - origin_y) * scale, (z - center_z) * scale)
        for x, y, z in vertices
    ]
    return normalized, scale


def _triangulate(face_vertices: List[ObjFaceVertex]) -> Iterable[Tuple[ObjFaceVertex, ObjFaceVertex, ObjFaceVertex]]:
    if len(face_vertices) < 3:
        return []
    triangles = []
    root = face_vertices[0]
    for idx in range(1, len(face_vertices) - 1):
        triangles.append((root, face_vertices[idx], face_vertices[idx + 1]))
    return triangles


def load_obj_mesh(
    path: str,
    *,
    normalize: bool = True,
    target_size: float = 1.0,
    base_on_ground: bool = True,
    default_material: str = "obj",
) -> ObjMeshData:
    obj_path = Path(path).resolve()
    mesh = ObjMeshData(source_path=str(obj_path))
    current_material = str(default_material or "obj")
    current_group = "default"
    materials_seen = {current_material}
    groups_seen = {current_group}

    for line_no, raw_line in enumerate(obj_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        op = parts[0].lower()
        values = parts[1:]
        try:
            if op == "v" and len(values) >= 3:
                mesh.vertices.append((float(values[0]), float(values[1]), float(values[2])))
            elif op == "vt" and len(values) >= 2:
                mesh.texcoords.append((float(values[0]), float(values[1])))
            elif op == "vn" and len(values) >= 3:
                mesh.normals.append((float(values[0]), float(values[1]), float(values[2])))
            elif op in {"o", "g"} and values:
                current_group = values[0]
                groups_seen.add(current_group)
            elif op == "usemtl" and values:
                current_material = values[0]
                materials_seen.add(current_material)
            elif op == "f" and len(values) >= 3:
                face_vertices = []
                for token in values:
                    parsed = _parse_face_vertex(token, len(mesh.vertices), len(mesh.texcoords), len(mesh.normals))
                    if parsed is not None:
                        face_vertices.append(parsed)
                for tri in _triangulate(face_vertices):
                    mesh.triangles.append(ObjTriangle(tri, material=current_material, group=current_group))
        except ValueError as exc:
            raise ValueError(f"OBJ invalido en {obj_path}:{line_no}: {raw_line}") from exc

    mesh.material_names = sorted(materials_seen)
    mesh.group_names = sorted(groups_seen)
    if normalize:
        mesh.vertices, mesh.scale_applied = _normalize_vertices(mesh.vertices, target_size, base_on_ground)
        mesh.normalized = True
    return mesh


def obj_mesh_to_entity_buffer(mesh: ObjMeshData, mesh_id: Optional[str] = None, kind: str = "obj") -> EntityMeshBufferData:
    buffer = EntityMeshBufferData(mesh_id=mesh_id or Path(mesh.source_path).stem, kind=kind)
    for tri in mesh.triangles:
        material = tri.material or "obj"
        batch_name = f"obj_{material}"
        if batch_name not in buffer.batches:
            buffer.batches[batch_name] = MeshBatch(name=batch_name, primitive="triangles", material="obj")
        batch = buffer.batches[batch_name]
        color = _material_color(material)
        points = [mesh.vertices[item.vertex] for item in tri.vertices]
        batch.add_triangle(color, points[0], points[1], points[2])
    return buffer


@dataclass
class ObjAssetRecord:
    asset_id: str
    path: str
    normalize: bool = True
    target_size: float = 1.0
    base_on_ground: bool = True
    default_material: str = "obj"


class ObjAssetRegistry:
    """Registro/cache pequeno para modelos OBJ futuros."""

    def __init__(self):
        self.records: Dict[str, ObjAssetRecord] = {}
        self.cache: Dict[str, ObjMeshData] = {}

    def register(
        self,
        asset_id: str,
        path: str,
        *,
        normalize: bool = True,
        target_size: float = 1.0,
        base_on_ground: bool = True,
        default_material: str = "obj",
    ) -> ObjAssetRecord:
        record = ObjAssetRecord(
            asset_id=str(asset_id),
            path=str(path),
            normalize=bool(normalize),
            target_size=float(target_size),
            base_on_ground=bool(base_on_ground),
            default_material=str(default_material or "obj"),
        )
        self.records[record.asset_id] = record
        self.cache.pop(record.asset_id, None)
        return record

    def load(self, asset_id: str) -> ObjMeshData:
        key = str(asset_id)
        if key in self.cache:
            return self.cache[key]
        if key not in self.records:
            raise KeyError(f"OBJ asset no registrado: {key}")
        record = self.records[key]
        mesh = load_obj_mesh(
            record.path,
            normalize=record.normalize,
            target_size=record.target_size,
            base_on_ground=record.base_on_ground,
            default_material=record.default_material,
        )
        self.cache[key] = mesh
        return mesh

    def get_buffer(self, asset_id: str, kind: str = "obj") -> EntityMeshBufferData:
        return obj_mesh_to_entity_buffer(self.load(asset_id), mesh_id=str(asset_id), kind=kind)

    def clear(self) -> None:
        self.cache.clear()

    def stats(self) -> Dict[str, int]:
        return {
            "obj_assets_registered": len(self.records),
            "obj_assets_loaded": len(self.cache),
            "obj_triangles_loaded": sum(mesh.triangle_count for mesh in self.cache.values()),
            "obj_vertices_loaded": sum(mesh.vertex_count for mesh in self.cache.values()),
            "obj_bytes_loaded": sum(mesh.byte_estimate() for mesh in self.cache.values()),
        }


DEFAULT_OBJ_ASSET_REGISTRY = ObjAssetRegistry()


def compact_obj_status(mesh: ObjMeshData) -> str:
    summary = mesh.summary()
    return (
        f"OBJ tris={summary['triangles']} vertices={summary['vertices_expanded']} "
        f"materials={summary['materials']} normalized={summary['normalized']} "
        f"bytes={summary['bytes']}"
    )
