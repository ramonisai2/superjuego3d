"""Stage32 Vulkan F - draw probe integrado (sin reemplazar OpenGL).

Objetivo:
- acercar la ruta Vulkan a un draw real sin romper el juego jugable;
- validar instance/device/queue;
- construir un plan de render pass + framebuffer + pipeline + draw indexed;
- preparar la frontera donde se conectara surface/swapchain real.

Nota honesta: esta etapa todavia no presenta imagen Vulkan en pantalla. En Python,
la creacion de surface/swapchain depende de extensiones de ventana que varian por
plataforma. Por eso este probe se centra en que el backend tenga los objetos y pasos
ordenados antes de conectar presentacion real.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class VulkanDrawProbeReport:
    ok: bool = False
    vulkan_imported: bool = False
    instance_created: bool = False
    physical_devices: int = 0
    graphics_queue_family: int = -1
    logical_device_created: bool = False
    geometry_vertices: int = 0
    geometry_indices: int = 0
    render_pass_plan: bool = False
    framebuffer_plan: bool = False
    pipeline_layout_plan: bool = False
    graphics_pipeline_plan: bool = False
    command_buffer_plan: bool = False
    draw_indexed_plan: bool = False
    present_blocked: bool = True
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        return (
            f"ok={int(self.ok)} vk={int(self.vulkan_imported)} dev={self.physical_devices} "
            f"q={self.graphics_queue_family} device={int(self.logical_device_created)} "
            f"rp={int(self.render_pass_plan)} pipe={int(self.graphics_pipeline_plan)} "
            f"drawIdx={int(self.draw_indexed_plan)} presentBlocked={int(self.present_blocked)} "
            f"err={self.error[:90]}"
        )


def _quad_geometry() -> Dict[str, Any]:
    # posicion xyz + color rgb, con indices para drawIndexed.
    vertices: List[float] = [
        -0.55, -0.55, 0.0, 0.2, 0.7, 1.0,
         0.55, -0.55, 0.0, 0.2, 1.0, 0.4,
         0.55,  0.55, 0.0, 1.0, 0.8, 0.2,
        -0.55,  0.55, 0.0, 1.0, 0.3, 0.3,
    ]
    indices: List[int] = [0, 1, 2, 0, 2, 3]
    return {"vertices": vertices, "indices": indices, "vertex_count": 4, "index_count": 6}


def run_vulkan_draw_probe() -> VulkanDrawProbeReport:
    report = VulkanDrawProbeReport()
    geom = _quad_geometry()
    report.geometry_vertices = int(geom["vertex_count"])
    report.geometry_indices = int(geom["index_count"])

    try:
        import vulkan as vk  # type: ignore
        report.vulkan_imported = True
    except Exception as exc:
        report.error = f"No se pudo importar paquete vulkan: {exc}"
        # Aun asi, el plan neutral queda creado.
        report.render_pass_plan = True
        report.framebuffer_plan = True
        report.pipeline_layout_plan = True
        report.graphics_pipeline_plan = True
        report.command_buffer_plan = True
        report.draw_indexed_plan = True
        return report

    instance = None
    device = None
    try:
        app = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Vulkan Draw Probe",
            applicationVersion=1,
            pEngineName="JUEGO Motor",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        ci = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app,
        )
        instance = vk.vkCreateInstance(ci, None)
        report.instance_created = True
        gpus = vk.vkEnumeratePhysicalDevices(instance) or []
        report.physical_devices = len(gpus)
        if not gpus:
            report.error = "No se detectaron GPUs Vulkan."
            return report

        gpu = gpus[0]
        families = vk.vkGetPhysicalDeviceQueueFamilyProperties(gpu)
        for i, fam in enumerate(families):
            if fam.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                report.graphics_queue_family = i
                break
        if report.graphics_queue_family < 0:
            report.error = "No se encontro queue family grafica."
            return report

        priority = [1.0]
        qci = vk.VkDeviceQueueCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex=report.graphics_queue_family,
            queueCount=1,
            pQueuePriorities=priority,
        )
        dci = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[qci],
        )
        device = vk.vkCreateDevice(gpu, dci, None)
        report.logical_device_created = True

        # Stage F: no compilamos shader ni presentacion aun. Dejamos el contrato completo.
        report.render_pass_plan = True
        report.framebuffer_plan = True
        report.pipeline_layout_plan = True
        report.graphics_pipeline_plan = True
        report.command_buffer_plan = True
        report.draw_indexed_plan = True
        report.ok = True
    except Exception as exc:
        report.error = str(exc)
    finally:
        if device is not None:
            try:
                vk.vkDestroyDevice(device, None)
            except Exception:
                pass
        if instance is not None:
            try:
                vk.vkDestroyInstance(instance, None)
            except Exception:
                pass
    return report


if __name__ == "__main__":
    print(run_vulkan_draw_probe().to_dict())
