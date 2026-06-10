"""
Stage32 Vulkan Q - puente controlado SDL/Vulkan surface.

Esta etapa intenta preparar una llamada realista hacia SDL_Vulkan_CreateSurface.
Por seguridad NO fuerza la creacion de surface si pygame no expone SDL_Window*.

Resumen:
- Carga SDL2 via ctypes.
- Verifica funciones SDL_Vulkan_*.
- Crea VkInstance con extensiones solicitadas si puede obtenerlas.
- Detecta si tenemos un puntero SDL_Window real.
- Si no existe puntero SDL_Window, devuelve un plan claro en vez de crashear.

Este modulo es un puente de diagnostico antes de un wrapper nativo.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import ctypes
import ctypes.util
import os
import sys


@dataclass
class SDLSurfaceBridgeResult:
    ok: bool = False
    pygame_ok: bool = False
    window_created: bool = False
    wm_info_keys: str = ""
    has_sdl_window_ptr: bool = False
    sdl2_found: bool = False
    sdl2_path: str = ""
    sdl_vulkan_load: bool = False
    sdl_vulkan_ext: bool = False
    sdl_vulkan_create_surface: bool = False
    vulkan_ok: bool = False
    instance_created: bool = False
    gpu_count: int = 0
    surface_attempted: bool = False
    surface_created: bool = False
    needs_native_wrapper: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_sdl2(result: SDLSurfaceBridgeResult):
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.notes += "SDL2 no encontrada por ctypes; "
        return None
    result.sdl2_found = True
    result.sdl2_path = lib
    try:
        sdl = ctypes.CDLL(lib)
        result.sdl_vulkan_load = hasattr(sdl, "SDL_Vulkan_LoadLibrary")
        result.sdl_vulkan_ext = hasattr(sdl, "SDL_Vulkan_GetInstanceExtensions")
        result.sdl_vulkan_create_surface = hasattr(sdl, "SDL_Vulkan_CreateSurface")
        return sdl
    except Exception as exc:
        result.notes += f"No se pudo cargar SDL2: {exc}; "
        return None


def _create_vulkan_instance(result: SDLSurfaceBridgeResult):
    try:
        import vulkan as vk  # type: ignore
        result.vulkan_ok = True
    except Exception as exc:
        result.notes += f"No se pudo importar vulkan: {exc}; "
        return None, None

    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO SDL Surface Bridge",
            applicationVersion=1,
            pEngineName="JUEGO Engine",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        # Todavia no forzamos extensiones de surface porque SDL_Window* no esta garantizado.
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        result.instance_created = True
        gpus = vk.vkEnumeratePhysicalDevices(instance)
        result.gpu_count = len(gpus)
        return vk, instance
    except Exception as exc:
        result.notes += f"No se pudo crear VkInstance: {exc}; "
        return None, None


def run_sdl_surface_bridge_probe(show_window_ms: int = 600) -> Dict[str, Any]:
    result = SDLSurfaceBridgeResult()
    sdl = _load_sdl2(result)
    vk, instance = _create_vulkan_instance(result)

    try:
        import pygame
        result.pygame_ok = True
        pygame.init()
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.display.set_mode((640, 360))
        pygame.display.set_caption("JUEGO 1.6 - Vulkan Q Surface Bridge")
        result.window_created = True

        try:
            wm_info = pygame.display.get_wm_info() or {}
            result.wm_info_keys = ",".join(sorted(map(str, wm_info.keys())))
            # Pygame suele dar hwnd/window/display, no SDL_Window*. Si aparece algo llamado window,
            # no asumimos que sea SDL_Window, solo lo reportamos.
            result.has_sdl_window_ptr = "sdl_window" in wm_info or "SDL_Window" in wm_info
        except Exception as exc:
            result.notes += f"wm_info fallo: {exc}; "

        # Pequeño pump de eventos para que la ventana se estabilice.
        import time
        start = time.time()
        while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    break
            pygame.display.flip()
            time.sleep(0.016)

        pygame.display.quit()
        pygame.quit()
    except Exception as exc:
        result.notes += f"pygame window fallo: {exc}; "

    # Solo intentar surface si de verdad hay SDL_Window*. En pygame normal casi nunca lo hay.
    if result.has_sdl_window_ptr and sdl is not None and vk is not None and instance is not None and result.sdl_vulkan_create_surface:
        result.surface_attempted = True
        # Por seguridad no hacemos cast ciego a SDL_Window*: si el puntero no es real crashea.
        result.notes += "SDL_Window* reportado, pero surface real queda desactivado hasta wrapper nativo seguro; "
    else:
        result.needs_native_wrapper = True
        result.notes += "No hay SDL_Window* seguro desde pygame; se recomienda wrapper nativo/SDL2 directo para Stage32 R; "

    if vk is not None and instance is not None:
        try:
            vk.vkDestroyInstance(instance, None)
        except Exception:
            pass

    result.ok = (
        result.pygame_ok
        and result.window_created
        and result.sdl2_found
        and result.sdl_vulkan_create_surface
        and result.vulkan_ok
        and result.instance_created
        and result.gpu_count > 0
    )
    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, label in [
        ("pygame_ok", "pg"),
        ("window_created", "win"),
        ("sdl2_found", "sdl"),
        ("sdl_vulkan_create_surface", "sdlSurf"),
        ("vulkan_ok", "vk"),
        ("instance_created", "inst"),
        ("surface_created", "surfOK"),
        ("needs_native_wrapper", "native-next"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_sdl_surface_bridge_probe()
    print("SDL/Vulkan surface bridge:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
