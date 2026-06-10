STAGE33 E - ALTAR DEL CHUNK

Objetivo:
- Preparar render pass del primer chunk.
- Unir pipeline de terreno + framebuffers + viewport/scissor + drawIndexed.
- Crear el frame packet:
  begin render pass -> bind pipeline -> bind buffers -> drawIndexed -> end render pass.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_first_chunk_renderpass_probe.py
- diagnostico_first_chunk_renderpass_vulkan.py
- DIAGNOSTICO_FIRST_CHUNK_RENDERPASS_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico render pass primer chunk:
  DIAGNOSTICO_FIRST_CHUNK_RENDERPASS_VULKAN.bat

Lectura:
- visible-next = el paquete de frame está listo para intentar primer chunk visible.
- rp/fb/viewport/clear/draw = partes del render pass preparadas.
- native = puede seguir faltando wrapper nativo para present real.

Siguiente etapa recomendada:
Stage33 F - primer chunk visible experimental.
