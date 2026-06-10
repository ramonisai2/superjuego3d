"""
Stage32 Vulkan U - intento controlado de VkSwapchainKHR real.

Objetivo:
- Crear ventana SDL2 con SDL_WINDOW_VULKAN.
- Crear VkInstance con extensiones SDL.
- Crear VkSurfaceKHR si el binding/handle lo permite.
- Consultar surface capabilities/formats/present modes.
- Intentar crear VkDevice con VK_KHR_swapchain.
- Preparar/crear VkSwapchainKHR si todo lo anterior funciona.

Seguridad:
- Si Python-vulkan no acepta handles crudos, no crashea: reporta native-wrapper.
- OpenGL sigue siendo la ruta jugable.
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
class VulkanSwapchainCreateResult:
    ok: bool = False
    sdl2_found: bool = False
    window_created: bool = False
    extensions: str = ""
    vulkan_imported: bool = False
    instance_created: bool = False
    surface_created: bool = False
    physical_devices: int = 0
    device_selected: bool = False
    graphics_queue_family: int = -1
    present_queue_family: int = -1
    device_created: bool = False
    swapchain_ext_enabled: bool = False
    caps_checked: bool = False
    formats_checked: bool = False
    present_modes_checked: bool = False
    swapchain_create_attempted: bool = False
    swapchain_created: bool = False
    swapchain_handle: str = ""
    chosen_format: str = ""
    chosen_present_mode: str = ""
    chosen_extent: str = ""
    image_count: int = 0
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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


def _get_extensions(sdl, window, result):
    sdl.SDL_Vulkan_GetInstanceExtensions.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_char_p),
    ]
    sdl.SDL_Vulkan_GetInstanceExtensions.restype = ctypes.c_int
    count = ctypes.c_uint(0)
    if sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), None) != 1:
        result.blocked_reason = "SDL extension count failed"
        return []
    arr_type = ctypes.c_char_p * count.value
    arr = arr_type()
    if sdl.SDL_Vulkan_GetInstanceExtensions(ctypes.c_void_p(window), ctypes.byref(count), arr) != 1:
        result.blocked_reason = "SDL extension names failed"
        return []
    exts = [arr[i].decode("utf-8") for i in range(count.value) if arr[i]]
    result.extensions = ",".join(exts)
    return exts


def run_swapchain_create_probe(show_window_ms: int = 900) -> Dict[str, Any]:
    result = VulkanSwapchainCreateResult()
    lib = ctypes.util.find_library("SDL2") or ctypes.util.find_library("SDL2-2.0")
    if not lib:
        result.blocked_reason = "SDL2 not found"
        result.notes += "SDL2 no encontrada; "
        return result.to_dict()
    result.sdl2_found = True

    sdl = None
    window = None
    vk = None
    instance = None
    device = None
    surface_raw = 0
    swapchain = None

    try:
        sdl = ctypes.CDLL(lib)
        required_sdl_funcs = ["SDL_Init", "SDL_CreateWindow", "SDL_Vulkan_GetInstanceExtensions", "SDL_Vulkan_CreateSurface"]
        missing = [name for name in required_sdl_funcs if not hasattr(sdl, name)]
        if missing:
            result.blocked_reason = "Missing SDL funcs: " + ",".join(missing)
            result.notes += result.blocked_reason + "; "
            return result.to_dict()

        sdl.SDL_Init.argtypes = [ctypes.c_uint32]
        sdl.SDL_Init.restype = ctypes.c_int
        if sdl.SDL_Init(SDL_INIT_VIDEO) != 0:
            result.blocked_reason = "SDL_Init failed"
            return result.to_dict()

        sdl.SDL_CreateWindow.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
        ]
        sdl.SDL_CreateWindow.restype = ctypes.c_void_p
        window = sdl.SDL_CreateWindow(
            b"JUEGO 1.6 - Vulkan U Swapchain Create Probe",
            SDL_WINDOWPOS_CENTERED_MASK, SDL_WINDOWPOS_CENTERED_MASK,
            640, 360, SDL_WINDOW_SHOWN | SDL_WINDOW_VULKAN,
        )
        if not window:
            result.blocked_reason = "SDL_CreateWindow Vulkan failed"
            return result.to_dict()
        result.window_created = True

        exts = _get_extensions(sdl, window, result)
        if not exts:
            result.notes += "No hay extensiones Vulkan SDL; "
            return result.to_dict()

        try:
            import vulkan as vk_mod  # type: ignore
            vk = vk_mod
            result.vulkan_imported = True
        except Exception as exc:
            result.blocked_reason = f"vulkan import failed: {exc}"
            result.notes += result.blocked_reason + "; "
            return result.to_dict()

        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Swapchain Create Probe",
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
            result.needs_native_wrapper = True
            result.blocked_reason = "No raw VkInstance handle from python binding"
            result.notes += "No hay raw VkInstance seguro; wrapper nativo requerido para surface/swapchain real. "
            return result.to_dict()

        sdl.SDL_Vulkan_CreateSurface.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
        sdl.SDL_Vulkan_CreateSurface.restype = ctypes.c_int
        surface_val = ctypes.c_uint64(0)
        ok = sdl.SDL_Vulkan_CreateSurface(ctypes.c_void_p(window), ctypes.c_void_p(raw_instance), ctypes.byref(surface_val))
        if ok != 1 or not surface_val.value:
            result.needs_native_wrapper = True
            result.blocked_reason = "SDL_Vulkan_CreateSurface failed"
            result.notes += "No se pudo crear VkSurfaceKHR; wrapper nativo probable. "
            return result.to_dict()

        surface_raw = surface_val.value
        result.surface_created = True

        devices = vk.vkEnumeratePhysicalDevices(instance)
        result.physical_devices = len(devices)
        if not devices:
            result.blocked_reason = "No Vulkan physical devices"
            return result.to_dict()

        selected_dev = None
        q_index = -1
        for dev in devices:
            try:
                qprops = vk.vkGetPhysicalDeviceQueueFamilyProperties(dev)
                for i, qp in enumerate(qprops):
                    if qp.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                        selected_dev = dev
                        q_index = i
                        break
                if selected_dev:
                    break
            except Exception:
                continue

        if selected_dev is None:
            result.blocked_reason = "No graphics queue family"
            return result.to_dict()

        result.device_selected = True
        result.graphics_queue_family = q_index
        result.present_queue_family = q_index

        # Intentar consultar capacidades de surface con raw handle. Puede fallar según binding.
        caps = None
        formats = []
        modes = []
        try:
            caps = vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(selected_dev, surface_raw)
            result.caps_checked = True
        except Exception as exc:
            result.notes += f"caps failed: {exc}; "

        try:
            formats = vk.vkGetPhysicalDeviceSurfaceFormatsKHR(selected_dev, surface_raw)
            result.formats_checked = True
        except Exception as exc:
            result.notes += f"formats failed: {exc}; "

        try:
            modes = vk.vkGetPhysicalDeviceSurfacePresentModesKHR(selected_dev, surface_raw)
            result.present_modes_checked = True
        except Exception as exc:
            result.notes += f"present modes failed: {exc}; "

        if not (result.caps_checked and result.formats_checked):
            result.needs_native_wrapper = True
            result.blocked_reason = "Surface handle not accepted by python-vulkan for caps/formats"
            result.notes += "Surface creado pero consultas KHR fallan; wrapper nativo recomendado. "
            return result.to_dict()

        chosen_format = formats[0] if formats else None
        if chosen_format:
            result.chosen_format = f"{getattr(chosen_format, 'format', '?')}/{getattr(chosen_format, 'colorSpace', '?')}"
        chosen_present_mode = modes[0] if modes else vk.VK_PRESENT_MODE_FIFO_KHR
        result.chosen_present_mode = str(chosen_present_mode)

        extent = getattr(caps, "currentExtent", None)
        width, height = 640, 360
        if extent and getattr(extent, "width", 0) not in (0, 0xFFFFFFFF):
            width, height = int(extent.width), int(extent.height)
        result.chosen_extent = f"{width}x{height}"

        min_count = int(getattr(caps, "minImageCount", 2) or 2)
        max_count = int(getattr(caps, "maxImageCount", 0) or 0)
        image_count = min_count + 1
        if max_count and image_count > max_count:
            image_count = max_count
        result.image_count = image_count

        # Logical device con VK_KHR_swapchain
        queue_priority = [1.0]
        qci = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=q_index,
            queueCount=1,
            pQueuePriorities=queue_priority,
        )
        dev_exts = ["VK_KHR_swapchain"]
        dci = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[qci],
            enabledExtensionCount=len(dev_exts),
            ppEnabledExtensionNames=dev_exts,
        )
        device = vk.vkCreateDevice(selected_dev, dci, None)
        result.device_created = True
        result.swapchain_ext_enabled = True

        # Intentar crear swapchain con la información disponible.
        result.swapchain_create_attempted = True
        sci = vk.VkSwapchainCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=surface_raw,
            minImageCount=image_count,
            imageFormat=getattr(chosen_format, "format", vk.VK_FORMAT_B8G8R8A8_UNORM) if chosen_format else vk.VK_FORMAT_B8G8R8A8_UNORM,
            imageColorSpace=getattr(chosen_format, "colorSpace", vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR) if chosen_format else vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR,
            imageExtent=vk.VkExtent2D(width=width, height=height),
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            preTransform=getattr(caps, "currentTransform", vk.VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR),
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=chosen_present_mode,
            clipped=vk.VK_TRUE,
            oldSwapchain=None,
        )
        swapchain = vk.vkCreateSwapchainKHR(device, sci, None)
        result.swapchain_created = True
        result.swapchain_handle = str(swapchain)
        result.ok = True
        result.notes += "VkSwapchainKHR creado correctamente. "

        if window and hasattr(sdl, "SDL_PumpEvents"):
            start = time.time()
            while (time.time() - start) * 1000 < max(0, int(show_window_ms)):
                sdl.SDL_PumpEvents()
                if hasattr(sdl, "SDL_Delay"):
                    sdl.SDL_Delay(16)
                else:
                    time.sleep(0.016)

    except Exception as exc:
        result.blocked_reason = f"exception: {exc}"
        result.notes += f"swapchain create probe fallo: {exc}; "
    finally:
        try:
            if vk is not None and device is not None and swapchain is not None:
                vk.vkDestroySwapchainKHR(device, swapchain, None)
        except Exception:
            pass
        try:
            if vk is not None and device is not None:
                vk.vkDestroyDevice(device, None)
        except Exception:
            pass
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
        ("device_created", "dev"),
        ("caps_checked", "caps"),
        ("formats_checked", "fmt"),
        ("swapchain_create_attempted", "trySwap"),
        ("swapchain_created", "swapOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("physical_devices"):
        flags.append(f"gpu{stats.get('physical_devices')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_swapchain_create_probe()
    print("Vulkan swapchain create probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
