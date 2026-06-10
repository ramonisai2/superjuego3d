STAGE33 G - ANILLO DE CHUNKS

Objetivo:
- Tomar la ruta del primer chunk visible experimental.
- Generar varios chunks MeshData alrededor del jugador.
- Preparar culling simple por radio.
- Crear lista de drawIndexed por chunk.
- Dejar listo el camino para varios chunks visibles en Vulkan experimental.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_multi_chunk_probe.py
- lanzar_multi_chunk_vulkan.py
- diagnostico_multi_chunk_vulkan.py
- LANZAR_MULTI_CHUNK_VULKAN.bat
- DIAGNOSTICO_MULTI_CHUNK_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar anillo de chunks:
  LANZAR_MULTI_CHUNK_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_MULTI_CHUNK_VULKAN.bat

Lectura:
- ring = coordenadas de chunks alrededor del jugador generadas.
- culling = culling simple preparado.
- drawlist = lista de drawIndexed por chunk preparada.
- multi-next = ruta lista para intentar varios chunks visibles.
- multiOK = varios chunks listos sin bloqueo nativo reportado.
- native = todavia hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Importante:
- Vulkan sigue siendo experimental y por etapas.
- OpenGL sigue siendo la ruta jugable estable.
- Esta etapa no afirma que Vulkan ya renderiza el juego completo.

Siguiente etapa recomendada:
Stage33 H - varios chunks visibles en Vulkan experimental.

ZIP sugerido:
JUEGO_1_6_STAGE33_G_MULTI_CHUNK_VULKAN.zip
