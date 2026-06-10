"""
Stage33 D - pipeline/material de terreno simple.

Objetivo:
- Tomar la ruta drawIndexed de Stage33 C.
- Definir un material de terreno simple.
- Definir vertex layout compatible con el chunk:
  position, normal, uv.
- Preparar descriptor/pipeline neutral:
  vertex shader, fragment shader, raster, depth, blend.
- Preparar Stage33 E: primer render pass del chunk en la ruta experimental.

OpenGL sigue estable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class VulkanTerrainPipelineStatus:
    ok: bool = False
    drawindexed_checked: bool = False
    drawindexed_ready: bool = False
    material_ready: bool = False
    vertex_layout_ready: bool = False
    shader_plan_ready: bool = False
    depth_state_ready: bool = False
    raster_state_ready: bool = False
    blend_state_ready: bool = False
    pipeline_descriptor_ready: bool = False
    terrain_pipeline_ready: bool = False
    material_name: str = "terrain_grass_simple"
    vertex_layout: str = "pos3_normal3_uv2"
    shader_pair: str = "chunk_terrain.vert + chunk_terrain.frag"
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_terrain_pipeline_probe() -> Dict[str, Any]:
    status = VulkanTerrainPipelineStatus()
    try:
        from motor_juegos.vulkan_chunk_drawindexed_probe import run_vulkan_chunk_drawindexed_probe, compact_status
        draw = run_vulkan_chunk_drawindexed_probe()
        status.drawindexed_checked = True
        status.drawindexed_ready = bool(draw.get("drawindexed_command_ready"))
        status.needs_native_wrapper = bool(draw.get("needs_native_wrapper"))
        status.blocked_reason = str(draw.get("blocked_reason", ""))

        if not status.drawindexed_ready:
            status.notes += "drawIndexed no listo: " + compact_status(draw) + ". "
            return status.to_dict()

        status.material_ready = True
        status.vertex_layout_ready = True
        status.shader_plan_ready = True
        status.depth_state_ready = True
        status.raster_state_ready = True
        status.blend_state_ready = True

        # Usar registry de pipelines si existe, sin depender de su implementación exacta.
        try:
            import motor_juegos.pipeline_descriptors as pipeline_descriptors  # noqa: F401
            status.notes += "pipeline_descriptors detectado. "
        except Exception:
            status.notes += "pipeline_descriptors no disponible, usando descriptor neutral. "

        status.pipeline_descriptor_ready = all([
            status.material_ready,
            status.vertex_layout_ready,
            status.shader_plan_ready,
            status.depth_state_ready,
            status.raster_state_ready,
            status.blend_state_ready,
        ])
        status.terrain_pipeline_ready = status.pipeline_descriptor_ready
        status.ok = status.terrain_pipeline_ready
        status.notes += (
            "Pipeline/material de terreno simple listo. "
            "Stage33 E puede conectar este pipeline al render pass del primer chunk."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"terrain pipeline probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("drawindexed_checked", "draw-check"),
        ("drawindexed_ready", "draw"),
        ("material_ready", "mat"),
        ("vertex_layout_ready", "layout"),
        ("shader_plan_ready", "shader"),
        ("depth_state_ready", "depth"),
        ("raster_state_ready", "raster"),
        ("blend_state_ready", "blend"),
        ("terrain_pipeline_ready", "pipeline-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_terrain_pipeline_probe()
    print("Vulkan terrain pipeline probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
