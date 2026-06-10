"""
Stage32 Vulkan W - acquire / clear / present probe.

Objetivo:
- Preparar la ruta del primer present real.
- Si Stage32 U/V logran swapchain y framebuffers, este probe describe y valida
  la secuencia:
    acquire image -> command buffer -> clear color -> submit -> present.
- Por seguridad, no intenta hacer un present destructivo si los handles de
  Python-vulkan no son confiables.

OpenGL sigue siendo la ruta jugable estable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class VulkanPresentClearResult:
    ok: bool = False
    swapchain_ready: bool = False
    framebuffers_ready: bool = False
    acquire_planned: bool = False
    command_buffer_planned: bool = False
    clear_pass_planned: bool = False
    submit_planned: bool = False
    present_planned: bool = False
    can_attempt_real_present: bool = False
    real_present_attempted: bool = False
    real_present_done: bool = False
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_present_clear_probe() -> Dict[str, Any]:
    result = VulkanPresentClearResult()
    try:
        from motor_juegos.vulkan_swapchain_frame_probe import run_swapchain_frame_probe
        frame_stats = run_swapchain_frame_probe(show_window_ms=0)
    except Exception as exc:
        result.blocked_reason = f"frame probe import/run failed: {exc}"
        result.notes += result.blocked_reason + "; "
        return result.to_dict()

    result.swapchain_ready = bool(frame_stats.get("swapchain_created"))
    result.framebuffers_ready = bool(frame_stats.get("framebuffers_created", 0))
    result.needs_native_wrapper = bool(frame_stats.get("needs_native_wrapper"))
    result.blocked_reason = str(frame_stats.get("blocked_reason", ""))

    if not result.swapchain_ready:
        result.notes += "No hay swapchain listo; primero Stage32 U debe marcar swapOK. "
        return result.to_dict()

    if not result.framebuffers_ready:
        result.notes += "No hay framebuffers listos; primero Stage32 V debe marcar present-next. "
        return result.to_dict()

    result.acquire_planned = True
    result.command_buffer_planned = True
    result.clear_pass_planned = True
    result.submit_planned = True
    result.present_planned = True

    # Esta etapa prepara el present real, pero no lo fuerza si el backend Python
    # no puede conservar handles confiables entre probes.
    result.can_attempt_real_present = not result.needs_native_wrapper
    if result.can_attempt_real_present:
        result.notes += (
            "Ruta acquire/clear/present planificada. "
            "Stage32 X puede consolidar handles persistentes para intentar present real visible. "
        )
        result.ok = True
    else:
        result.notes += (
            "Ruta planificada, pero se requiere wrapper nativo o backend persistente "
            "para present real confiable. "
        )

    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, label in [
        ("swapchain_ready", "swap"),
        ("framebuffers_ready", "fb"),
        ("acquire_planned", "acq"),
        ("clear_pass_planned", "clear"),
        ("submit_planned", "sub"),
        ("present_planned", "present"),
        ("can_attempt_real_present", "real-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_present_clear_probe()
    print("Vulkan present clear probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
