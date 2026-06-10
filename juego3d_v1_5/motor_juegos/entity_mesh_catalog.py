"""Catalogo neutral de StaticMesh para entidades.

Stage31 Pre-P:
- No reemplaza aun el render legacy de jugador/slimes/NPCs.
- Define siluetas reutilizables que Vulkan podra subir como buffers estaticos.
- EntityInstanceData referencia mesh_id para separar 'geometria estatica' de
  'instancia con posicion/rotacion/escala'.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

Vec3 = Tuple[float, float, float]
Color = Tuple[float, float, float]


@dataclass
class StaticBoxPart:
    name: str
    center: Vec3
    size: Vec3
    material: str = "entity"
    color: Color = (1.0, 1.0, 1.0)

    @property
    def vertex_count(self) -> int:
        # Caja con 6 caras, 4 vertices por cara si se expande por material/cara.
        return 24

    @property
    def index_count(self) -> int:
        # 6 caras * 2 triangulos * 3 indices.
        return 36


@dataclass
class StaticMeshInfo:
    mesh_id: str
    kind: str
    parts: List[StaticBoxPart] = field(default_factory=list)
    transparent: bool = False

    @property
    def part_count(self) -> int:
        return len(self.parts)

    @property
    def vertex_count(self) -> int:
        return sum(p.vertex_count for p in self.parts)

    @property
    def index_count(self) -> int:
        return sum(p.index_count for p in self.parts)

    def byte_estimate(self) -> int:
        # Estimado simple: pos(3f)+color(3f)+uv(2f) = 32 bytes por vertice, indice uint32.
        return self.vertex_count * 32 + self.index_count * 4


class EntityMeshCatalog:
    def __init__(self):
        self.meshes: Dict[str, StaticMeshInfo] = {}
        self.kind_to_mesh: Dict[str, str] = {}
        self._build_defaults()

    def register(self, mesh: StaticMeshInfo, *kinds: str) -> None:
        self.meshes[mesh.mesh_id] = mesh
        for kind in kinds or (mesh.kind,):
            self.kind_to_mesh[kind] = mesh.mesh_id

    def get_mesh_id_for_kind(self, kind: str) -> str:
        return self.kind_to_mesh.get(kind, "mesh_unknown_box")

    def get(self, mesh_id: str) -> StaticMeshInfo:
        return self.meshes.get(mesh_id, self.meshes["mesh_unknown_box"])

    def stats(self) -> Dict[str, int]:
        return {
            "static_meshes": len(self.meshes),
            "static_mesh_parts": sum(m.part_count for m in self.meshes.values()),
            "static_mesh_vertices": sum(m.vertex_count for m in self.meshes.values()),
            "static_mesh_indices": sum(m.index_count for m in self.meshes.values()),
            "static_mesh_bytes": sum(m.byte_estimate() for m in self.meshes.values()),
        }

    def _build_defaults(self) -> None:
        # Caja de emergencia.
        self.register(StaticMeshInfo(
            mesh_id="mesh_unknown_box",
            kind="unknown",
            parts=[StaticBoxPart("body", (0, 0.5, 0), (0.6, 1.0, 0.6), "entity", (0.8, 0.8, 0.8))],
        ), "unknown")

        # Slime: cuerpo gelatinoso + nucleo + ojos + patitas.
        self.register(StaticMeshInfo(
            mesh_id="mesh_slime_basic",
            kind="enemy",
            transparent=True,
            parts=[
                StaticBoxPart("body", (0, 0.70, 0), (0.90, 0.74, 0.86), "slime_body", (0.85, 0.10, 0.12)),
                StaticBoxPart("core", (0, 0.68, 0), (0.50, 0.36, 0.46), "slime_core", (1.0, 0.18, 0.18)),
                StaticBoxPart("eye_l", (-0.18, 0.80, 0.45), (0.13, 0.10, 0.03), "eye", (1, 1, 1)),
                StaticBoxPart("eye_r", (0.18, 0.80, 0.45), (0.13, 0.10, 0.03), "eye", (1, 1, 1)),
                StaticBoxPart("leg_fl", (-0.25, 0.16, 0.25), (0.10, 0.32, 0.10), "slime_leg", (0.55, 0.08, 0.08)),
                StaticBoxPart("leg_fr", (0.25, 0.16, 0.25), (0.10, 0.32, 0.10), "slime_leg", (0.55, 0.08, 0.08)),
                StaticBoxPart("leg_bl", (-0.25, 0.16, -0.25), (0.10, 0.32, 0.10), "slime_leg", (0.55, 0.08, 0.08)),
                StaticBoxPart("leg_br", (0.25, 0.16, -0.25), (0.10, 0.32, 0.10), "slime_leg", (0.55, 0.08, 0.08)),
            ],
        ), "enemy", "slime", "slime_puddle")

        # Humanoide base para jugador y NPCs: geometria estatica de referencia.
        humanoid_parts = [
            StaticBoxPart("torso", (0, 1.03, -0.02), (0.76, 0.74, 0.42), "cloth", (0.18, 0.32, 0.70)),
            StaticBoxPart("head", (0, 1.60, 0), (0.43, 0.49, 0.43), "skin", (0.88, 0.74, 0.60)),
            StaticBoxPart("arm_l", (-0.54, 1.00, 0), (0.18, 0.76, 0.22), "cloth", (0.15, 0.30, 0.60)),
            StaticBoxPart("arm_r", (0.54, 1.00, 0), (0.18, 0.78, 0.22), "cloth", (0.15, 0.30, 0.60)),
            StaticBoxPart("leg_l", (-0.19, 0.55, 0), (0.25, 0.55, 0.28), "pants", (0.12, 0.18, 0.30)),
            StaticBoxPart("leg_r", (0.19, 0.55, 0), (0.25, 0.55, 0.28), "pants", (0.12, 0.18, 0.30)),
            StaticBoxPart("boot_l", (-0.19, 0.12, 0), (0.31, 0.09, 0.37), "boot", (0.08, 0.10, 0.13)),
            StaticBoxPart("boot_r", (0.19, 0.12, 0), (0.31, 0.09, 0.37), "boot", (0.08, 0.10, 0.13)),
            StaticBoxPart("backpack", (0, 1.05, -0.29), (0.36, 0.42, 0.14), "leather", (0.31, 0.21, 0.12)),
        ]
        self.register(StaticMeshInfo("mesh_player_boxel", "player", humanoid_parts), "player")
        self.register(StaticMeshInfo("mesh_npc_humanoid", "npc", humanoid_parts[:8]), "npc", "human", "humanoid")


DEFAULT_ENTITY_MESH_CATALOG = EntityMeshCatalog()


def mesh_id_for_kind(kind: str) -> str:
    return DEFAULT_ENTITY_MESH_CATALOG.get_mesh_id_for_kind(kind)


def catalog_stats() -> Dict[str, int]:
    return DEFAULT_ENTITY_MESH_CATALOG.stats()
