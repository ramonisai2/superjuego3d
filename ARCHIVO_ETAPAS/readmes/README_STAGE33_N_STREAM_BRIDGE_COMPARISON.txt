STAGE33 N - COMPARATIVA SEGURA

Objetivo:
- Comparar OpenGL legacy contra OpenGL + puente seguro antes de pedir logs.
- Medir requests, LODs, liberaciones y diferencias finales de chunks.
- Decidir si vale la pena probar LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat en juego real.
- Mantener OpenGL legacy como ruta estable.

Nuevos archivos:
- motor_juegos/stream_bridge_comparison_probe.py
- lanzar_stream_bridge_comparison_vulkan.py
- diagnostico_stream_bridge_comparison_vulkan.py
- LANZAR_STREAM_BRIDGE_COMPARISON_VULKAN.bat
- DIAGNOSTICO_STREAM_BRIDGE_COMPARISON_VULKAN.bat

Uso:
- Comparativa sin abrir juego:
  LANZAR_STREAM_BRIDGE_COMPARISON_VULKAN.bat

- Jugar normal:
  LANZAR_OPENGL.bat

- Probar juego con puente seguro:
  LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat

Lectura:
- legacy = simulacion del gestor actual.
- bridge = simulacion del puente seguro.
- dReq = diferencia de solicitudes de detalle.
- dLOD = diferencia de LODs creados.
- dFree = diferencia de liberaciones.
- try-game = el margen parece razonable para probar jugando.

Siguiente etapa recomendada:
Stage33 O - si try-game sale bien, hacer prueba jugable guiada y pedir solo logs concretos si falla.
