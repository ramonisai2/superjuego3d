"""
Stage32 Vulkan R - SDL2 direct window / native bridge prep.

Esta prueba intenta abrir una ventana con SDL2 via ctypes, no con pygame.
La meta es obtener un SDL_Window* real y verificar si SDL_Vulkan_CreateSurface
ya seria posible con un wrapper mas directo.

Sigue siendo diagnostico seguro:
- OpenGL no se reemplaza.
- No fuerza VkSurfaceKHR si faltan extensiones.
- Reporta si el siguiente paso puede intentar surface real.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import ctypes
import ctypes.util
import time
import os


SDL_INIT_VIDEO = 0x00000020
SDL_WINDOWPOS_CENTERED_MASK = 0x2FFF0000
SDL_WINDOW_SHOWN = 0x00000004
SDL_WINDOW_VULKAN = 0x10000000


@dataclass
class SDL2DirectProbeResult:
    ok: bool = False
    sdl2_found: bool = False
    sdl2_path: str = ""
    sdl_init_ok: bool = False
    sdl_window_created: bool = False
    sdl_window_ptr: str = ""
    sdl_vulkan_functions_found: int = 0
    sdl_vulkan_functions: str = ""
    vulkan_imported: bool = False
    vulkan_instance_created: bool = False
    gpu_count: int = 0
    ready_for_surface_attempt: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _probe_vulkan(result: SDL2DirectProbeResult) -> None:
    try:
        import vulkan as vk  # type: ignore
        result.vulkan_imported = True
    except Exception as exc:
        result.notes += f"vulkan import fallo: {exc}; "
        return

    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO SDL2 Direct Probe",
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
        result.notes += f"VkInstance/GPU fallo: {exc}; "


def run_sdl2_direct_probe(show_window_ms: int = 900) -> Dict[str, Any]:
    result = SDL2DirectProbeResult()
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.notes += "No se encontro SDL2 con ctypes.util.find_library; "
        _probe_vulkan(result)
        return result.to_dict()

    result.sdl2_found = True
    result.sdl2_path = lib

    sdl = None
    window = None
    try:
        sdl = ctypes.CDLL(lib)
        funcs = []
        for name in [
            "SDL_Init",
            "SDL_CreateWindow",
            "SDL_DestroyWindow",
            "SDL_Quit",
            "SDL_PumpEvents",
            "SDL_Delay",
            "SDL_Vulkan_LoadLibrary",
            "SDL_Vulkan_GetInstanceExtensions",
            "SDL_Vulkan_CreateSurface",
            "SDL_Vulkan_GetDrawableSize",
        ]:
            if hasattr(sdl, name):
                funcs.append(name)
        vkfuncs = [f for f in funcs if f.startswith("SDL_Vulkan")]
        result.sdl_vulkan_functions_found = len(vkfuncs)
        result.sdl_vulkan_functions = ",".join(vkfuncs)

        sdl.SDL_Init.argtypes = [ctypes.c_uint32]
        sdl.SDL_Init.restype = ctypes.c_int
        if sdl.SDL_Init(SDL_INIT_VIDEO) == 0:
            result.sdl_init_ok = True
        else:
            result.notes += "SDL_Init fallo; "

        if result.sdl_init_ok and hasattr(sdl, "SDL_CreateWindow"):
            sdl.SDL_CreateWindow.argtypes = [
                ctypes.c_char_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_uint32,
            ]
            sdl.SDL_CreateWindow.restype = ctypes.c_void_p
            window = sdl.SDL_CreateWindow(
                b"JUEGO 1.6 - Vulkan R SDL2 Direct Probe",
                SDL_WINDOWPOS_CENTERED_MASK,
                SDL_WINDOWPOS_CENTERED_MASK,
                640,
                360,
                SDL_WINDOW_SHOWN | SDL_WINDOW_VULKAN,
            )
            if window:
                result.sdl_window_created = True
                result.sdl_window_ptr = hex(int(window))

        if window and hasattr(sdl, "SDL_PumpEvents"):
            start = time.time()
            while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
                sdl.SDL_PumpEvents()
                if hasattr(sdl, "SDL_Delay"):
                    sdl.SDL_Delay(16)
                else:
                    time.sleep(0.016)

    except Exception as exc:
        result.notes += f"SDL2 direct probe fallo: {exc}; "
    finally:
        try:
            if sdl is not None and window and hasattr(sdl, "SDL_DestroyWindow"):
                sdl.SDL_DestroyWindow(ctypes.c_void_p(window))
        except Exception:
            pass
        try:
            if sdl is not None and hasattr(sdl, "SDL_Quit"):
                sdl.SDL_Quit()
        except Exception:
            pass

    _probe_vulkan(result)
    result.ready_for_surface_attempt = (
        result.sdl2_found
        and result.sdl_init_ok
        and result.sdl_window_created
        and result.sdl_vulkan_functions_found >= 2
        and result.vulkan_imported
        and result.vulkan_instance_created
        and result.gpu_count > 0
    )
    result.ok = result.ready_for_surface_attempt
    if result.ok:
        result.notes += "Listo para Stage32 S: intentar SDL_Vulkan_CreateSurface real con SDL_Window* directo. "
    else:
        result.notes += "Aun falta SDL2/Vulkan/ventana para surface real. "
    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, label in [
        ("sdl2_found", "sdl"),
        ("sdl_init_ok", "init"),
        ("sdl_window_created", "winptr"),
        ("vulkan_imported", "vk"),
        ("vulkan_instance_created", "inst"),
        ("ready_for_surface_attempt", "surface-next"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    if stats.get("sdl_vulkan_functions_found"):
        flags.append(f"sdlvk{stats.get('sdl_vulkan_functions_found')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_sdl2_direct_probe()
    print("SDL2 direct Vulkan probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
