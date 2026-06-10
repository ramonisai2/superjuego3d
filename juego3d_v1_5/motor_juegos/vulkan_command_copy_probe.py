"""Stage32 Vulkan D: command pool / command buffer / copy buffer probe.

Esta prueba mantiene OpenGL como render jugable, pero valida otra pieza clave
para Vulkan real:
- crear command pool,
- crear command buffer,
- crear staging buffer y destination buffer,
- mapear/escribir bytes en staging,
- grabar vkCmdCopyBuffer,
- enviar a la cola grafica,
- esperar a que termine,
- limpiar recursos sin crashear.

Aun no renderiza drawIndexed ni presenta frames con Vulkan. Eso queda para la
siguiente etapa.
"""
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple
import ctypes

from motor_juegos.vulkan_memory_upload import VulkanUploadPlan, VulkanBufferRequest, accumulate_upload_stats


@dataclass
class VulkanCommandCopyProbeReport:
    ok: bool = False
    python_package_available: bool = False
    physical_devices: int = 0
    logical_device_created: bool = False
    queue_family_index: int = -1
    command_pool_created: bool = False
    command_buffers_allocated: int = 0
    buffers_created: int = 0
    memories_allocated: int = 0
    buffers_bound: int = 0
    mapped_allocations: int = 0
    bytes_written: int = 0
    copy_commands_recorded: int = 0
    submits: int = 0
    upload_plans: int = 0
    upload_bytes_planned: int = 0
    allocated_bytes: int = 0
    error: str = ""
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.ok:
            return (
                f"Vulkan command copy OK: devices={self.physical_devices} "
                f"cmdBuf={self.command_buffers_allocated} copies={self.copy_commands_recorded} "
                f"submit={self.submits} writeKB={self.bytes_written // 1024}"
            )
        return f"Vulkan command copy no listo: {self.error or 'sin detalle'}"


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
        VulkanBufferRequest("stageD_triangle_vertices", "vertex", 3 * 7 * 4, 3, "debug"),
        VulkanBufferRequest("stageD_quad_vertices", "vertex", 4 * 7 * 4, 4, "debug"),
        VulkanBufferRequest("stageD_quad_indices", "index", 6 * 4, 6, "debug"),
    ]


def _requests_from_plans(plans: List[VulkanUploadPlan]) -> List[VulkanBufferRequest]:
    requests: List[VulkanBufferRequest] = []
    for plan in plans:
        for req in (plan.vertex_requests or [])[:2]:
            requests.append(VulkanBufferRequest(req.label + ":copy", req.role, min(req.byte_size, 192 * 1024), req.item_count, req.material))
        for req in (plan.index_requests or [])[:2]:
            requests.append(VulkanBufferRequest(req.label + ":copy", req.role, min(req.byte_size, 96 * 1024), req.item_count, req.material))
        if len(requests) >= 4:
            break
    return requests[:4] or _fallback_requests()


def _pattern_bytes(size: int, seed: int) -> bytes:
    size = max(1, min(int(size), 256 * 1024))
    return bytes(((i * 13 + seed * 29) & 0xFF) for i in range(size))


def run_vulkan_command_copy_probe(plans: Optional[List[VulkanUploadPlan]] = None) -> VulkanCommandCopyProbeReport:
    report = VulkanCommandCopyProbeReport()
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
    command_pool = None
    created_buffers: List[Tuple[Any, Any]] = []
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Stage32 Vulkan D",
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
        report.queue_family_index = int(graphics_family)

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
        queue = vk.vkGetDeviceQueue(device, graphics_family, 0)

        pool_info = vk.VkCommandPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
            queueFamilyIndex=graphics_family,
        )
        command_pool = vk.vkCreateCommandPool(device, pool_info, None)
        report.command_pool_created = True

        alloc_cmd = vk.VkCommandBufferAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=1,
        )
        command_buffers = vk.vkAllocateCommandBuffers(device, alloc_cmd)
        command_buffer = command_buffers[0]
        report.command_buffers_allocated = 1

        host_flags = vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        device_flags = vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT

        begin_info = vk.VkCommandBufferBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
            flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
        )
        vk.vkBeginCommandBuffer(command_buffer, begin_info)

        for idx, req in enumerate(_requests_from_plans(plans)):
            size = max(1, int(req.byte_size))
            # Staging/source buffer.
            src_info = vk.VkBufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
                size=size,
                usage=vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            )
            src_buf = vk.vkCreateBuffer(device, src_info, None)
            report.buffers_created += 1
            src_req = vk.vkGetBufferMemoryRequirements(device, src_buf)
            src_type = _find_memory_type(vk, physical, src_req.memoryTypeBits, host_flags)
            if src_type is None:
                report.error = "No se encontro memoria HOST_VISIBLE/HOST_COHERENT para staging."
                return report
            src_alloc = vk.VkMemoryAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                allocationSize=src_req.size,
                memoryTypeIndex=src_type,
            )
            src_mem = vk.vkAllocateMemory(device, src_alloc, None)
            report.memories_allocated += 1
            report.allocated_bytes += int(src_req.size)
            vk.vkBindBufferMemory(device, src_buf, src_mem, 0)
            report.buffers_bound += 1
            created_buffers.append((src_buf, src_mem))

            write_size = min(size, int(src_req.size), 256 * 1024)
            data = _pattern_bytes(write_size, idx)
            ptr = vk.vkMapMemory(device, src_mem, 0, write_size, 0)
            try:
                ctypes.memmove(ptr, data, write_size)
                report.bytes_written += write_size
                report.mapped_allocations += 1
            finally:
                vk.vkUnmapMemory(device, src_mem)

            # Destination buffer. Prefer device local, fallback host visible if needed.
            usage = vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT
            if req.role == "vertex":
                usage |= vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT
            elif req.role == "index":
                usage |= vk.VK_BUFFER_USAGE_INDEX_BUFFER_BIT
            dst_info = vk.VkBufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
                size=size,
                usage=usage,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            )
            dst_buf = vk.vkCreateBuffer(device, dst_info, None)
            report.buffers_created += 1
            dst_req = vk.vkGetBufferMemoryRequirements(device, dst_buf)
            dst_type = _find_memory_type(vk, physical, dst_req.memoryTypeBits, device_flags)
            if dst_type is None:
                dst_type = _find_memory_type(vk, physical, dst_req.memoryTypeBits, host_flags)
            if dst_type is None:
                report.error = "No se encontro memoria compatible para destination buffer."
                return report
            dst_alloc = vk.VkMemoryAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                allocationSize=dst_req.size,
                memoryTypeIndex=dst_type,
            )
            dst_mem = vk.vkAllocateMemory(device, dst_alloc, None)
            report.memories_allocated += 1
            report.allocated_bytes += int(dst_req.size)
            vk.vkBindBufferMemory(device, dst_buf, dst_mem, 0)
            report.buffers_bound += 1
            created_buffers.append((dst_buf, dst_mem))

            region = vk.VkBufferCopy(srcOffset=0, dstOffset=0, size=size)
            vk.vkCmdCopyBuffer(command_buffer, src_buf, dst_buf, 1, [region])
            report.copy_commands_recorded += 1

        vk.vkEndCommandBuffer(command_buffer)
        submit_info = vk.VkSubmitInfo(
            sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,
            commandBufferCount=1,
            pCommandBuffers=[command_buffer],
        )
        vk.vkQueueSubmit(queue, 1, [submit_info], None)
        report.submits += 1
        vk.vkQueueWaitIdle(queue)

        report.ok = bool(
            report.logical_device_created
            and report.command_pool_created
            and report.command_buffers_allocated > 0
            and report.copy_commands_recorded > 0
            and report.submits > 0
            and report.buffers_created == report.buffers_bound
        )
        return report
    except Exception as exc:
        report.error = str(exc)
        return report
    finally:
        try:
            if device:
                try:
                    vk.vkDeviceWaitIdle(device)
                except Exception:
                    pass
                if command_pool:
                    try:
                        vk.vkDestroyCommandPool(device, command_pool, None)
                    except Exception:
                        pass
                for buf, memory in created_buffers:
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
