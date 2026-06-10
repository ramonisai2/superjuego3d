"""
Stage33 C - drawIndexed experimental del primer chunk.

Objetivo:
- Tomar los buffers planeados de Stage33 B.
- Crear una orden de dibujo neutral tipo Vulkan:
  bind pipeline -> bind vertex buffer -> bind index buffer -> drawIndexed.
- Preparar Stage33 D: pipeline/material real para terreno simple.

Esto sigue siendo un puente experimental. OpenGL sigue estable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class VulkanChunkDrawIndexedStatus:
    ok: bool = False
    buffer_upload_checked: bool = False
    buffers_ready: bool = False
    pipeline_layout_planned: bool = False
    terrain_pipeline_planned: bool = False
    vertex_binding_planned: bool = False
    index_binding_planned: bool = False
    drawindexed_command_ready: bool = False
    draw_index_count: int = 0
    draw_instance_count: int = 1
    first_index: int = 0
    vertex_offset: int = 0
    first_instance: int = 0
    command_sequence: str = ""
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_chunk_drawindexed_probe() -> Dict[str, Any]:
    status = VulkanChunkDrawIndexedStatus()
    try:
        from motor_juegos.vulkan_chunk_buffer_upload_probe import run_vulkan_chunk_buffer_upload_probe, compact_status
        buffers = run_vulkan_chunk_buffer_upload_probe()
        status.buffer_upload_checked = True
        status.buffers_ready = bool(buffers.get("gpu_upload_ready"))
        status.needs_native_wrapper = bool(buffers.get("needs_native_wrapper"))
        status.blocked_reason = str(buffers.get("blocked_reason", ""))

        if not status.buffers_ready:
            status.notes += "Buffers del chunk no listos: " + compact_status(buffers) + ". "
            return status.to_dict()

        status.pipeline_layout_planned = True
        status.terrain_pipeline_planned = True
        status.vertex_binding_planned = True
        status.index_binding_planned = True
        status.draw_index_count = int(buffers.get("index_count", 0) or 96)

        status.command_sequence = "vkCmdBindPipeline > vkCmdBindVertexBuffers > vkCmdBindIndexBuffer > vkCmdDrawIndexed"
        status.drawindexed_command_ready = status.draw_index_count > 0
        status.ok = status.drawindexed_command_ready

        status.notes += (
            "Comando drawIndexed neutral listo para el primer chunk. "
            "Stage33 D puede preparar pipeline/material de terreno simple."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"chunk drawIndexed probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("buffer_upload_checked", "buffer-check"),
        ("buffers_ready", "buffers"),
        ("pipeline_layout_planned", "layout"),
        ("terrain_pipeline_planned", "pipe"),
        ("vertex_binding_planned", "vbind"),
        ("index_binding_planned", "ibind"),
        ("drawindexed_command_ready", "drawIndexed-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("draw_index_count"):
        flags.append(f"indices{stats.get('draw_index_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_chunk_drawindexed_probe()
    print("Vulkan chunk drawIndexed probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
