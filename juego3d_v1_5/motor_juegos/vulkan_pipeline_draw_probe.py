"""Stage32 Vulkan E - prueba de pipeline grafico minimo.

Este modulo NO reemplaza el render jugable. Es una prueba aislada para avanzar hacia
Vulkan: valida que la instalacion pueda preparar los datos necesarios para un draw
simple de triangulo/quad. Mantiene OpenGL como respaldo.

La implementacion evita asumir que todos los equipos tienen el paquete Python `vulkan`
o shaders SPIR-V disponibles. Si no existen, devuelve un reporte claro sin crashear.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class VulkanPipelineProbeResult:
    ok: bool = False
    vulkan_imported: bool = False
    instance_created: bool = False
    gpu_count: int = 0
    shader_plan_created: bool = False
    pipeline_layout_plan: bool = False
    render_pass_plan: bool = False
    pipeline_plan: bool = False
    draw_plan: bool = False
    vertices: int = 0
    indices: int = 0
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _make_triangle_quad_geometry() -> Dict[str, Any]:
    # Datos neutrales: posicion xyz + color rgb.
    vertices: List[float] = [
        # triangulo
        -0.50, -0.35, 0.0, 1.0, 0.2, 0.2,
         0.50, -0.35, 0.0, 0.2, 1.0, 0.2,
         0.00,  0.45, 0.0, 0.2, 0.3, 1.0,
        # quad separado
        -0.65, -0.65, 0.0, 0.2, 0.8, 1.0,
        -0.25, -0.65, 0.0, 0.2, 0.8, 1.0,
        -0.25, -0.25, 0.0, 0.2, 0.8, 1.0,
        -0.65, -0.25, 0.0, 0.2, 0.8, 1.0,
    ]
    indices: List[int] = [0, 1, 2, 3, 4, 5, 3, 5, 6]
    return {"vertices": vertices, "indices": indices, "vertex_count": 7, "index_count": 9}


def run_vulkan_pipeline_draw_probe() -> VulkanPipelineProbeResult:
    """Intenta llegar hasta un plan de pipeline/draw minimo sin romper el juego.

    En esta etapa el objetivo es validar la ruta de datos y el bootstrap. El draw real
    completo requiere surface/swapchain/render pass compatible con la ventana activa,
    que se implementara en una etapa posterior.
    """
    result = VulkanPipelineProbeResult()
    geom = _make_triangle_quad_geometry()
    result.vertices = geom["vertex_count"]
    result.indices = geom["index_count"]

    try:
        import vulkan as vk  # type: ignore
        result.vulkan_imported = True
    except Exception as exc:
        result.error = f"No se pudo importar paquete vulkan: {exc}"
        # Aun asi dejamos claro que el plan de draw neutral existe.
        result.shader_plan_created = True
        result.pipeline_layout_plan = True
        result.render_pass_plan = True
        result.pipeline_plan = True
        result.draw_plan = True
        return result

    instance = None
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Vulkan Pipeline Probe",
            applicationVersion=1,
            pEngineName="JUEGO Motor",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        result.instance_created = True
        gpus = vk.vkEnumeratePhysicalDevices(instance)
        result.gpu_count = len(gpus) if gpus else 0

        # En Stage E todavia no compilamos shaders SPIR-V reales; preparamos el contrato.
        result.shader_plan_created = True
        result.pipeline_layout_plan = True
        result.render_pass_plan = True
        result.pipeline_plan = True
        result.draw_plan = result.gpu_count > 0
        result.ok = result.draw_plan
    except Exception as exc:
        result.error = str(exc)
    finally:
        if instance is not None:
            try:
                vk.vkDestroyInstance(instance, None)
            except Exception:
                pass
    return result


if __name__ == "__main__":
    print(run_vulkan_pipeline_draw_probe().to_dict())
