STAGE33 A - PRIMERA PIEDRA

Objetivo:
- Empezar Stage33: conectar MeshData con Vulkan experimental.
- Crear un primer chunk neutral de prueba.
- Preparar un paquete de upload con vertices, indices, material y bounds.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_meshdata_chunk_probe.py
- diagnostico_meshdata_chunk_vulkan.py
- DIAGNOSTICO_MESHDATA_CHUNK_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico primer chunk MeshData:
  DIAGNOSTICO_MESHDATA_CHUNK_VULKAN.bat

Lectura:
- upload-next = el chunk está listo para subir a buffers Vulkan.
- native = hace falta wrapper nativo para present real, pero el paquete MeshData puede avanzar.
- v / i = cantidad de vertices e indices preparados.

Siguiente etapa recomendada:
Stage33 B - subir vertex/index buffers reales del primer chunk.
