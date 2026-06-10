STAGE32 VULKAN V - CRISTAL DEL PRESENT

Objetivo:
- Continuar despues de VkSwapchainKHR.
- Preparar image views, render pass y framebuffers por imagen.
- Preparar la siguiente etapa: acquire/clear/present.

Nuevos archivos:
- motor_juegos/vulkan_swapchain_frame_probe.py
- diagnostico_swapchain_frame.py
- DIAGNOSTICO_SWAPCHAIN_FRAME.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico de frames de swapchain:
  DIAGNOSTICO_SWAPCHAIN_FRAME.bat

Lectura:
- present-next = podemos intentar acquire/clear/present en la siguiente etapa.
- native = aun falta wrapper nativo o resolver handles.
- swap sin present-next = el swapchain existe, pero falta image views/framebuffers.

Notas:
- OpenGL sigue siendo el modo jugable.
- Vulkan sigue en modo diagnóstico.
- Esta etapa depende de que Stage32 U marque swapOK en la PC del usuario.
