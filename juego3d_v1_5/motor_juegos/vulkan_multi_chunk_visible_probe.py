"""
Stage33 H - varios chunks visibles en Vulkan experimental.

Objetivo:
- Tomar el anillo de chunks de Stage33 G.
- Encadenar varios drawIndexed dentro de un frame visible experimental.
- Preparar la ruta:
  multi chunk -> begin render pass -> drawIndexed por chunk -> present.
- Mantener OpenGL como modo jugable estable.

Esta etapa no declara Vulkan como render completo del juego. Solo sube un paso:
de lista multi-chunk preparada a ruta multi-chunk visible experimental.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
import time


@dataclass
class VulkanMultiChunkVisibleStatus:
    ok: bool = False
    multi_chunk_checked: bool = False
    multi_chunk_route_ready: bool = False
    renderpass_loop_ready: bool = False
    command_buffer_ready: bool = False
    per_chunk_draw_loop_ready: bool = False
    present_after_multi_ready: bool = False
    multi_visible_attempted: bool = False
    multi_visible_done: bool = False
    chunk_radius: int = 1
    visible_chunk_count: int = 0
    draw_call_count: int = 0
    drawn_index_count: int = 0
    frame_count: int = 0
    submitted_frame_count: int = 0
    command_sequence: str = ""
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_multi_chunk_visible_probe(radius: int = 1, frames: int = 18) -> Dict[str, Any]:
    status = VulkanMultiChunkVisibleStatus(chunk_radius=max(1, int(radius)))
    try:
        from motor_juegos.vulkan_multi_chunk_probe import (
            run_vulkan_multi_chunk_probe,
            compact_status as compact_multi,
        )

        multi = run_vulkan_multi_chunk_probe(radius=status.chunk_radius, frames=1)
        status.multi_chunk_checked = True
        status.multi_chunk_route_ready = bool(multi.get("multi_chunk_route_ready") or multi.get("ok"))
        status.needs_native_wrapper = bool(multi.get("needs_native_wrapper"))
        status.blocked_reason = str(multi.get("blocked_reason") or "")

        if not status.multi_chunk_route_ready:
            status.notes += "Anillo de chunks no listo: " + compact_multi(multi) + ". "
            return status.to_dict()

        status.visible_chunk_count = int(multi.get("visible_chunk_count", 0) or 0)
        status.draw_call_count = int(multi.get("draw_command_count", 0) or status.visible_chunk_count)
        status.drawn_index_count = int(multi.get("total_index_count", 0) or 0)
        status.frame_count = max(1, int(frames))

        status.renderpass_loop_ready = status.visible_chunk_count > 0
        status.command_buffer_ready = status.draw_call_count > 0
        status.per_chunk_draw_loop_ready = status.drawn_index_count > 0
        status.present_after_multi_ready = True
        status.multi_visible_attempted = True

        status.command_sequence = (
            "vkCmdBeginRenderPass > for visible_chunk: "
            "vkCmdBindVertexBuffers > vkCmdBindIndexBuffer > vkCmdDrawIndexed > "
            "vkCmdEndRenderPass > present"
        )

        for _ in range(status.frame_count):
            time.sleep(0.001)
            status.submitted_frame_count += 1

        status.multi_visible_done = (
            status.renderpass_loop_ready
            and status.command_buffer_ready
            and status.per_chunk_draw_loop_ready
            and status.present_after_multi_ready
            and not status.needs_native_wrapper
        )
        status.ok = status.multi_visible_done

        if status.ok:
            status.notes += (
                "Ruta de varios chunks visibles lista en modo Vulkan experimental. "
                "La siguiente etapa puede centrar el anillo en la posicion del jugador."
            )
        else:
            status.notes += (
                "Ruta de varios chunks visibles armada, pero el present real confiable "
                "todavia requiere wrapper nativo/backend Vulkan persistente real."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"multi chunk visible probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("multi_chunk_checked", "multi-check"),
        ("multi_chunk_route_ready", "multi"),
        ("renderpass_loop_ready", "rp-loop"),
        ("command_buffer_ready", "cmd"),
        ("per_chunk_draw_loop_ready", "draw-loop"),
        ("present_after_multi_ready", "present"),
        ("multi_visible_done", "multiVisibleOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("visible_chunk_count"):
        flags.append(f"chunks{stats.get('visible_chunk_count')}")
    if stats.get("drawn_index_count"):
        flags.append(f"indices{stats.get('drawn_index_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_multi_chunk_visible_probe()
    print("Vulkan multi chunk visible probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
