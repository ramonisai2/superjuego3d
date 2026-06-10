"""Materiales neutrales del motor.

Stage31 Pre-L:
- Centraliza propiedades de materiales para OpenGL actual y Vulkan futuro.
- Vulkan usara estos ids para crear pipelines/descriptor sets por material.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

Color4 = Tuple[float, float, float, float]


@dataclass(frozen=True)
class MaterialInfo:
    id: str
    sort_order: int = 100
    blend: bool = False
    depth_write: bool = True
    double_sided: bool = False
    alpha: float = 1.0
    debug_color: Color4 = (1.0, 1.0, 1.0, 1.0)
    notes: str = ""


MATERIALS: Dict[str, MaterialInfo] = {
    "terrain": MaterialInfo("terrain", sort_order=10, debug_color=(0.35, 0.55, 0.25, 1.0), notes="Suelo/biomas"),
    "rock": MaterialInfo("rock", sort_order=20, debug_color=(0.45, 0.43, 0.40, 1.0), notes="Rocas y prismas minerales"),
    "tree_trunk": MaterialInfo("tree_trunk", sort_order=30, debug_color=(0.34, 0.22, 0.12, 1.0), notes="Troncos"),
    "tree_leaf": MaterialInfo("tree_leaf", sort_order=40, debug_color=(0.10, 0.38, 0.13, 1.0), notes="Hojas/copas/musgo"),
    "plant": MaterialInfo("plant", sort_order=50, double_sided=True, debug_color=(0.20, 0.55, 0.15, 1.0), notes="Pasto, flores, cactus, arbustos"),
    "water": MaterialInfo("water", sort_order=900, blend=True, depth_write=False, double_sided=True, alpha=0.34, debug_color=(0.22, 0.55, 0.75, 0.34), notes="Agua translucida"),
    "shadow": MaterialInfo("shadow", sort_order=910, blend=True, depth_write=False, double_sided=True, alpha=0.12, debug_color=(0.03, 0.03, 0.04, 0.12), notes="Sombras planas baratas"),
    "default": MaterialInfo("default", sort_order=100, debug_color=(1.0, 1.0, 1.0, 1.0), notes="Material fallback"),
}


def get_material(material_id: str) -> MaterialInfo:
    return MATERIALS.get(material_id or "default", MATERIALS["default"])


def ordered_material_ids():
    return [m.id for m in sorted(MATERIALS.values(), key=lambda m: m.sort_order)]
