"""Stage32 Vulkan H - Shader modules + pipeline layout probe.

Esta prueba NO reemplaza el render jugable. Valida que, si ya existen shaders
SPIR-V compilados, Python/Vulkan puede crear VkShaderModule y VkPipelineLayout.
OpenGL sigue siendo el camino jugable.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import struct

from motor_juegos.vulkan_shader_probe import run_vulkan_shader_probe


@dataclass
class VulkanShaderModuleProbeReport:
    ok: bool = False
    vulkan_imported: bool = False
    physical_devices: int = 0
    spirv_generated: bool = False
    compiler_found: bool = False
    vertex_spirv_bytes: int = 0
    fragment_spirv_bytes: int = 0
    shader_modules_created: int = 0
    pipeline_layout_created: bool = False
    descriptor_set_layouts: int = 0
    push_constant_ranges: int = 0
    errors: str = ""

    def to_dict(self):
        return asdict(self)

    def summary(self) -> str:
        return (
            f"ok={int(self.ok)} vk={int(self.vulkan_imported)} dev={self.physical_devices} "
            f"spv={int(self.spirv_generated)} mods={self.shader_modules_created} "
            f"layout={int(self.pipeline_layout_created)} vs={self.vertex_spirv_bytes} fs={self.fragment_spirv_bytes}"
        )


def _spv_u32_words(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 4 != 0:
        raise RuntimeError(f"SPIR-V invalido, tamano no multiplo de 4: {path}")
    if len(data) < 20:
        raise RuntimeError(f"SPIR-V demasiado pequeno: {path}")
    words = list(struct.unpack("<" + "I" * (len(data) // 4), data))
    # Magic SPIR-V little endian = 0x07230203
    if words[0] != 0x07230203:
        raise RuntimeError(f"SPIR-V magic invalido en {path}: {hex(words[0])}")
    return words


def _asset_spv_paths() -> tuple[Path, Path]:
    asset_dir = Path(__file__).resolve().parent.parent / "assets" / "shaders" / "vulkan_probe"
    return asset_dir / "probe.vert.spv", asset_dir / "probe.frag.spv"


def run_vulkan_shader_module_probe() -> VulkanShaderModuleProbeReport:
    report = VulkanShaderModuleProbeReport()

    # Primero reutilizamos la etapa G para escribir/compilar shaders si hay compilador.
    shader_report = run_vulkan_shader_probe(write_assets=True)
    report.vulkan_imported = bool(shader_report.vulkan_imported)
    report.physical_devices = int(shader_report.physical_devices or 0)
    report.spirv_generated = bool(shader_report.spirv_generated)
    report.compiler_found = bool(shader_report.compiler_found)
    report.vertex_spirv_bytes = int(shader_report.vertex_spirv_bytes or 0)
    report.fragment_spirv_bytes = int(shader_report.fragment_spirv_bytes or 0)
    if shader_report.errors:
        report.errors += f"shaderG:{shader_report.errors}; "

    try:
        import vulkan as vk  # type: ignore
        report.vulkan_imported = True

        app = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Stage32 Vulkan H ShaderModule Probe",
            applicationVersion=1,
            pEngineName="JUEGO Vulkan Prep",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        instance_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app,
        )
        instance = vk.vkCreateInstance(instance_info, None)
        device = None
        vert_module = None
        frag_module = None
        pipeline_layout = None
        try:
            physical_devices = vk.vkEnumeratePhysicalDevices(instance)
            report.physical_devices = len(physical_devices or [])
            if not physical_devices:
                raise RuntimeError("No hay GPU Vulkan disponible")
            physical_device = physical_devices[0]

            queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical_device)
            graphics_index: Optional[int] = None
            for i, q in enumerate(queue_families or []):
                if q.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                    graphics_index = i
                    break
            if graphics_index is None:
                raise RuntimeError("No se encontro queue family grafica")

            queue_priority = [1.0]
            qinfo = vk.VkDeviceQueueCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                queueFamilyIndex=graphics_index,
                queueCount=1,
                pQueuePriorities=queue_priority,
            )
            dinfo = vk.VkDeviceCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
                queueCreateInfoCount=1,
                pQueueCreateInfos=[qinfo],
            )
            device = vk.vkCreateDevice(physical_device, dinfo, None)

            vert_path, frag_path = _asset_spv_paths()
            if not vert_path.exists() or not frag_path.exists():
                raise RuntimeError("No hay SPIR-V. Instala glslangValidator o glslc para generar probe.vert.spv/probe.frag.spv")

            vert_words = _spv_u32_words(vert_path)
            frag_words = _spv_u32_words(frag_path)
            report.vertex_spirv_bytes = vert_path.stat().st_size
            report.fragment_spirv_bytes = frag_path.stat().st_size
            report.spirv_generated = True

            vert_info = vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=report.vertex_spirv_bytes,
                pCode=vert_words,
            )
            frag_info = vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=report.fragment_spirv_bytes,
                pCode=frag_words,
            )
            vert_module = vk.vkCreateShaderModule(device, vert_info, None)
            report.shader_modules_created += 1
            frag_module = vk.vkCreateShaderModule(device, frag_info, None)
            report.shader_modules_created += 1

            layout_info = vk.VkPipelineLayoutCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
                setLayoutCount=0,
                pSetLayouts=None,
                pushConstantRangeCount=0,
                pPushConstantRanges=None,
            )
            pipeline_layout = vk.vkCreatePipelineLayout(device, layout_info, None)
            report.pipeline_layout_created = pipeline_layout is not None
            report.descriptor_set_layouts = 0
            report.push_constant_ranges = 0

        finally:
            try:
                if pipeline_layout is not None and device is not None:
                    vk.vkDestroyPipelineLayout(device, pipeline_layout, None)
            except Exception:
                pass
            try:
                if vert_module is not None and device is not None:
                    vk.vkDestroyShaderModule(device, vert_module, None)
            except Exception:
                pass
            try:
                if frag_module is not None and device is not None:
                    vk.vkDestroyShaderModule(device, frag_module, None)
            except Exception:
                pass
            try:
                if device is not None:
                    vk.vkDestroyDevice(device, None)
            except Exception:
                pass
            try:
                vk.vkDestroyInstance(instance, None)
            except Exception:
                pass
    except Exception as exc:
        report.errors += f"shaderModule:{exc}; "

    report.ok = bool(
        report.vulkan_imported
        and report.physical_devices > 0
        and report.spirv_generated
        and report.shader_modules_created >= 2
        and report.pipeline_layout_created
    )
    return report


if __name__ == "__main__":
    print(run_vulkan_shader_module_probe().to_dict())
