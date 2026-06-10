STAGE32 VULKAN T - CADENA DEL SWAPCHAIN

Objetivo:
- Si Stage32 S logra VkSurfaceKHR, preparar el siguiente paso:
  consultar capacidades de surface, formatos, present modes y plan de swapchain.
- Si no hay surface, reportar claramente si se necesita wrapper nativo.

Nuevos archivos:
- motor_juegos/vulkan_swapchain_real_probe.py
- diagnostico_swapchain_real.py
- DIAGNOSTICO_SWAPCHAIN_REAL.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnosticar swapchain real:
  DIAGNOSTICO_SWAPCHAIN_REAL.bat

Lectura:
- swap-next = surface y plan de swapchain listos.
- native = probablemente hace falta wrapper nativo para manejar VkInstance/VkSurfaceKHR.
- surf sin caps/fmt/pm = surface existe, pero el binding no acepta consultar capacidades con handle crudo.

Siguiente etapa:
- Si swap-next: Stage32 U intenta crear VkSwapchainKHR.
- Si native: crear wrapper nativo pequeño para surface/swapchain.
