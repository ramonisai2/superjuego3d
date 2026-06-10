STAGE32 VULKAN Z - PORTAL EXPERIMENTAL

Objetivo:
- Cerrar la serie Stage32 con un modo Vulkan experimental separado.
- Mantener OpenGL como juego estable.
- Preparar la transición a Stage33:
  primer chunk MeshData dibujado por Vulkan.

Nuevos archivos:
- motor_juegos/vulkan_experimental_mode.py
- lanzar_vulkan_experimental.py
- diagnostico_vulkan_experimental.py
- LANZAR_VULKAN_EXPERIMENTAL_STAGE32Z.bat
- DIAGNOSTICO_VULKAN_EXPERIMENTAL.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar modo Vulkan experimental:
  LANZAR_VULKAN_EXPERIMENTAL_STAGE32Z.bat

- Diagnóstico:
  DIAGNOSTICO_VULKAN_EXPERIMENTAL.bat

Lectura:
- vulkan-mode = modo experimental preparado.
- mesh-bridge = listo para conectar MeshData.
- chunk-next = siguiente etapa: primer chunk Vulkan.
- native = hace falta wrapper nativo para present real confiable.

Siguiente etapa recomendada:
Stage33 A - PRIMER CHUNK VULKAN
- tomar ChunkMeshData real del mundo;
- subir vertices/indices;
- dibujar un chunk simple en modo Vulkan experimental;
- mantener OpenGL como fallback.
