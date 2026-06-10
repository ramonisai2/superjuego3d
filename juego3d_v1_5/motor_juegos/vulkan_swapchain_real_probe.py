"""
Stage32 Vulkan T - swapchain real probe.

Objetivo:
- Reutilizar la ruta de SDL2 direct window + SDL_Vulkan_CreateSurface.
- Si se logra crear surface, consultar capacidades/formats/present modes.
- Preparar un plan de VkSwapchainKHR real.
- Si no hay surface, reportar bloqueo claro para wrapper nativo.

OpenGL sigue como modo jugable.
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
class VulkanSwapchainRealResult:
    ok: bool = False
    sdl2_found: bool = False
    window_created: bool = False
    required_extensions: str = ""
    vulkan_imported: bool = False
    instance_created: bool = False
    surface_created: bool = False
    physical_devices: int = 0
    selected_device_index: int = -1
    graphics_queue_family: int = -1
    present_queue_family: int = -1
    surface_caps_checked: bool = False
    formats_checked: bool = False
    present_modes_checked: bool = False
    format_count: int = 0
    present_mode_count: int = 0
    swapchain_plan_ready: bool = False
    chosen_format: str = ""
    chosen_present_mode: str = ""
    chosen_extent: str = ""
    blocked_by_raw_instance: bool = False
    blocked_by_surface: bool = False
    needs_native_wrapper: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _get_extensions(sdl, window, result):
    if not hasattr(sdl, "SDL_Vulkan_GetInstanceExtensions"):
        result.notes += "SDL_Vulkan_GetInstanceExtensions no disponible; "
        return []
    sdl.SDL_Vulkan_GetInstanceExtensions.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_char_p),
    ]
    sdl.SDL_Vulkan_GetInstanceExtensions.restype = ctypes.c_int
    count = ctypes.c_uint(0)
    if sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), None) != 1:
        result.notes += "No se pudo obtener conteo de extensiones; "
        return []
    arr_type = ctypes.c_char_p * count.value
    arr = arr_type()
    if sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), arr) != 1:
        result.notes += "No se pudieron obtener extensiones; "
        return []
    exts = [arr[i].decode("utf-8") for i in range(count.value) if arr[i]]
    result.required_extensions = ",".join(exts)
    return exts


def _try_raw_handle(obj) -> int:
    try:
        return int(obj)
    except Exception:
        pass
    try:
        value = getattr(obj, "value", None)
        if value:
            return int(value)
    except Exception:
        pass
    return 0


def run_swapchain_real_probe(show_window_ms: int = 900) -> Dict[str, Any]:
    result = VulkanSwapchainRealResult()
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.notes += "SDL2 no encontrada; "
        return result.to_dict()
    result.sdl2_found = True

    sdl = None
    window = None
    vk = None
    instance = None
    surface = None

    try:
        sdl = ctypes.CDLL(lib)
        sdl.SDL_Init.argtypes = [ctypes.c_uint32]
        sdl.SDL_Init.restype = ctypes.c_int
        if sdl.SDL_Init(SDL_INIT_VIDEO) != 0:
            result.notes += "SDL_Init fallo; "
            return result.to_dict()

        sdl.SDL_CreateWindow.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
        ]
        sdl.SDL_CreateWindow.restype = ctypes.c_void_p
        window = sdl.SDL_CreateWindow(
            b"JUEGO 1.6 - Vulkan T Swapchain Real Probe",
            SDL_WINDOWPOS_CENTERED_MASK, SDL_WINDOWPOS_CENTERED_MASK,
            640, 360, SDL_WINDOW_SHOWN | SDL_WINDOW_VULKAN,
        )
        if not window:
            result.notes += "SDL_CreateWindow Vulkan fallo; "
            return result.to_dict()
        result.window_created = True

        exts = _get_extensions(sdl, window, result)

        try:
            import vulkan as vk_mod  # type: ignore
            vk = vk_mod
            result.vulkan_imported = True
        except Exception as exc:
            result.notes += f"vulkan import fallo: {exc}; "
            return result.to_dict()

        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Swapchain Real Probe",
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

        raw_instance = _try_raw_handle(instance)
        if raw_instance == 0:
            result.blocked_by_raw_instance = True
            result.needs_native_wrapper = True
            result.notes += "No hay raw VkInstance seguro para ctypes; se requiere wrapper nativo para surface/swapchain real. "
            return result.to_dict()

        if not hasattr(sdl, "SDL_Vulkan_CreateSurface"):
            result.blocked_by_surface = True
            result.notes += "SDL_Vulkan_CreateSurface no disponible; "
            return result.to_dict()

        sdl.SDL_Vulkan_CreateSurface.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint64),
        ]
        sdl.SDL_Vulkan_CreateSurface.restype = ctypes.c_int
        surf_value = ctypes.c_uint64(0)
        ok = sdl.SDL_Vulkan_CreateSurface(
            ctypes.c_void_p(window),
            ctypes.c_void_p(raw_instance),
            ctypes.byref(surf_value),
        )
        if ok != 1 or not surf_value.value:
            result.blocked_by_surface = True
            result.needs_native_wrapper = True
            result.notes += "No se pudo crear VkSurfaceKHR con SDL/ctypes; probable wrapper nativo requerido. "
            return result.to_dict()

        result.surface_created = True
        surface = surf_value.value

        devices = vk.vkEnumeratePhysicalDevices(instance)
        result.physical_devices = len(devices)

        # Nota: en algunos bindings, VkSurfaceKHR crudo no se acepta como handle Python.
        # Intentamos consultas si el binding lo tolera. Si no, dejamos plan.
        selected = None
        for i, dev in enumerate(devices):
            try:
                props = vk.vkGetPhysicalDeviceQueueFamilyProperties(dev)
                for qi, q in enumerate(props):
                    if q.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                        result.selected_device_index = i
                        result.graphics_queue_family = qi
                        result.present_queue_family = qi
                        selected = dev
                        break
                if selected:
                    break
            except Exception:
                continue

        if selected is None:
            result.notes += "No se encontro queue grafica; "
            return result.to_dict()

        try:
            caps = vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(selected, surface)
            result.surface_caps_checked = True
            extent = getattr(caps, "currentExtent", None)
            if extent:
                result.chosen_extent = f"{extent.width}x{extent.height}"
        except Exception as exc:
            result.notes += f"Caps surface no consultables por binding/raw surface: {exc}; "

        try:
            formats = vk.vkGetPhysicalDeviceSurfaceFormatsKHR(selected, surface)
            result.formats_checked = True
            result.format_count = len(formats)
            if formats:
                fmt = formats[0]
                result.chosen_format = f"{getattr(fmt, 'format', '?')}/{getattr(fmt, 'colorSpace', '?')}"
        except Exception as exc:
            result.notes += f"Formats surface no consultables: {exc}; "

        try:
            modes = vk.vkGetPhysicalDeviceSurfacePresentModesKHR(selected, surface)
            result.present_modes_checked = True
            result.present_mode_count = len(modes)
            if modes:
                result.chosen_present_mode = str(modes[0])
        except Exception as exc:
            result.notes += f"Present modes no consultables: {exc}; "

        result.swapchain_plan_ready = result.surface_created and result.selected_device_index >= 0
        result.ok = result.swapchain_plan_ready
        if result.ok:
            result.notes += "Surface creado y plan de swapchain listo. Stage32 U puede intentar VkSwapchainKHR. "

        if window and hasattr(sdl, "SDL_PumpEvents"):
            start = time.time()
            while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
                sdl.SDL_PumpEvents()
                if hasattr(sdl, "SDL_Delay"):
                    sdl.SDL_Delay(16)
                else:
                    time.sleep(0.016)

    except Exception as exc:
        result.notes += f"swapchain real probe fallo: {exc}; "
    finally:
        # No destruimos surface crudo por seguridad si binding no lo maneja bien.
        try:
            if vk is not None and instance is not None:
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
        ("window_created", "win"),
        ("vulkan_imported", "vk"),
        ("instance_created", "inst"),
        ("surface_created", "surf"),
        ("surface_caps_checked", "caps"),
        ("formats_checked", "fmt"),
        ("present_modes_checked", "pm"),
        ("swapchain_plan_ready", "swap-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("physical_devices"):
        flags.append(f"gpu{stats.get('physical_devices')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_swapchain_real_probe()
    print("Vulkan swapchain real probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
