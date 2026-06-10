STAGE33 B - SANGRE DE BUFFER

Objetivo:
- Convertir el primer chunk MeshData a bytes de vertices e indices.
- Preparar vertex buffer e index buffer.
- Preparar staging upload.
- Dejar listo Stage33 C: drawIndexed del primer chunk.

Nuevos archivos:
- motor_juegos/vulkan_chunk_buffer_upload_probe.py
- diagnostico_chunk_buffer_vulkan.py
- DIAGNOSTICO_CHUNK_BUFFER_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico buffers del primer chunk:
  DIAGNOSTICO_CHUNK_BUFFER_VULKAN.bat

Lectura:
- draw-next = buffers listos para conectar a drawIndexed.
- vbuf / ibuf = vertex/index buffer planeados.
- vb / ib = bytes de vertices e indices.
- native = puede seguir faltando wrapper nativo para present real.

Siguiente etapa recomendada:
Stage33 C - drawIndexed del primer chunk simple.
