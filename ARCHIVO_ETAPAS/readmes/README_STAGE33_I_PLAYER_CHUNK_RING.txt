STAGE33 I - ANILLO CENTRADO EN JUGADOR

Objetivo:
- Mostrar claramente si el juego/probe usa OpenGL o Vulkan.
- Tomar la ruta de varios chunks visibles de Stage33 H.
- Convertir posicion de jugador/camara a coordenada de chunk.
- Generar el anillo de chunks alrededor del jugador/camara.
- Preparar culling y drawIndexed por chunk centrado.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_player_chunk_ring_probe.py
- lanzar_player_chunk_ring_vulkan.py
- diagnostico_player_chunk_ring_vulkan.py
- LANZAR_PLAYER_CHUNK_RING_VULKAN.bat
- DIAGNOSTICO_PLAYER_CHUNK_RING_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar anillo centrado en jugador/camara:
  LANZAR_PLAYER_CHUNK_RING_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_PLAYER_CHUNK_RING_VULKAN.bat

Lectura:
- MODO RENDER: OPENGL ESTABLE = ruta jugable normal.
- MODO RENDER: VULKAN EXPERIMENTAL = probe/ruta Vulkan.
- center = chunk central calculado desde jugador/camara.
- ring = anillo centrado generado.
- culling = filtro simple alrededor del centro.
- drawlist = drawIndexed por chunk visible preparado.
- playerRingOK = anillo centrado listo sin bloqueo nativo reportado.
- native = todavia hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Siguiente etapa recomendada:
Stage33 J - carga/descarga dinamica de chunks por movimiento.
