STAGE33 K - PUENTE AL MUNDO REAL

Objetivo:
- Mantener visible si se usa OpenGL o Vulkan.
- Tomar el streaming de chunks de Stage33 J.
- Traducir load/keep/unload a operaciones compatibles con el gestor real:
  mundo_chunks
  mundo_chunks_simple
  cola_de_peticiones
  chunks_pendientes
- Preparar request detail, create LOD, release handles, cancel requests y refresh draw list.
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/world_chunk_stream_bridge.py
- lanzar_world_chunk_bridge_vulkan.py
- diagnostico_world_chunk_bridge_vulkan.py
- LANZAR_WORLD_CHUNK_BRIDGE_VULKAN.bat
- DIAGNOSTICO_WORLD_CHUNK_BRIDGE_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar puente al gestor real:
  LANZAR_WORLD_CHUNK_BRIDGE_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_WORLD_CHUNK_BRIDGE_VULKAN.bat

Lectura:
- MODO RENDER: OPENGL ESTABLE = ruta jugable normal.
- MODO RENDER: VULKAN EXPERIMENTAL = probe/ruta Vulkan.
- world = snapshot de estructuras reales simulado.
- targets = anillos detail/LOD calculados.
- queue = solicitudes de detalle preparadas.
- release = liberaciones/cancelaciones preparadas.
- bridgeOK = puente listo sin bloqueo nativo reportado.
- native = todavia hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Siguiente etapa recomendada:
Stage33 L - aplicar el puente al gestor real en modo seguro/feature flag.
