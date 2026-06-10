"""Stage32 Vulkan A: probe de upload de MeshData de chunk a buffers Vulkan.

El objetivo es comprobar que los datos neutrales del mundo ya pueden planearse
como vertex/index buffers tipo Vulkan. Si el paquete `vulkan` esta instalado,
intenta crear device y buffers pequenos; si no, deja reporte usable sin crashear.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from motor_juegos.vulkan_memory_upload import VulkanUploadPlan, accumulate_upload_stats


@dataclass
class VulkanChunkUploadProbeReport:
    ok: bool = False
    python_package_available: bool = False
    physical_devices: int = 0
    logical_device_created: bool = False
    created_buffers: int = 0
    upload_plans: int = 0
    vertex_buffers_planned: int = 0
    index_buffers_planned: int = 0
    upload_bytes_planned: int = 0
    error: str = ""
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.ok:
            return (
                f"Vulkan chunk upload OK: devices={self.physical_devices} "
                f"buffers={self.created_buffers} planned_bytes={self.upload_bytes_planned}"
            )
        return f"Vulkan chunk upload no listo: {self.error or 'sin detalle'}"


def run_vulkan_chunk_upload_probe(plans: Optional[List[VulkanUploadPlan]] = None) -> VulkanChunkUploadProbeReport:
    report = VulkanChunkUploadProbeReport()
    plans = plans or []
    mem_stats = accumulate_upload_stats(plans)
    report.upload_plans = mem_stats.plans
    report.vertex_buffers_planned = mem_stats.vertex_buffers
    report.index_buffers_planned = mem_stats.index_buffers
    report.upload_bytes_planned = mem_stats.total_bytes

    try:
        import vulkan as vk  # type: ignore
        report.python_package_available = True
    except Exception as exc:
        report.error = f"Paquete Python 'vulkan' no disponible: {exc}"
        report.notes.append("Instala vulkan y drivers Vulkan para hacer prueba real.")
        return report

    instance = None
    device = None
    buffers = []
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Stage32 Vulkan A",
            applicationVersion=1,
            pEngineName="JUEGO Custom Engine",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        devices = vk.vkEnumeratePhysicalDevices(instance)
        report.physical_devices = len(devices or [])
        if not devices:
            report.error = "No se detectaron GPUs Vulkan."
            return report
        physical = devices[0]
        families = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical)
        graphics_family = None
        for i, props in enumerate(families):
            if props.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                graphics_family = i
                break
        if graphics_family is None:
            report.error = "No se encontro queue family grafica."
            return report
        priority = [1.0]
        queue_info = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=graphics_family,
            queueCount=1,
            pQueuePriorities=priority,
        )
        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_info],
        )
        device = vk.vkCreateDevice(physical, device_info, None)
        report.logical_device_created = True

        # Stage32 A: prueba segura. Creamos buffers vacios/pequenos para validar ruta.
        # No asignamos memoria todavia aqui; eso queda para etapa B.
        requests = []
        for plan in plans:
            requests.extend(plan.vertex_requests[:2])
            requests.extend(plan.index_requests[:2])
        if not requests:
            # fallback: crear dos buffers de prueba, vertex/index.
            from motor_juegos.vulkan_memory_upload import VulkanBufferRequest
            requests = [
                VulkanBufferRequest("probe_vertex", "vertex", 256, 4),
                VulkanBufferRequest("probe_index", "index", 128, 6),
            ]
        for req in requests[:8]:
            usage = vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT if req.usage == "vertex" else vk.VK_BUFFER_USAGE_INDEX_BUFFER_BIT
            info = vk.VkBufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
                size=max(1, int(req.byte_size)),
                usage=usage,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            )
            buf = vk.vkCreateBuffer(device, info, None)
            buffers.append(buf)
        report.created_buffers = len(buffers)
        report.ok = bool(report.logical_device_created and report.created_buffers > 0)
        return report
    except Exception as exc:
        report.error = str(exc)
        return report
    finally:
        try:
            if device:
                for buf in buffers:
                    try:
                        vk.vkDestroyBuffer(device, buf, None)
                    except Exception:
                        pass
                vk.vkDestroyDevice(device, None)
        except Exception:
            pass
        try:
            if instance:
                vk.vkDestroyInstance(instance, None)
        except Exception:
            pass
