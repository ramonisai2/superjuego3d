STAGE32 VULKAN U - ESPEJO DEL SWAPCHAIN

Objetivo:
- Intentar crear VkSwapchainKHR real si el surface y las consultas KHR funcionan.
- Crear logical device con VK_KHR_swapchain.
- Elegir formato, extent, present mode e image count.
- Reportar si se logra swapOK o si se requiere wrapper nativo.

Nuevos archivos:
- motor_juegos/vulkan_swapchain_create_probe.py
- diagnostico_swapchain_create.py
- DIAGNOSTICO_SWAPCHAIN_CREATE.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnosticar swapchain real:
  DIAGNOSTICO_SWAPCHAIN_CREATE.bat

Lectura:
- swapOK = VkSwapchainKHR creado correctamente.
- native = bloqueo por handles crudos/bindings; conviene wrapper nativo.
- surf + caps + fmt pero sin swapOK = revisar detalles de device/swapchain.
- sin surf = la etapa S aun no esta lista en tu PC.

Notas:
- OpenGL sigue siendo el modo jugable.
- Esta etapa solo diagnostica/crea y destruye recursos Vulkan.
- No reemplaza el render del juego.
