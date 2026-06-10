"""
Stage32 Vulkan M - estado de modo de render.

Este modulo centraliza el reporte del backend elegido para que los lanzadores,
main.py y los probes Vulkan escriban informacion consistente.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import os
import platform
import sys
from typing import Dict, Any


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "render_backend_status.log"


@dataclass
class RenderModeStatus:
    requested_backend: str
    stable_backend: str
    is_vulkan_requested: bool
    is_experimental: bool
    python: str
    platform: str
    executable: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compact(self) -> str:
        tag = "VULKAN-EXP" if self.is_vulkan_requested else "OPENGL"
        return f"{tag} requested={self.requested_backend} stable={self.stable_backend}"

    def display_name(self) -> str:
        return "VULKAN EXPERIMENTAL" if self.is_vulkan_requested else "OPENGL ESTABLE"

    def hud_label(self) -> str:
        return f"Render: {self.display_name()}"


def get_render_mode_status() -> RenderModeStatus:
    requested = os.environ.get("JUEGO_RENDER_BACKEND", "opengl").strip().lower() or "opengl"
    vulkan_aliases = {
        "vulkan",
        "vulkan_probe",
        "vulkan_clear",
        "vulkan_triangle",
        "vulkan_chunk",
        "vulkan_memory",
        "vulkan_staging",
        "vulkan_command",
        "vulkan_draw",
        "vulkan_shader",
        "vulkan_shader_module",
        "vulkan_pipeline_real",
        "vulkan_framebuffer_draw",
        "vulkan_present",
    }
    is_vk = requested in vulkan_aliases or requested.startswith("vulkan")
    stable = "opengl" if not is_vk else "opengl_fallback"
    notes = "OpenGL jugable estable." if not is_vk else "Vulkan experimental; OpenGL puede seguir como respaldo."
    return RenderModeStatus(
        requested_backend=requested,
        stable_backend=stable,
        is_vulkan_requested=is_vk,
        is_experimental=is_vk,
        python=sys.version.split()[0],
        platform=platform.platform(),
        executable=sys.executable,
        notes=notes,
    )


def write_render_mode_log(extra: str = "") -> RenderModeStatus:
    status = get_render_mode_status()
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write("=" * 72 + "\n")
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
            f.write(status.compact() + "\n")
            f.write(f"python={status.python}\n")
            f.write(f"platform={status.platform}\n")
            f.write(f"executable={status.executable}\n")
            f.write(f"notes={status.notes}\n")
            if extra:
                f.write(f"extra={extra}\n")
    except Exception:
        pass
    return status


def print_render_mode_banner(extra: str = "") -> RenderModeStatus:
    status = write_render_mode_log(extra)
    print("=" * 48)
    print(f"MODO RENDER: {status.display_name()}")
    print(f"Backend pedido: {status.requested_backend}")
    print(status.notes)
    print("=" * 48)
    return status


if __name__ == "__main__":
    st = write_render_mode_log("manual status check")
    print(st.compact())
    print(st.to_dict())
    print("Log:", LOG_FILE)
