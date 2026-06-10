STAGE32 VULKAN A - CHUNK UPLOAD PROBE

Objetivo:
- Seguir la migracion hacia Vulkan sin romper el juego jugable en OpenGL.
- Probar que MeshData de chunks puede convertirse a planes de vertex/index buffers.
- Agregar una ruta experimental para crear buffers Vulkan tipo chunk.

Uso normal:
    python main.py

Uso de prueba Vulkan chunk/upload:
PowerShell:
    $env:JUEGO_RENDER_BACKEND="vulkan_chunk"; python main.py
CMD:
    set JUEGO_RENDER_BACKEND=vulkan_chunk
    python main.py

Cambios principales:
- Nuevo motor_juegos/vulkan_memory_upload.py
  Convierte MeshData a planes de upload tipo Vulkan.
- Nuevo motor_juegos/vulkan_chunk_probe.py
  Intenta crear instancia Vulkan, device y buffers de prueba.
- Nuevo backend combinado:
  OpenGL jugable + Vulkan chunk upload probe.
- Admin Hub muestra:
  chunk, chunkBuf y vkKB dentro de VulkanPrep.

Notas:
- Aun NO renderiza el mundo completo con Vulkan.
- Vulkan sigue siendo prueba experimental.
- OpenGL sigue como respaldo jugable.
- La siguiente etapa deberia asignar memoria Vulkan real a los buffers y preparar staging/upload mas formal.
