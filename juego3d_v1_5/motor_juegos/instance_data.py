"""Datos de instancia neutrales para entidades.

Stage31 Pre-O:
- Todavia renderizamos las entidades con callbacks legacy/OpenGL.
- Pero antes de dibujarlas empezamos a crear EntityInstanceData.
- Vulkan necesitara algo similar para llenar instance buffers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from motor_juegos.entity_mesh_catalog import mesh_id_for_kind


@dataclass
class EntityInstanceData:
    kind: str
    position: Tuple[float, float, float]
    yaw: float = 0.0
    scale: float = 1.0
    flags: int = 0
    material: str = "entity"
    mesh_id: str = "mesh_unknown_box"
    transparent: bool = False


@dataclass
class InstanceFrameData:
    instances: List[EntityInstanceData] = field(default_factory=list)

    def clear(self) -> None:
        self.instances.clear()

    def add(self, instance: EntityInstanceData) -> None:
        self.instances.append(instance)

    def count_by_kind(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for inst in self.instances:
            result[inst.kind] = result.get(inst.kind, 0) + 1
        return result

    def stats(self) -> Dict[str, int]:
        by_kind = self.count_by_kind()
        data = {
            "instance_total": len(self.instances),
            "instance_transparent": sum(1 for inst in self.instances if inst.transparent),
            "instance_kinds": len(by_kind),
        }
        for kind, count in by_kind.items():
            data[f"instance_{kind}"] = count
        return data


def build_entity_instance(kind: str, entity, *, transparent: bool = False, material: str = "entity") -> EntityInstanceData:
    """Construye una instancia neutral desde los objetos actuales del juego.

    Soporta entidades con nombres de posicion distintos:
    - player usa pos_x, pos_y, pos_z
    - enemies/npcs/restos usan x, y, z
    """
    x = float(getattr(entity, "pos_x", getattr(entity, "x", 0.0)))
    y = float(getattr(entity, "pos_y", getattr(entity, "y", 0.0)))
    z = float(getattr(entity, "pos_z", getattr(entity, "z", 0.0)))
    yaw = float(getattr(entity, "visual_yaw", getattr(entity, "yaw", 0.0)))
    scale = float(getattr(entity, "body_scale", getattr(entity, "scale", 1.0)))
    flags = 0
    if bool(getattr(entity, "z_locked", False)):
        flags |= 1
    if bool(getattr(entity, "highlight", False)):
        flags |= 2
    if bool(getattr(entity, "is_swimming", False)):
        flags |= 4
    return EntityInstanceData(
        kind=kind,
        position=(x, y, z),
        yaw=yaw,
        scale=scale,
        flags=flags,
        material=material,
        mesh_id=mesh_id_for_kind(kind),
        transparent=transparent,
    )
