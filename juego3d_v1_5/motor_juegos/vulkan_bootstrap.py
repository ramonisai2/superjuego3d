"""Bootstrap/probe inicial para la futura migracion a Vulkan.

Stage31 Pre-W:
- No dibuja el mundo con Vulkan todavia.
- Detecta si existe el paquete Python `vulkan`.
- Intenta crear una instancia Vulkan minima solo cuando se solicita explicitamente.
- Mantiene OpenGL como backend jugable por defecto.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VulkanProbeReport:
    requested: bool = False
    python_package_available: bool = False
    instance_created: bool = False
    physical_devices: int = 0
    device_names: List[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.device_names is None:
            self.device_names = []

    @property
    def ok(self) -> bool:
        return self.python_package_available and self.instance_created

    def summary(self) -> str:
        if not self.requested:
            return "Vulkan no solicitado; usando OpenGL."
        if self.error:
            return f"Vulkan probe fallo: {self.error}"
        return f"Vulkan probe OK: devices={self.physical_devices} names={self.device_names}"


def probe_vulkan(create_instance: bool = True) -> VulkanProbeReport:
    report = VulkanProbeReport(requested=True)
    try:
        import vulkan as vk  # type: ignore
        report.python_package_available = True
    except Exception as exc:
        report.error = "No se encontro el paquete Python 'vulkan'. Instalar despues con: pip install vulkan"
        return report

    if not create_instance:
        return report

    instance = None
    try:
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO 1.6 Vulkan Probe",
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
        for dev in devices:
            try:
                props = vk.vkGetPhysicalDeviceProperties(dev)
                name = getattr(props, "deviceName", "GPU Vulkan")
                if isinstance(name, bytes):
                    name = name.decode("utf-8", "ignore").rstrip("\x00")
                report.device_names.append(str(name))
            except Exception:
                report.device_names.append("GPU Vulkan")
    except Exception as exc:
        report.error = str(exc)
    finally:
        if instance is not None:
            try:
                vk.vkDestroyInstance(instance, None)
            except Exception:
                pass
    return report
