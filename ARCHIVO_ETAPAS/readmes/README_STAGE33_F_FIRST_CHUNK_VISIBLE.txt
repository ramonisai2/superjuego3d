STAGE33 F - PRIMER BLOQUE VISIBLE

Objetivo:
- Preparar la ruta completa del primer chunk visible experimental.
- Unir:
  modo Vulkan experimental
  render pass del primer chunk
  clear
  drawIndexed
  present
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_first_chunk_visible_probe.py
- lanzar_first_chunk_visible_vulkan.py
- diagnostico_first_chunk_visible_vulkan.py
- LANZAR_FIRST_CHUNK_VISIBLE_VULKAN.bat
- DIAGNOSTICO_FIRST_CHUNK_VISIBLE_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar primer chunk visible:
  LANZAR_FIRST_CHUNK_VISIBLE_VULKAN.bat

- Diagnóstico:
  DIAGNOSTICO_FIRST_CHUNK_VISIBLE_VULKAN.bat

Lectura:
- visibleOK = primer chunk visible listo en ruta experimental.
- multi-next = ruta lista para preparar varios chunks.
- native = hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Siguiente etapa recomendada:
Stage33 G - varios chunks MeshData en Vulkan experimental.
