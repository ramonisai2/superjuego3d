STAGE33 D - PIEL DE TERRENO

Objetivo:
- Preparar pipeline/material simple para el primer chunk Vulkan.
- Definir material terrain_grass_simple.
- Definir vertex layout pos3_normal3_uv2.
- Preparar shader plan, depth, raster y blend.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_terrain_pipeline_probe.py
- diagnostico_terrain_pipeline_vulkan.py
- DIAGNOSTICO_TERRAIN_PIPELINE_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico pipeline terreno:
  DIAGNOSTICO_TERRAIN_PIPELINE_VULKAN.bat

Lectura:
- pipeline-next = pipeline/material de terreno simple listo.
- mat/layout/shader/depth/raster/blend = partes del pipeline preparadas.
- native = puede seguir faltando wrapper nativo para present real.

Siguiente etapa recomendada:
Stage33 E - render pass del primer chunk con pipeline de terreno.
