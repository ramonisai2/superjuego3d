"""
Stage32 Vulkan N - diagnóstico SDL/pygame para surface Vulkan.

Objetivo:
- Revisar si el entorno tiene pygame/SDL2 suficiente para intentar
  conectar Vulkan con una ventana real.
- No crea un VkSurfaceKHR todavía para evitar crasheos por bindings incompletos.
- Genera un reporte claro antes de Stage32 Vulkan O.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import ctypes.util
import os
import platform
import sys


@dataclass
class VulkanSurfaceReadiness:
    ok_for_next_probe: bool = False
    pygame_imported: bool = False
    pygame_version: str = ""
    sdl_version: str = ""
    video_driver: str = ""
    platform: str = ""
    vulkan_imported: bool = False
    vulkan_instance_ok: bool = False
    gpu_count: int = 0
    sdl2_library: str = ""
    window_probe_safe: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _probe_vulkan(stats: VulkanSurfaceReadiness) -> None:
    try:
        import vulkan as vk  # type: ignore
        stats.vulkan_imported = True
    except Exception as exc:
        stats.notes += f"Vulkan import fallo: {exc}; "
        return

    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Surface Readiness",
            applicationVersion=1,
            pEngineName="JUEGO Engine",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        stats.vulkan_instance_ok = True
        gpus = vk.vkEnumeratePhysicalDevices(instance)
        stats.gpu_count = len(gpus)
        vk.vkDestroyInstance(instance, None)
    except Exception as exc:
        stats.notes += f"Vulkan instance/GPU fallo: {exc}; "


def run_surface_readiness_probe(create_tiny_window: bool = False) -> Dict[str, Any]:
    stats = VulkanSurfaceReadiness()
    stats.platform = platform.platform()
    stats.sdl2_library = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0") or ""

    try:
        import pygame
        stats.pygame_imported = True
        stats.pygame_version = getattr(pygame, "version", None).ver if hasattr(pygame, "version") else str(pygame.version.ver)
        try:
            stats.sdl_version = ".".join(map(str, pygame.get_sdl_version()))
        except Exception:
            stats.sdl_version = "unknown"

        if create_tiny_window:
            # Ventana oculta/minima para detectar driver sin dejar el juego colgado.
            os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
            pygame.init()
            try:
                pygame.display.set_mode((64, 64), pygame.HIDDEN)
            except Exception:
                pygame.display.set_mode((64, 64))
            try:
                stats.video_driver = pygame.display.get_driver()
            except Exception:
                stats.video_driver = "unknown"
            pygame.display.quit()
            pygame.quit()
            stats.window_probe_safe = True
        else:
            stats.window_probe_safe = False
            stats.video_driver = os.environ.get("SDL_VIDEODRIVER", "") or "not-created"
    except Exception as exc:
        stats.notes += f"pygame/SDL probe fallo: {exc}; "

    _probe_vulkan(stats)

    stats.ok_for_next_probe = (
        stats.pygame_imported
        and stats.vulkan_imported
        and stats.vulkan_instance_ok
        and stats.gpu_count > 0
    )
    if stats.ok_for_next_probe:
        stats.notes += "Listo para intentar Stage32 Vulkan O con surface real controlado. "
    else:
        stats.notes += "Aun no conviene crear surface real; revisar pygame/vulkan/GPU. "
    return stats.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, short in [
        ("pygame_imported", "pg"),
        ("vulkan_imported", "vk"),
        ("vulkan_instance_ok", "inst"),
        ("ok_for_next_probe", "ready"),
        ("window_probe_safe", "win"),
    ]:
        if stats.get(key):
            flags.append(short)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_surface_readiness_probe(create_tiny_window=True)
    print("Surface readiness:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
