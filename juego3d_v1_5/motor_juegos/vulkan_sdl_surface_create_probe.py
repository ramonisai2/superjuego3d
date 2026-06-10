"""
Stage32 Vulkan S - intento controlado de SDL_Vulkan_CreateSurface real.

Esta es la primera etapa que intenta llegar a un VkSurfaceKHR real usando:
- ventana SDL2 directa creada con SDL_WINDOW_VULKAN;
- extensiones requeridas por SDL_Vulkan_GetInstanceExtensions;
- VkInstance creado con esas extensiones;
- llamada a SDL_Vulkan_CreateSurface.

Seguridad:
- Si los bindings Python de Vulkan no permiten obtener un handle crudo de VkInstance,
  el probe NO crashea; reporta el bloqueo.
- OpenGL sigue siendo el modo jugable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import ctypes
import ctypes.util
import time


SDL_INIT_VIDEO = 0x00000020
SDL_WINDOWPOS_CENTERED_MASK = 0x2FFF0000
SDL_WINDOW_SHOWN = 0x00000004
SDL_WINDOW_VULKAN = 0x10000000


@dataclass
class SDLSurfaceCreateResult:
    ok: bool = False
    sdl2_found: bool = False
    sdl2_path: str = ""
    sdl_init_ok: bool = False
    window_created: bool = False
    window_ptr: str = ""
    got_required_extensions: bool = False
    required_extensions: str = ""
    required_extension_count: int = 0
    vulkan_imported: bool = False
    instance_created: bool = False
    raw_instance_available: bool = False
    surface_attempted: bool = False
    surface_created: bool = False
    surface_handle: str = ""
    gpu_count: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _decode_required_extensions(sdl, window, result: SDLSurfaceCreateResult) -> List[str]:
    if not hasattr(sdl, "SDL_Vulkan_GetInstanceExtensions"):
        result.notes += "SDL_Vulkan_GetInstanceExtensions no existe; "
        return []

    sdl.SDL_Vulkan_GetInstanceExtensions.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_char_p),
    ]
    sdl.SDL_Vulkan_GetInstanceExtensions.restype = ctypes.c_int

    count = ctypes.c_uint(0)
    ok = sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), None)
    if ok != 1 or count.value <= 0:
        result.notes += "No se pudo obtener conteo de extensiones SDL Vulkan; "
        return []

    arr_type = ctypes.c_char_p * count.value
    arr = arr_type()
    ok = sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), arr)
    if ok != 1:
        result.notes += "No se pudieron obtener nombres de extensiones SDL Vulkan; "
        return []

    exts = []
    for i in range(count.value):
        if arr[i]:
            exts.append(arr[i].decode("utf-8"))
    result.got_required_extensions = bool(exts)
    result.required_extension_count = len(exts)
    result.required_extensions = ",".join(exts)
    return exts


def _try_raw_instance_handle(instance) -> int:
    # Los bindings de vulkan en Python varian. En algunos casos el handle puede
    # convertirse a int; en otros no. Nunca hacemos hacks peligrosos.
    try:
        return int(instance)
    except Exception:
        pass
    try:
        value = getattr(instance, "value", None)
        if value:
            return int(value)
    except Exception:
        pass
    return 0


def run_sdl_surface_create_probe(show_window_ms: int = 900) -> Dict[str, Any]:
    result = SDLSurfaceCreateResult()
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.notes += "SDL2 no encontrada; "
        return result.to_dict()

    result.sdl2_found = True
    result.sdl2_path = lib
    sdl = None
    window = None
    vk = None
    instance = None

    try:
        sdl = ctypes.CDLL(lib)
        if not hasattr(sdl, "SDL_Init") or not hasattr(sdl, "SDL_CreateWindow"):
            result.notes += "SDL2 incompleta: faltan SDL_Init/SDL_CreateWindow; "
            return result.to_dict()

        sdl.SDL_Init.argtypes = [ctypes.c_uint32]
        sdl.SDL_Init.restype = ctypes.c_int
        if sdl.SDL_Init(SDL_INIT_VIDEO) == 0:
            result.sdl_init_ok = True
        else:
            result.notes += "SDL_Init fallo; "
            return result.to_dict()

        sdl.SDL_CreateWindow.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
        ]
        sdl.SDL_CreateWindow.restype = ctypes.c_void_p
        window = sdl.SDL_CreateWindow(
            b"JUEGO 1.6 - Vulkan S Surface Create Probe",
            SDL_WINDOWPOS_CENTERED_MASK,
            SDL_WINDOWPOS_CENTERED_MASK,
            640,
            360,
            SDL_WINDOW_SHOWN | SDL_WINDOW_VULKAN,
        )
        if not window:
            result.notes += "SDL_CreateWindow con SDL_WINDOW_VULKAN fallo; "
            return result.to_dict()

        result.window_created = True
        result.window_ptr = hex(int(window))

        exts = _decode_required_extensions(sdl, window, result)

        try:
            import vulkan as vk_mod  # type: ignore
            vk = vk_mod
            result.vulkan_imported = True
        except Exception as exc:
            result.notes += f"vulkan import fallo: {exc}; "
            return result.to_dict()

        try:
            app_info = vk.VkApplicationInfo(
                sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
                pApplicationName="JUEGO Surface Create Probe",
                applicationVersion=1,
                pEngineName="JUEGO Engine",
                engineVersion=1,
                apiVersion=vk.VK_API_VERSION_1_0,
            )
            create_info = vk.VkInstanceCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
                pApplicationInfo=app_info,
                enabledExtensionCount=len(exts),
                ppEnabledExtensionNames=exts,
            )
            instance = vk.vkCreateInstance(create_info, None)
            result.instance_created = True
            try:
                result.gpu_count = len(vk.vkEnumeratePhysicalDevices(instance))
            except Exception:
                result.gpu_count = 0
        except Exception as exc:
            result.notes += f"VkInstance con extensiones SDL fallo: {exc}; "
            return result.to_dict()

        raw_instance = _try_raw_instance_handle(instance)
        result.raw_instance_available = raw_instance != 0

        if raw_instance and hasattr(sdl, "SDL_Vulkan_CreateSurface"):
            sdl.SDL_Vulkan_CreateSurface.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_uint64),
            ]
            sdl.SDL_Vulkan_CreateSurface.restype = ctypes.c_int
            surface = ctypes.c_uint64(0)
            result.surface_attempted = True
            ok = sdl.SDL_Vulkan_CreateSurface(
                ctypes.c_void_p(window),
                ctypes.c_void_p(raw_instance),
                ctypes.byref(surface),
            )
            if ok == 1 and surface.value:
                result.surface_created = True
                result.surface_handle = hex(int(surface.value))
                result.ok = True
                result.notes += "VkSurfaceKHR creado correctamente. "
            else:
                result.notes += "SDL_Vulkan_CreateSurface fue llamado pero no devolvio surface valido. "
        else:
            result.notes += (
                "No se intento surface: falta raw VkInstance compatible con ctypes "
                "o SDL_Vulkan_CreateSurface. "
            )

        if window and hasattr(sdl, "SDL_PumpEvents"):
            start = time.time()
            while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
                sdl.SDL_PumpEvents()
                if hasattr(sdl, "SDL_Delay"):
                    sdl.SDL_Delay(16)
                else:
                    time.sleep(0.016)

    except Exception as exc:
        result.notes += f"surface create probe fallo: {exc}; "
    finally:
        if vk is not None and instance is not None:
            try:
                vk.vkDestroyInstance(instance, None)
            except Exception:
                pass
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

    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, label in [
        ("sdl2_found", "sdl"),
        ("sdl_init_ok", "init"),
        ("window_created", "win"),
        ("got_required_extensions", "ext"),
        ("vulkan_imported", "vk"),
        ("instance_created", "inst"),
        ("raw_instance_available", "raw"),
        ("surface_attempted", "trySurf"),
        ("surface_created", "surfOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("gpu_count"):
        flags.append(f"gpu{stats.get('gpu_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_sdl_surface_create_probe()
    print("SDL Vulkan surface create probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
