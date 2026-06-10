"""
Stage32 Vulkan K - swapchain/framebuffers/present probe.

Este modulo es experimental y NO reemplaza el render OpenGL jugable.
Objetivo:
- centralizar una ruta de prueba para surface/swapchain/framebuffers/present;
- reportar pasos que una implementacion Vulkan real debe completar;
- fallar de forma segura si Python no tiene bindings Vulkan/surface adecuados.

Nota:
Crear un VkSurfaceKHR real desde pygame/SDL en Python depende de extensiones
de plataforma y de bindings disponibles. Por eso este probe mantiene una ruta
segura: detecta soporte, genera un plan de present y evita crashear.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class VulkanPresentProbeResult:
    ok: bool = False
    vulkan_imported: bool = False
    instance_created: bool = False
    gpu_detected: bool = False
    surface_planned: bool = False
    swapchain_planned: bool = False
    framebuffers_planned: bool = False
    acquire_planned: bool = False
    present_planned: bool = False
    devices: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_vulkan_present_probe() -> Dict[str, Any]:
    result = VulkanPresentProbeResult()
    try:
        import vulkan as vk  # type: ignore
        result.vulkan_imported = True
    except Exception as exc:
        result.notes = "No se pudo importar vulkan: %s" % exc
        return result.to_dict()

    vk = __import__("vulkan")

    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Vulkan Present Probe",
            applicationVersion=1,
            pEngineName="JUEGO Engine",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )

        # Pedimos solo instancia basica. Surface real queda planificada para no
        # depender de integracion SDL/pygame especifica en esta etapa.
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app_info,
        )
        instance = vk.vkCreateInstance(create_info, None)
        result.instance_created = True

        gpus = vk.vkEnumeratePhysicalDevices(instance)
        result.devices = len(gpus)
        result.gpu_detected = len(gpus) > 0

        # Plan de la siguiente conexion real:
        # 1) crear VkSurfaceKHR desde ventana SDL/pygame
        # 2) consultar support/present modes/formats
        # 3) crear VkSwapchainKHR
        # 4) crear image views y framebuffers por imagen
        # 5) acquire next image
        # 6) submit command buffer
        # 7) queue present
        result.surface_planned = True
        result.swapchain_planned = result.gpu_detected
        result.framebuffers_planned = result.gpu_detected
        result.acquire_planned = result.gpu_detected
        result.present_planned = result.gpu_detected
        result.ok = result.vulkan_imported and result.instance_created and result.gpu_detected
        result.notes = "Present probe seguro: surface/swapchain/present quedan planificados para integracion SDL."
        vk.vkDestroyInstance(instance, None)
    except Exception as exc:
        result.notes = "Fallo Vulkan present probe: %s" % exc
    return result.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags: List[str] = []
    for key, short in [
        ("vulkan_imported", "vk"),
        ("instance_created", "inst"),
        ("gpu_detected", "gpu"),
        ("surface_planned", "surf"),
        ("swapchain_planned", "swp"),
        ("framebuffers_planned", "fb"),
        ("acquire_planned", "acq"),
        ("present_planned", "prs"),
    ]:
        if stats.get(key):
            flags.append(short)
    return " ".join(flags) if flags else "no-vk"


if __name__ == "__main__":
    stats = run_vulkan_present_probe()
    print("Vulkan Present Probe:", compact_status(stats))
    print(stats)
