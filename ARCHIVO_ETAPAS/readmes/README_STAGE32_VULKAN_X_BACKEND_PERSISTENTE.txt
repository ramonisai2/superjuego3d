STAGE32 VULKAN X - NUCLEO DEL DESTELLO

Objetivo:
- Crear una clase de backend Vulkan persistente.
- Unificar los resultados de U, V y W:
  swapchain -> frames -> present plan.
- Preparar la siguiente etapa: clear visible real en un loop dedicado.

Nuevos archivos:
- motor_juegos/vulkan_persistent_clear_backend.py
- diagnostico_backend_vulkan_persistente.py
- DIAGNOSTICO_BACKEND_VULKAN_PERSISTENTE.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico backend Vulkan persistente:
  DIAGNOSTICO_BACKEND_VULKAN_PERSISTENTE.bat

Lectura:
- clear-next = ya se puede intentar clear visible real en Stage32 Y.
- native = hace falta wrapper nativo para handles persistentes.
- U-swap / V-frames / W-present = qué partes ya están listas.

Notas:
- OpenGL sigue siendo el modo jugable.
- Vulkan sigue experimental.
- Esta etapa organiza el backend para dejar de depender de probes sueltos.
