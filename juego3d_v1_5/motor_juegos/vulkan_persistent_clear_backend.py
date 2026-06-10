"""
Stage32 Vulkan X - backend Vulkan persistente para clear visible.

Esta etapa deja preparada una clase de sesión Vulkan persistente:
- ventana SDL2 directa;
- instancia;
- surface;
- device;
- swapchain;
- frames;
- plan de acquire/clear/present.

Todavía es defensiva: si Python-vulkan no conserva handles fiables o falta
surface/swapchain, reporta el bloqueo y no rompe OpenGL.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import time


@dataclass
class VulkanPersistentClearStatus:
    ok: bool = False
    initialized: bool = False
    persistent_session_ready: bool = False
    clear_visible_ready: bool = False
    backend_alive: bool = False
    frames_prepared: bool = False
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    stage_u_swapchain: bool = False
    stage_v_frames: bool = False
    stage_w_present_plan: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VulkanPersistentClearBackend:
    """Backend experimental. No reemplaza OpenGL todavía."""

    def __init__(self) -> None:
        self.status = VulkanPersistentClearStatus()
        self.created_at = time.time()
        self.frame_counter = 0

    def initialize(self) -> Dict[str, Any]:
        """Valida prerequisitos y prepara estado persistente."""
        try:
            from motor_juegos.vulkan_swapchain_create_probe import run_swapchain_create_probe
            from motor_juegos.vulkan_swapchain_frame_probe import run_swapchain_frame_probe
            from motor_juegos.vulkan_present_clear_probe import run_present_clear_probe

            u = run_swapchain_create_probe(show_window_ms=0)
            v = run_swapchain_frame_probe(show_window_ms=0)
            w = run_present_clear_probe()

            self.status.stage_u_swapchain = bool(u.get("swapchain_created"))
            self.status.stage_v_frames = bool(v.get("acquire_present_plan_ready"))
            self.status.stage_w_present_plan = bool(w.get("present_planned"))
            self.status.needs_native_wrapper = bool(
                u.get("needs_native_wrapper") or v.get("needs_native_wrapper") or w.get("needs_native_wrapper")
            )
            self.status.blocked_reason = str(
                u.get("blocked_reason") or v.get("blocked_reason") or w.get("blocked_reason") or ""
            )

            if self.status.stage_u_swapchain and self.status.stage_v_frames and self.status.stage_w_present_plan:
                self.status.initialized = True
                self.status.persistent_session_ready = True
                self.status.frames_prepared = True
                self.status.clear_visible_ready = not self.status.needs_native_wrapper
                self.status.backend_alive = True
                self.status.ok = self.status.clear_visible_ready
                if self.status.ok:
                    self.status.notes += (
                        "Sesión persistente lista. La siguiente etapa puede consolidar "
                        "un loop Vulkan separado con clear visible."
                    )
                else:
                    self.status.notes += (
                        "Sesión planificada, pero aún se necesita wrapper nativo para "
                        "handles persistentes seguros."
                    )
            else:
                self.status.notes += (
                    "Faltan prerequisitos Vulkan: swapchain/framebuffers/present plan. "
                    "Ejecuta diagnósticos U, V y W."
                )

        except Exception as exc:
            self.status.blocked_reason = f"exception: {exc}"
            self.status.notes += f"initialize fallo: {exc}; "

        return self.status.to_dict()

    def tick(self) -> Dict[str, Any]:
        """Simula un frame persistente seguro."""
        if not self.status.backend_alive:
            return self.status.to_dict()
        self.frame_counter += 1
        self.status.notes = f"Backend persistente activo, frame simulado {self.frame_counter}."
        return self.status.to_dict()

    def shutdown(self) -> Dict[str, Any]:
        self.status.backend_alive = False
        self.status.notes += " Backend persistente apagado."
        return self.status.to_dict()


def run_persistent_clear_backend_probe(ticks: int = 3) -> Dict[str, Any]:
    backend = VulkanPersistentClearBackend()
    stats = backend.initialize()
    for _ in range(max(0, int(ticks))):
        stats = backend.tick()
        time.sleep(0.03)
    stats = backend.shutdown()
    return stats


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("stage_u_swapchain", "U-swap"),
        ("stage_v_frames", "V-frames"),
        ("stage_w_present_plan", "W-present"),
        ("persistent_session_ready", "persist"),
        ("clear_visible_ready", "clear-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_persistent_clear_backend_probe()
    print("Vulkan persistent clear backend:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
