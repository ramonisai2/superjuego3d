"""Stage31 Pre-Y: prueba Vulkan de triangulo/quad sin reemplazar OpenGL.

Esta prueba NO presenta imagen en pantalla todavia. El objetivo es avanzar un paso
real hacia Vulkan comprobando que podemos:
- crear instancia Vulkan,
- elegir GPU,
- encontrar familia de cola grafica,
- crear logical device,
- crear buffers Vulkan para vertices/indices de triangulo y quad,
- destruir todo sin crashear.

El juego sigue usando OpenGL como backend jugable por defecto.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import struct


@dataclass
class VulkanTriangleProbeReport:
    requested: bool = True
    python_package_available: bool = False
    instance_created: bool = False
    physical_devices: int = 0
    selected_device_name: str = ""
    graphics_queue_family: int = -1
    logical_device_created: bool = False
    triangle_vertices: int = 0
    triangle_indices: int = 0
    quad_vertices: int = 0
    quad_indices: int = 0
    vertex_buffer_created: bool = False
    index_buffer_created: bool = False
    created_buffers: int = 0
    error: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            self.python_package_available
            and self.instance_created
            and self.logical_device_created
            and self.vertex_buffer_created
            and self.index_buffer_created
        )

    def summary(self) -> str:
        if self.error:
            return f"Vulkan triangle probe fallo: {self.error}"
        return (
            f"Vulkan triangle probe ok={self.ok} gpu='{self.selected_device_name}' "
            f"qfam={self.graphics_queue_family} buffers={self.created_buffers}"
        )


def build_triangle_vertices() -> List[Tuple[float, float, float, float, float, float, float, float]]:
    """Vertices: pos.xyz + color.rgba + uv.u (padding simple para futuro)."""
    return [
        (0.0, -0.55, 0.0, 1.0, 0.15, 0.10, 1.0, 0.0),
        (0.55, 0.45, 0.0, 0.10, 0.85, 0.20, 1.0, 0.5),
        (-0.55, 0.45, 0.0, 0.15, 0.35, 1.0, 1.0, 1.0),
    ]


def build_quad_vertices() -> List[Tuple[float, float, float, float, float, float, float, float]]:
    return [
        (-0.55, -0.55, 0.0, 0.10, 0.25, 0.95, 1.0, 0.0),
        (0.55, -0.55, 0.0, 0.10, 0.65, 0.95, 1.0, 0.0),
        (0.55, 0.55, 0.0, 0.80, 0.95, 0.30, 1.0, 1.0),
        (-0.55, 0.55, 0.0, 0.95, 0.35, 0.20, 1.0, 1.0),
    ]


def pack_vertices(vertices) -> bytes:
    data = bytearray()
    for v in vertices:
        data.extend(struct.pack("8f", *v))
    return bytes(data)


def pack_indices(indices) -> bytes:
    data = bytearray()
    for i in indices:
        data.extend(struct.pack("I", int(i)))
    return bytes(data)


def _decode_device_name(name) -> str:
    if isinstance(name, bytes):
        return name.decode("utf-8", "ignore").rstrip("\x00")
    return str(name)


def run_vulkan_triangle_probe() -> VulkanTriangleProbeReport:
    report = VulkanTriangleProbeReport()
    triangle_vertices = build_triangle_vertices()
    quad_vertices = build_quad_vertices()
    triangle_indices = [0, 1, 2]
    quad_indices = [0, 1, 2, 2, 3, 0]
    report.triangle_vertices = len(triangle_vertices)
    report.triangle_indices = len(triangle_indices)
    report.quad_vertices = len(quad_vertices)
    report.quad_indices = len(quad_indices)

    try:
        import vulkan as vk  # type: ignore
        report.python_package_available = True
    except Exception:
        report.error = "No se encontro el paquete Python 'vulkan'. Instalar despues con: pip install vulkan"
        return report

    instance = None
    device = None
    vertex_buffer = None
    index_buffer = None
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Vulkan Triangle Probe",
            applicationVersion=vk.VK_MAKE_VERSION(0, 1, 0),
            pEngineName="JUEGO 1.6 Experimental",
            engineVersion=vk.VK_MAKE_VERSION(0, 1, 0),
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        report.instance_created = True

        devices = vk.vkEnumeratePhysicalDevices(instance)
        report.physical_devices = len(devices)
        if not devices:
            report.error = "No se detectaron GPUs Vulkan."
            return report

        physical = devices[0]
        props = vk.vkGetPhysicalDeviceProperties(physical)
        report.selected_device_name = _decode_device_name(getattr(props, "deviceName", "GPU Vulkan"))

        queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical)
        graphics_family = -1
        for i, q in enumerate(queue_families):
            if getattr(q, "queueFlags", 0) & vk.VK_QUEUE_GRAPHICS_BIT:
                graphics_family = i
                break
        if graphics_family < 0:
            report.error = "No se encontro familia de cola grafica Vulkan."
            return report
        report.graphics_queue_family = graphics_family

        priority = [1.0]
        queue_create = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=graphics_family,
            queueCount=1,
            pQueuePriorities=priority,
        )
        device_create = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_create],
        )
        device = vk.vkCreateDevice(physical, device_create, None)
        report.logical_device_created = True

        vertex_bytes = pack_vertices(triangle_vertices + quad_vertices)
        index_bytes = pack_indices(triangle_indices + quad_indices)

        vbuf_info = vk.VkBufferCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            size=len(vertex_bytes),
            usage=vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
        )
        vertex_buffer = vk.vkCreateBuffer(device, vbuf_info, None)
        report.vertex_buffer_created = vertex_buffer is not None
        if report.vertex_buffer_created:
            report.created_buffers += 1

        ibuf_info = vk.VkBufferCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            size=len(index_bytes),
            usage=vk.VK_BUFFER_USAGE_INDEX_BUFFER_BIT,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
        )
        index_buffer = vk.vkCreateBuffer(device, ibuf_info, None)
        report.index_buffer_created = index_buffer is not None
        if report.index_buffer_created:
            report.created_buffers += 1

        report.notes.append("Buffers creados sin asignar memoria; la siguiente etapa hara memory allocation/map/upload.")
    except Exception as exc:
        report.error = str(exc)
    finally:
        try:
            if device is not None and vertex_buffer is not None:
                vk.vkDestroyBuffer(device, vertex_buffer, None)
        except Exception:
            pass
        try:
            if device is not None and index_buffer is not None:
                vk.vkDestroyBuffer(device, index_buffer, None)
        except Exception:
            pass
        try:
            if device is not None:
                vk.vkDestroyDevice(device, None)
        except Exception:
            pass
        try:
            if instance is not None:
                vk.vkDestroyInstance(instance, None)
        except Exception:
            pass
    return report
