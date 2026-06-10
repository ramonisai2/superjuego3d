STAGE33 L - PUENTE SEGURO ACTIVABLE

Objetivo:
- Mantener visible si se usa OpenGL o Vulkan.
- Aplicar el puente de Stage33 K al gestor real solo con feature flag.
- No cambiar la ruta estable por defecto.
- Preparar administracion real de chunks con:
  request detail
  create LOD
  release handles
  cancel stale requests
- Mantener OpenGL como modo estable.

Feature flag:
- JUEGO_STREAM_BRIDGE_SAFE=0 o vacio: usa gestion legacy estable.
- JUEGO_STREAM_BRIDGE_SAFE=1: usa el puente seguro experimental.

Nuevos archivos:
- motor_juegos/world_chunk_stream_safe_apply.py
- lanzar_safe_stream_bridge_vulkan.py
- diagnostico_safe_stream_bridge_vulkan.py
- LANZAR_SAFE_STREAM_BRIDGE_VULKAN.bat
- DIAGNOSTICO_SAFE_STREAM_BRIDGE_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar juego real con OpenGL + puente seguro:
  LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat

- Probar plan seguro:
  LANZAR_SAFE_STREAM_BRIDGE_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_SAFE_STREAM_BRIDGE_VULKAN.bat

Lectura:
- flag-off = el puente queda apagado por defecto.
- safeApply = operaciones listas para aplicarse con feature flag.
- safeApplyOK = modo seguro listo sin cambiar la ruta estable.

Siguiente etapa recomendada:
Stage33 M - probar el feature flag dentro del juego y registrar estadisticas.
