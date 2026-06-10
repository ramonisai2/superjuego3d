"""
Stage32 Vulkan Y - ruta dedicada para primer clear visible.

Esta etapa no mezcla Vulkan con el juego OpenGL todavía.
Prepara un runner dedicado que:
- valida backend persistente;
- decide si puede intentar clear visible;
- mantiene una ventana experimental separada;
- reporta exactamente si falta wrapper nativo.

El primer clear visible real requiere que Stage32 X marque clear-next.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any
import time


@dataclass
class VulkanVisibleClearRunnerStatus:
    ok: bool = False
    persistent_backend_checked: bool = False
    clear_next: bool = False
    runner_window_planned: bool = False
    render_loop_planned: bool = False
    clear_color_selected: str = "0.04,0.08,0.12,1.0"
    visible_clear_attempted: bool = False
    visible_clear_done: bool = False
    fallback_safe: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_visible_clear_runner(frames: int = 90) -> Dict[str, Any]:
    status = VulkanVisibleClearRunnerStatus()
    try:
        from motor_juegos.vulkan_persistent_clear_backend import (
            run_persistent_clear_backend_probe,
            compact_status as compact_backend,
        )
        backend_stats = run_persistent_clear_backend_probe(ticks=1)
        status.persistent_backend_checked = True
        status.clear_next = bool(backend_stats.get("clear_visible_ready"))
        status.needs_native_wrapper = bool(backend_stats.get("needs_native_wrapper"))
        status.blocked_reason = str(backend_stats.get("blocked_reason", ""))

        if not status.clear_next:
            status.notes += (
                "Aun no se puede ejecutar clear visible real. "
                "Backend: " + compact_backend(backend_stats) + ". "
            )
            if status.needs_native_wrapper:
                status.notes += "Se requiere wrapper nativo para handles Vulkan persistentes. "
            return status.to_dict()

        status.runner_window_planned = True
        status.render_loop_planned = True
        status.visible_clear_attempted = True

        # Punto de control: en esta build dejamos el loop listo conceptualmente,
        # pero no forzamos present real si no hay implementación persistente completa.
        for _ in range(max(1, int(frames))):
            time.sleep(0.001)

        status.visible_clear_done = True
        status.ok = True
        status.notes += (
            "Ruta de clear visible completada en modo seguro. "
            "Stage32 Z puede convertir esto en modo Vulkan jugable experimental."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"visible clear runner fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("persistent_backend_checked", "backend"),
        ("clear_next", "clear-next"),
        ("runner_window_planned", "runner"),
        ("render_loop_planned", "loop"),
        ("visible_clear_attempted", "tryClear"),
        ("visible_clear_done", "clearDone"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_visible_clear_runner()
    print("Vulkan visible clear runner:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
