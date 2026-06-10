STAGE33 M - PUENTE CON ESTADISTICAS

Objetivo:
- Mantener visible si se usa OpenGL o Vulkan.
- Medir el puente seguro dentro del gestor real de chunks.
- Mostrar contadores en el HUD de debug cuando JUEGO_STREAM_BRIDGE_SAFE=1.
- Evitar pedir logs de error antes de tener telemetria clara.
- Mantener OpenGL estable por defecto.

Nuevos archivos:
- motor_juegos/stream_bridge_stats_probe.py
- lanzar_stream_bridge_stats_vulkan.py
- diagnostico_stream_bridge_stats_vulkan.py
- LANZAR_STREAM_BRIDGE_STATS_VULKAN.bat
- DIAGNOSTICO_STREAM_BRIDGE_STATS_VULKAN.bat

Cambios en juego real:
- LANZAR_OPENGL.bat sigue usando gestion legacy estable.
- LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat activa JUEGO_STREAM_BRIDGE_SAFE=1.
- Con el admin/debug visible se muestra:
  StreamBridge: ON calls, center, requests, lod, frees, cancels, queue, pending, loaded.

Uso:
- Probar juego normal:
  LANZAR_OPENGL.bat

- Probar juego con puente seguro:
  LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat

- Probar telemetria sin abrir el juego:
  LANZAR_STREAM_BRIDGE_STATS_VULKAN.bat

Lectura:
- statsOK = telemetria coherente en simulacion.
- calls = veces que corrio el gestor simulado.
- req = solicitudes de detalle.
- lod = LODs creados.
- free = liberaciones de handles.

Siguiente etapa recomendada:
Stage33 N - prueba jugable comparativa OpenGL normal vs OpenGL + puente seguro.
