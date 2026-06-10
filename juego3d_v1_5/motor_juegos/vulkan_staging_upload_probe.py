"""Stage32 Vulkan C: probe de staging/upload host visible.

Este modulo mantiene OpenGL como render jugable, pero prueba una parte clave
para Vulkan real:
- crear buffers con uso TRANSFER_SRC / TRANSFER_DST,
- asignar memoria HOST_VISIBLE / HOST_COHERENT,
- enlazar buffer+memoria,
- mapear memoria,
- copiar bytes de prueba hacia el buffer,
- limpiar recursos sin crashear.

Aun no presenta imagen ni ejecuta vkCmdCopyBuffer/drawIndexed. Esa sera la
siguiente etapa. Esta prueba valida que Python+drivers pueden mapear/subir datos.
"""
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple
import ctypes

from motor_juegos.vulkan_memory_upload import VulkanUploadPlan, VulkanBufferRequest, accumulate_upload_stats


@dataclass
class VulkanStagingUploadProbeReport:
    ok: bool = False
    python_package_available: bool = False
    physical_devices: int = 0
    logical_device_created: bool = False
    buffers_created: int = 0
    memories_allocated: int = 0
    buffers_bound: int = 0
    mapped_allocations: int = 0
    bytes_written: int = 0
    upload_plans: int = 0
    upload_bytes_planned: int = 0
    allocated_bytes: int = 0
    error: str = ""
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.ok:
            return (
                f"Vulkan staging upload OK: devices={self.physical_devices} "
                f"buffers={self.buffers_created} mapped={self.mapped_allocations} "
                f"writeKB={self.bytes_written // 1024} allocKB={self.allocated_bytes // 1024}"
            )
        return f"Vulkan staging upload no listo: {self.error or 'sin detalle'}"


def _find_memory_type(vk: Any, physical: Any, type_bits: int, desired_flags: int) -> Optional[int]:
    props = vk.vkGetPhysicalDeviceMemoryProperties(physical)
    for i in range(int(props.memoryTypeCount)):
        if not (type_bits & (1 << i)):
            continue
        flags = props.memoryTypes[i].propertyFlags
        if (flags & desired_flags) == desired_flags:
            return i
    return None


def _fallback_requests() -> List[VulkanBufferRequest]:
    return [
        VulkanBufferRequest("stageC_triangle_vertex_staging", "staging", 3 * 7 * 4, 3, "debug"),
        VulkanBufferRequest("stageC_quad_vertex_staging", "staging", 4 * 7 * 4, 4, "debug"),
        VulkanBufferRequest("stageC_quad_index_staging", "staging", 6 * 4, 6, "debug"),
    ]


def _requests_from_plans(plans: List[VulkanUploadPlan]) -> List[VulkanBufferRequest]:
    requests: List[VulkanBufferRequest] = []
    for plan in plans:
        # Para probe: toma poco para no hacer asignaciones enormes.
        for req in (plan.vertex_requests or [])[:2]:
            requests.append(VulkanBufferRequest(req.label + ":staging", "staging", min(req.byte_size, 256 * 1024), req.item_count, req.material))
        for req in (plan.index_requests or [])[:2]:
            requests.append(VulkanBufferRequest(req.label + ":staging", "staging", min(req.byte_size, 128 * 1024), req.item_count, req.material))
        if len(requests) >= 6:
            break
    return requests[:6] or _fallback_requests()


def _pattern_bytes(size: int, seed: int) -> bytes:
    # Patron determinista pequeño. Suficiente para validar map/write.
    size = max(1, min(int(size), 256 * 1024))
    return bytes(((i * 31 + seed * 17) & 0xFF) for i in range(size))


def run_vulkan_staging_upload_probe(plans: Optional[List[VulkanUploadPlan]] = None) -> VulkanStagingUploadProbeReport:
    report = VulkanStagingUploadProbeReport()
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
            pApplicationName="JUEGO 1.6 Stage32 Vulkan C",
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
        for idx, req in enumerate(_requests_from_plans(plans)):
            usage = vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT
            # En Vulkan real se usara staging -> device local vertex/index.
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
                report.error = "No se encontro memory type HOST_VISIBLE/HOST_COHERENT para staging."
                return report
            alloc_info = vk.VkMemoryAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                allocationSize=mem_req.size,
                memoryTypeIndex=mem_type,
            )
            memory = vk.vkAllocateMemory(device, alloc_info, None)
            report.memories_allocated += 1
            report.allocated_bytes += int(mem_req.size)
            vk.vkBindBufferMemory(device, buf, memory, 0)
            report.buffers_bound += 1
            created.append((buf, memory))

            write_size = min(int(req.byte_size), int(mem_req.size), 256 * 1024)
            data = _pattern_bytes(write_size, idx)
            ptr = vk.vkMapMemory(device, memory, 0, write_size, 0)
            try:
                # pyvulkan suele devolver una direccion compatible con ctypes.
                ctypes.memmove(ptr, data, write_size)
                report.bytes_written += write_size
                report.mapped_allocations += 1
            finally:
                vk.vkUnmapMemory(device, memory)

        report.ok = bool(
            report.logical_device_created
            and report.buffers_created > 0
            and report.buffers_created == report.buffers_bound
            and report.mapped_allocations == report.buffers_created
            and report.bytes_written > 0
        )
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
