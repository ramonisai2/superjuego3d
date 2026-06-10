"""
Stage32 Vulkan O - intento controlado de VkSurfaceKHR real.

No reemplaza OpenGL. Intenta preparar/crear surface Vulkan solo en modo diagnostico.
Como pygame/SDL en Python puede no exponer directamente el puntero SDL_Window,
el probe esta disenado para fallar seguro y reportar exactamente que falta.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import ctypes
import ctypes.util
import os
import platform


@dataclass
class VulkanRealSurfaceResult:
    ok: bool = False
    pygame_imported: bool = False
    pygame_window_created: bool = False
    pygame_sdl2_available: bool = False
    vulkan_imported: bool = False
    vulkan_instance_created: bool = False
    gpu_count: int = 0
    sdl2_library_found: bool = False
    sdl_vulkan_functions_found: bool = False
    sdl_window_pointer_available: bool = False
    surface_created: bool = False
    surface_destroyed: bool = False
    platform: str = ""
    video_driver: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_sdl2(stats: VulkanRealSurfaceResult):
    libname = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not libname:
        stats.notes += "No se encontro SDL2 dinamico; "
        return None
    try:
        lib = ctypes.CDLL(libname)
        stats.sdl2_library_found = True
        has = all(hasattr(lib, name) for name in ["SDL_Vulkan_CreateSurface", "SDL_Vulkan_GetInstanceExtensions"])
        stats.sdl_vulkan_functions_found = has
        if not has:
            stats.notes += "SDL2 existe pero no expone funciones Vulkan; "
        return lib
    except Exception as exc:
        stats.notes += f"No se pudo cargar SDL2: {exc}; "
        return None


def _try_get_sdl_window_pointer(stats: VulkanRealSurfaceResult, pygame_module):
    """Intentos seguros. Pygame normalmente devuelve HWND/X11, no SDL_Window*."""
    try:
        info = pygame_module.display.get_wm_info()
        # Esto NO suele ser SDL_Window*, pero lo registramos para diagnostico.
        for key in ("window", "wmwindow", "window_handle"):
            if key in info and info[key]:
                stats.notes += f"pygame wm_info trae {key}, pero puede no ser SDL_Window*; "
                break
    except Exception as exc:
        stats.notes += f"wm_info fallo: {exc}; "

    try:
        import pygame._sdl2 as sdl2  # type: ignore
        stats.pygame_sdl2_available = True
        # pygame._sdl2 no garantiza exponer puntero bruto SDL_Window.
        stats.notes += "pygame._sdl2 disponible; falta confirmar puntero SDL_Window bruto; "
    except Exception as exc:
        stats.notes += f"pygame._sdl2 no disponible/expuesto: {exc}; "
    return None


def run_real_surface_probe(create_window: bool = True, attempt_create_surface: bool = False) -> Dict[str, Any]:
    stats = VulkanRealSurfaceResult(platform=platform.platform())
    sdl2 = _load_sdl2(stats)

    try:
        import pygame
        stats.pygame_imported = True
        if create_window:
            pygame.init()
            os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
            flags = 0
            # NO usamos OPENGL aqui; es solo diagnostico de ventana.
            try:
                pygame.display.set_mode((320, 180), flags)
                stats.pygame_window_created = True
                try:
                    stats.video_driver = pygame.display.get_driver()
                except Exception:
                    stats.video_driver = "unknown"
            except Exception as exc:
                stats.notes += f"No se pudo crear ventana pygame: {exc}; "
        _try_get_sdl_window_pointer(stats, pygame)
    except Exception as exc:
        stats.notes += f"pygame fallo: {exc}; "
        pygame = None  # type: ignore

    try:
        import vulkan as vk  # type: ignore
        stats.vulkan_imported = True
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Stage32 Vulkan O Surface Real Probe",
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
        stats.vulkan_instance_created = True
        gpus = vk.vkEnumeratePhysicalDevices(instance)
        stats.gpu_count = len(gpus)

        if attempt_create_surface:
            # Por seguridad no se llama SDL_Vulkan_CreateSurface sin SDL_Window* real.
            stats.notes += "Surface real no creado: falta SDL_Window* seguro desde pygame; "
        else:
            stats.notes += "Surface real preparado en modo diagnostico; intento destructivo desactivado; "

        vk.vkDestroyInstance(instance, None)
    except Exception as exc:
        stats.notes += f"Vulkan instance/surface probe fallo: {exc}; "

    try:
        if create_window and 'pygame' in globals():
            pass
    except Exception:
        pass
    try:
        import pygame as _pg
        if stats.pygame_window_created:
            _pg.display.quit()
            _pg.quit()
    except Exception:
        pass

    stats.ok = stats.pygame_imported and stats.vulkan_imported and stats.vulkan_instance_created and stats.gpu_count > 0
    return stats.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, short in [
        ("pygame_imported", "pg"),
        ("pygame_window_created", "win"),
        ("sdl2_library_found", "sdl2"),
        ("sdl_vulkan_functions_found", "sdlvk"),
        ("vulkan_imported", "vk"),
        ("vulkan_instance_created", "inst"),
        ("surface_created", "surf"),
    ]:
        if stats.get(key):
            flags.append(short)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    res = run_real_surface_probe(create_window=True, attempt_create_surface=False)
    print("Real surface probe:", compact_status(res))
    for k, v in res.items():
        print(f"{k}: {v}")
