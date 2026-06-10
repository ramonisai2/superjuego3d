STAGE33 J - CHUNKS EN MOVIMIENTO

Objetivo:
- Mantener visible si se usa OpenGL o Vulkan.
- Tomar el anillo centrado en jugador/camara de Stage33 I.
- Simular movimiento entre chunks.
- Calcular chunks que se cargan, se mantienen y se descargan.
- Preparar colas neutrales de upload/release para Vulkan.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_chunk_streaming_probe.py
- lanzar_chunk_streaming_vulkan.py
- diagnostico_chunk_streaming_vulkan.py
- LANZAR_CHUNK_STREAMING_VULKAN.bat
- DIAGNOSTICO_CHUNK_STREAMING_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar streaming experimental:
  LANZAR_CHUNK_STREAMING_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_CHUNK_STREAMING_VULKAN.bat

Lectura:
- MODO RENDER: OPENGL ESTABLE = ruta jugable normal.
- MODO RENDER: VULKAN EXPERIMENTAL = probe/ruta Vulkan.
- path = ruta de movimiento simulada.
- sets = calculo load/keep/unload listo.
- uploadQ = cola de carga preparada.
- releaseQ = cola de descarga preparada.
- refresh = draw list refrescada tras el movimiento.
- streamOK = streaming listo sin bloqueo nativo reportado.
- native = todavia hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Siguiente etapa recomendada:
Stage33 K - conectar streaming al gestor real de mundo/chunks.
