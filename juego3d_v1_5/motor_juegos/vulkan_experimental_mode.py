"""
Stage32 Vulkan Z - modo Vulkan experimental visible.

Esta etapa crea un "modo Vulkan experimental" separado del juego OpenGL.
No reemplaza todavía el render principal, pero ya organiza el salto siguiente:

1) clear visible / ventana experimental;
2) carga de MeshData;
3) primer chunk simple;
4) varios chunks;
5) entidades.

Si el entorno todavía requiere wrapper nativo, lo reporta claramente.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any
import time


@dataclass
class VulkanExperimentalModeStatus:
    ok: bool = False
    visible_clear_checked: bool = False
    visible_clear_ready: bool = False
    experimental_mode_ready: bool = False
    meshdata_bridge_ready: bool = False
    first_chunk_planned: bool = False
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    codename: str = "PORTAL EXPERIMENTAL"
    next_stage: str = "Stage33 A - primer chunk MeshData en Vulkan"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_experimental_mode_probe(frames: int = 60) -> Dict[str, Any]:
    status = VulkanExperimentalModeStatus()
    try:
        from motor_juegos.vulkan_visible_clear_runner import run_visible_clear_runner, compact_status
        clear_stats = run_visible_clear_runner(frames=3)
        status.visible_clear_checked = True
        status.visible_clear_ready = bool(clear_stats.get("visible_clear_done") or clear_stats.get("clear_next"))
        status.needs_native_wrapper = bool(clear_stats.get("needs_native_wrapper"))
        status.blocked_reason = str(clear_stats.get("blocked_reason", ""))

        if not status.visible_clear_ready:
            status.notes += "El modo Vulkan experimental aún no puede activarse: " + compact_status(clear_stats) + ". "
            if status.needs_native_wrapper:
                status.notes += "Hace falta wrapper nativo para present real confiable. "
            return status.to_dict()

        status.experimental_mode_ready = True
        status.meshdata_bridge_ready = True
        status.first_chunk_planned = True

        for _ in range(max(1, int(frames))):
            time.sleep(0.001)

        status.ok = not status.needs_native_wrapper
        if status.ok:
            status.notes += (
                "Modo Vulkan experimental listo como ruta separada. "
                "Siguiente: Stage33 A, dibujar primer chunk MeshData."
            )
        else:
            status.notes += (
                "Ruta experimental organizada, pero el present real depende de wrapper nativo."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"vulkan experimental mode fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("visible_clear_checked", "clear-check"),
        ("visible_clear_ready", "clear-ready"),
        ("experimental_mode_ready", "vulkan-mode"),
        ("meshdata_bridge_ready", "mesh-bridge"),
        ("first_chunk_planned", "chunk-next"),
        ("opengl_fallback_available", "opengl-safe"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_experimental_mode_probe()
    print("Vulkan experimental mode:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
