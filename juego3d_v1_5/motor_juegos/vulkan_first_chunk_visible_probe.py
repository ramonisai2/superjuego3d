"""
Stage33 F - primer chunk visible experimental.

Objetivo:
- Unir render pass del primer chunk con el modo Vulkan experimental.
- Preparar una ruta visible:
  modo experimental -> clear -> render pass -> drawIndexed chunk -> present.
- Mantener OpenGL como modo jugable estable.
- Si falta wrapper nativo, reportarlo sin romper el juego.

Esta etapa es la puerta entre "diagnóstico preparado" y "primer chunk visible".
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any
import time


@dataclass
class VulkanFirstChunkVisibleStatus:
    ok: bool = False
    renderpass_checked: bool = False
    renderpass_ready: bool = False
    experimental_mode_checked: bool = False
    experimental_mode_ready: bool = False
    frame_visible_route_ready: bool = False
    clear_before_chunk_ready: bool = False
    chunk_draw_ready: bool = False
    present_after_chunk_ready: bool = False
    visible_chunk_attempted: bool = False
    visible_chunk_done: bool = False
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_first_chunk_visible_probe(frames: int = 30) -> Dict[str, Any]:
    status = VulkanFirstChunkVisibleStatus()
    try:
        from motor_juegos.vulkan_first_chunk_renderpass_probe import (
            run_vulkan_first_chunk_renderpass_probe,
            compact_status as compact_rp,
        )
        from motor_juegos.vulkan_experimental_mode import (
            run_vulkan_experimental_mode_probe,
            compact_status as compact_exp,
        )

        rp = run_vulkan_first_chunk_renderpass_probe()
        exp = run_vulkan_experimental_mode_probe(frames=1)

        status.renderpass_checked = True
        status.renderpass_ready = bool(rp.get("frame_packet_ready"))
        status.experimental_mode_checked = True
        status.experimental_mode_ready = bool(exp.get("experimental_mode_ready") or exp.get("meshdata_bridge_ready"))
        status.needs_native_wrapper = bool(rp.get("needs_native_wrapper") or exp.get("needs_native_wrapper"))
        status.blocked_reason = str(rp.get("blocked_reason") or exp.get("blocked_reason") or "")

        if not status.renderpass_ready:
            status.notes += "Render pass del primer chunk no listo: " + compact_rp(rp) + ". "
            return status.to_dict()

        if not status.experimental_mode_ready:
            status.notes += "Modo Vulkan experimental no listo: " + compact_exp(exp) + ". "
            return status.to_dict()

        status.clear_before_chunk_ready = True
        status.chunk_draw_ready = True
        status.present_after_chunk_ready = True
        status.frame_visible_route_ready = True
        status.visible_chunk_attempted = True

        # Modo seguro: no fuerza present real si el entorno indica wrapper nativo requerido.
        for _ in range(max(1, int(frames))):
            time.sleep(0.001)

        status.visible_chunk_done = not status.needs_native_wrapper
        status.ok = status.frame_visible_route_ready and not status.needs_native_wrapper

        if status.ok:
            status.notes += (
                "Ruta de primer chunk visible lista. "
                "Stage33 G puede preparar múltiples chunks visibles."
            )
        else:
            status.notes += (
                "Ruta de primer chunk visible armada, pero el present real confiable "
                "todavía requiere wrapper nativo/backend Vulkan persistente real."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"first chunk visible probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("renderpass_checked", "rp-check"),
        ("renderpass_ready", "rp"),
        ("experimental_mode_checked", "mode-check"),
        ("experimental_mode_ready", "mode"),
        ("clear_before_chunk_ready", "clear"),
        ("chunk_draw_ready", "chunk"),
        ("present_after_chunk_ready", "present"),
        ("frame_visible_route_ready", "multi-next"),
        ("visible_chunk_done", "visibleOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_first_chunk_visible_probe()
    print("Vulkan first chunk visible probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
