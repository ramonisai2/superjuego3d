"""Stage32 Vulkan B: probe de buffers + memoria Vulkan para chunks.

Esta etapa intenta ir un paso mas alla de crear VkBuffer: consulta requisitos,
busca memory types, asigna VkDeviceMemory y hace vkBindBufferMemory.
El render jugable sigue siendo OpenGL.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any

from motor_juegos.vulkan_memory_upload import VulkanUploadPlan, VulkanBufferRequest, accumulate_upload_stats


@dataclass
class VulkanChunkMemoryProbeReport:
    ok: bool = False
    python_package_available: bool = False
    physical_devices: int = 0
    logical_device_created: bool = False
    buffers_created: int = 0
    memories_allocated: int = 0
    buffers_bound: int = 0
    upload_plans: int = 0
    upload_bytes_planned: int = 0
    allocated_bytes: int = 0
    host_visible_allocations: int = 0
    error: str = ""
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.ok:
            return (
                f"Vulkan chunk memory OK: devices={self.physical_devices} "
                f"buffers={self.buffers_created} bound={self.buffers_bound} "
                f"allocKB={self.allocated_bytes // 1024}"
            )
        return f"Vulkan chunk memory no listo: {self.error or 'sin detalle'}"


def _find_memory_type(vk: Any, physical: Any, type_bits: int, desired_flags: int) -> Optional[int]:
    props = vk.vkGetPhysicalDeviceMemoryProperties(physical)
    for i in range(int(props.memoryTypeCount)):
        if not (type_bits & (1 << i)):
            continue
        flags = props.memoryTypes[i].propertyFlags
        if (flags & desired_flags) == desired_flags:
            return i
    # fallback: cualquier memory type compatible
    for i in range(int(props.memoryTypeCount)):
        if type_bits & (1 << i):
            return i
    return None


def _make_fallback_requests() -> List[VulkanBufferRequest]:
    return [
        VulkanBufferRequest("probe_chunk_vertex", "vertex", 4096, 64, "terrain"),
        VulkanBufferRequest("probe_chunk_index", "index", 2048, 256, "terrain"),
    ]


def _requests_from_plans(plans: List[VulkanUploadPlan]) -> List[VulkanBufferRequest]:
    requests: List[VulkanBufferRequest] = []
    for plan in plans:
        # Limite intencional para no reservar demasiado en una prueba.
        requests.extend((plan.vertex_requests or [])[:3])
        requests.extend((plan.index_requests or [])[:3])
        if len(requests) >= 8:
            break
    return requests[:8] or _make_fallback_requests()


def run_vulkan_chunk_memory_probe(plans: Optional[List[VulkanUploadPlan]] = None) -> VulkanChunkMemoryProbeReport:
    report = VulkanChunkMemoryProbeReport()
    plans = plans or []
    mem_stats = accumulate_upload_stats(plans)
    report.upload_plans = mem_stats.plans
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
    created: List[Tuple[Any, Any]] = []
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Stage32 Vulkan B",
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

        queue_info = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=graphics_family,
            queueCount=1,
            pQueuePriorities=[1.0],
        )
        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[queue_info],
        )
        device = vk.vkCreateDevice(physical, device_info, None)
        report.logical_device_created = True

        desired = vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        for req in _requests_from_plans(plans):
            usage = vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT if req.usage == "vertex" else vk.VK_BUFFER_USAGE_INDEX_BUFFER_BIT
            # Se agrega TRANSFER_DST para que luego se pueda usar staging.
            usage = usage | vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
            info = vk.VkBufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
                size=max(1, int(req.byte_size)),
                usage=usage,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            )
            buf = vk.vkCreateBuffer(device, info, None)
            report.buffers_created += 1
            mem_req = vk.vkGetBufferMemoryRequirements(device, buf)
            mem_type = _find_memory_type(vk, physical, mem_req.memoryTypeBits, desired)
            if mem_type is None:
                vk.vkDestroyBuffer(device, buf, None)
                report.error = "No se encontro memory type compatible para buffer."
                return report
            alloc_info = vk.VkMemoryAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                allocationSize=mem_req.size,
                memoryTypeIndex=mem_type,
            )
            memory = vk.vkAllocateMemory(device, alloc_info, None)
            report.memories_allocated += 1
            report.allocated_bytes += int(mem_req.size)
            props = vk.vkGetPhysicalDeviceMemoryProperties(physical)
            flags = props.memoryTypes[mem_type].propertyFlags
            if (flags & vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT):
                report.host_visible_allocations += 1
            vk.vkBindBufferMemory(device, buf, memory, 0)
            report.buffers_bound += 1
            created.append((buf, memory))

        report.ok = bool(report.logical_device_created and report.buffers_bound == report.buffers_created and report.buffers_created > 0)
        return report
    except Exception as exc:
        report.error = str(exc)
        return report
    finally:
        try:
            if device:
                for buf, memory in created:
                    try:
                        vk.vkDestroyBuffer(device, buf, None)
                    except Exception:
                        pass
                    try:
                        vk.vkFreeMemory(device, memory, None)
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
