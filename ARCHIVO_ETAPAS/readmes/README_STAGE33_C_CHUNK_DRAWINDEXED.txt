STAGE33 C - GOLPE INDEXADO

Objetivo:
- Conectar los buffers del primer chunk a una ruta drawIndexed experimental.
- Preparar secuencia de comandos:
  vkCmdBindPipeline
  vkCmdBindVertexBuffers
  vkCmdBindIndexBuffer
  vkCmdDrawIndexed
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_chunk_drawindexed_probe.py
- diagnostico_chunk_drawindexed_vulkan.py
- DIAGNOSTICO_CHUNK_DRAWINDEXED_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico drawIndexed del primer chunk:
  DIAGNOSTICO_CHUNK_DRAWINDEXED_VULKAN.bat

Lectura:
- drawIndexed-next = comando de dibujo del primer chunk listo.
- pipe/layout/vbind/ibind = partes de la ruta preparadas.
- native = puede seguir faltando wrapper nativo para present real.

Siguiente etapa recomendada:
Stage33 D - pipeline/material de terreno simple para el primer chunk.
