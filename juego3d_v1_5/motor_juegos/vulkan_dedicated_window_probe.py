"""
Stage32 Vulkan P - ventana dedicada Vulkan/SDL surface probe.

Esta etapa intenta acercarse al surface real sin reemplazar el juego OpenGL.
Crea una ventana pygame dedicada y revisa si SDL reporta soporte Vulkan.

Importante:
- Pygame puede no exponer directamente SDL_Window* para crear VkSurfaceKHR.
- Este probe NO debe crashear el juego si faltan extensiones.
- El objetivo es saber si la PC/SDL/Python estan listos para el siguiente paso.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import os
import sys
import time
import ctypes
import ctypes.util


@dataclass
class VulkanDedicatedWindowResult:
    ok: bool = False
    pygame_imported: bool = False
    pygame_window_created: bool = False
    sdl_version: str = ""
    video_driver: str = ""
    vulkan_imported: bool = False
    vulkan_instance_created: bool = False
    gpu_count: int = 0
    sdl2_library_found: bool = False
    sdl2_library_path: str = ""
    sdl_vulkan_functions_found: int = 0
    sdl_vulkan_functions: str = ""
    window_handle_available: bool = False
    surface_creation_ready: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _probe_vulkan(result: VulkanDedicatedWindowResult) -> None:
    try:
        import vulkan as vk  # type: ignore
        result.vulkan_imported = True
    except Exception as exc:
        result.notes += f"vulkan import fallo: {exc}; "
        return

    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Vulkan Dedicated Window Probe",
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
        result.vulkan_instance_created = True
        gpus = vk.vkEnumeratePhysicalDevices(instance)
        result.gpu_count = len(gpus)
        vk.vkDestroyInstance(instance, None)
    except Exception as exc:
        result.notes += f"vk instance/GPU fallo: {exc}; "


def _probe_sdl2(result: VulkanDedicatedWindowResult) -> None:
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.notes += "No se encontro libreria SDL2 por ctypes; "
        return
    result.sdl2_library_found = True
    result.sdl2_library_path = lib
    try:
        sdl = ctypes.CDLL(lib)
        funcs = []
        for name in [
            "SDL_Vulkan_LoadLibrary",
            "SDL_Vulkan_GetInstanceExtensions",
            "SDL_Vulkan_CreateSurface",
            "SDL_Vulkan_GetDrawableSize",
        ]:
            if hasattr(sdl, name):
                funcs.append(name)
        result.sdl_vulkan_functions_found = len(funcs)
        result.sdl_vulkan_functions = ",".join(funcs)
    except Exception as exc:
        result.notes += f"No se pudo abrir SDL2: {exc}; "


def run_dedicated_window_probe(show_window_ms: int = 900) -> Dict[str, Any]:
    result = VulkanDedicatedWindowResult()
    _probe_sdl2(result)
    _probe_vulkan(result)

    try:
        import pygame
        result.pygame_imported = True
        try:
            result.sdl_version = ".".join(map(str, pygame.get_sdl_version()))
        except Exception:
            result.sdl_version = "unknown"

        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.init()
        flags = 0
        # No pedimos OPENGL aqui; queremos saber si una ventana SDL normal puede servir
        # como base para el surface. La creacion real de VkSurfaceKHR se deja para Q.
        screen = pygame.display.set_mode((640, 360), flags)
        pygame.display.set_caption("JUEGO 1.6 - Vulkan P Dedicated Window Probe")
        result.pygame_window_created = True
        try:
            result.video_driver = pygame.display.get_driver()
        except Exception:
            result.video_driver = "unknown"

        # Pygame no garantiza exponer SDL_Window*. Marcamos explicitamente si aparece.
        wm_info = {}
        try:
            wm_info = pygame.display.get_wm_info() or {}
        except Exception:
            wm_info = {}
        # En Windows normalmente devuelve HWND, no SDL_Window*. Sirve para diagnostico.
        result.window_handle_available = bool(wm_info)

        start = time.time()
        while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    break
            screen.fill((20, 24, 32))
            pygame.display.flip()
            time.sleep(0.016)

        pygame.display.quit()
        pygame.quit()
    except Exception as exc:
        result.notes += f"pygame dedicated window fallo: {exc}; "

    result.surface_creation_ready = (
        result.pygame_window_created
        and result.vulkan_imported
        and result.vulkan_instance_created
        and result.gpu_count > 0
        and result.sdl_vulkan_functions_found >= 2
    )
    result.ok = result.surface_creation_ready
    if result.ok:
        result.notes += "Listo para intentar wrapper surface real en Stage32 Q. "
    else:
        result.notes += "Falta soporte o acceso directo a SDL/Vulkan surface. "
    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, label in [
        ("pygame_imported", "pg"),
        ("pygame_window_created", "win"),
        ("vulkan_imported", "vk"),
        ("vulkan_instance_created", "inst"),
        ("sdl2_library_found", "sdl"),
        ("surface_creation_ready", "surf-ready"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    if stats.get("sdl_vulkan_functions_found"):
        flags.append(f"sdlvk{stats.get('sdl_vulkan_functions_found')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_dedicated_window_probe()
    print("Vulkan dedicated window probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
