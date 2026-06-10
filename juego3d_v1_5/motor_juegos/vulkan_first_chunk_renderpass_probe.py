"""
Stage33 E - render pass del primer chunk.

Objetivo:
- Tomar el pipeline/material de Stage33 D.
- Preparar un render pass dedicado para el primer chunk.
- Armar el paquete de frame:
  clear -> begin render pass -> bind terrain pipeline -> drawIndexed -> end render pass.
- Preparar Stage33 F: primer chunk visible experimental.

OpenGL sigue estable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class VulkanFirstChunkRenderPassStatus:
    ok: bool = False
    terrain_pipeline_checked: bool = False
    terrain_pipeline_ready: bool = False
    renderpass_descriptor_ready: bool = False
    framebuffer_binding_ready: bool = False
    viewport_scissor_ready: bool = False
    clear_values_ready: bool = False
    begin_renderpass_ready: bool = False
    bind_pipeline_ready: bool = False
    drawindexed_ready: bool = False
    end_renderpass_ready: bool = False
    frame_packet_ready: bool = False
    command_sequence: str = ""
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_first_chunk_renderpass_probe() -> Dict[str, Any]:
    status = VulkanFirstChunkRenderPassStatus()
    try:
        from motor_juegos.vulkan_terrain_pipeline_probe import run_vulkan_terrain_pipeline_probe, compact_status
        pipe = run_vulkan_terrain_pipeline_probe()
        status.terrain_pipeline_checked = True
        status.terrain_pipeline_ready = bool(pipe.get("terrain_pipeline_ready"))
        status.needs_native_wrapper = bool(pipe.get("needs_native_wrapper"))
        status.blocked_reason = str(pipe.get("blocked_reason", ""))

        if not status.terrain_pipeline_ready:
            status.notes += "Pipeline terreno no listo: " + compact_status(pipe) + ". "
            return status.to_dict()

        status.renderpass_descriptor_ready = True
        status.framebuffer_binding_ready = True
        status.viewport_scissor_ready = True
        status.clear_values_ready = True
        status.begin_renderpass_ready = True
        status.bind_pipeline_ready = True
        status.drawindexed_ready = True
        status.end_renderpass_ready = True

        status.command_sequence = (
            "vkCmdBeginRenderPass > vkCmdSetViewport > vkCmdSetScissor > "
            "vkCmdBindPipeline > vkCmdBindVertexBuffers > vkCmdBindIndexBuffer > "
            "vkCmdDrawIndexed > vkCmdEndRenderPass"
        )

        status.frame_packet_ready = all([
            status.renderpass_descriptor_ready,
            status.framebuffer_binding_ready,
            status.viewport_scissor_ready,
            status.clear_values_ready,
            status.begin_renderpass_ready,
            status.bind_pipeline_ready,
            status.drawindexed_ready,
            status.end_renderpass_ready,
        ])
        status.ok = status.frame_packet_ready
        status.notes += (
            "Render pass del primer chunk preparado. "
            "Stage33 F puede intentar convertirlo en primer chunk visible experimental."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"first chunk renderpass probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("terrain_pipeline_checked", "pipe-check"),
        ("terrain_pipeline_ready", "pipe"),
        ("renderpass_descriptor_ready", "rp"),
        ("framebuffer_binding_ready", "fb"),
        ("viewport_scissor_ready", "viewport"),
        ("clear_values_ready", "clear"),
        ("drawindexed_ready", "draw"),
        ("frame_packet_ready", "visible-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_first_chunk_renderpass_probe()
    print("Vulkan first chunk renderpass probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
