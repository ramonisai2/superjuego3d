STAGE32 VULKAN B - MEMORY BIND PROBE

Objetivo:
- Continuar la migracion hacia Vulkan sin romper la ruta jugable OpenGL.
- Probar un paso mas realista: crear VkBuffer, consultar requisitos de memoria,
  asignar VkDeviceMemory y hacer vkBindBufferMemory.

Uso normal:
    python main.py

Prueba Vulkan memory/bind:
PowerShell:
    $env:JUEGO_RENDER_BACKEND="vulkan_memory"; python main.py

CMD:
    set JUEGO_RENDER_BACKEND=vulkan_memory
    python main.py

Cambios:
- Nuevo modulo: motor_juegos/vulkan_chunk_memory_probe.py
- Nuevo backend: opengl+vulkan_chunk_memory_probe
- El juego sigue renderizando con OpenGL, pero al iniciar intenta:
  1) crear instancia Vulkan,
  2) detectar GPU,
  3) crear logical device,
  4) crear buffers de chunk,
  5) consultar memory requirements,
  6) buscar memory type compatible,
  7) asignar memoria,
  8) hacer bind de memoria a buffers,
  9) destruir recursos sin crashear.

Admin Hub / debug:
- VulkanPrep ahora muestra:
  mem: si el probe de memoria/bind fue exitoso
  bound: buffers ligados a memoria
  allocKB: memoria asignada en KB

Importante:
- Todavia no renderiza el mundo con Vulkan.
- OpenGL sigue siendo el modo jugable.
- El siguiente paso recomendado es Stage32 Vulkan C: staging/upload real y primer draw simple con pipeline Vulkan.
