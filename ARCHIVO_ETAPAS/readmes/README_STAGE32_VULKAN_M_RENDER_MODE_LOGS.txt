STAGE32 VULKAN M - LANZADORES + LOGS DE RENDER

Objetivo:
- Mantener dos rutas claras:
  1) OpenGL estable / jugable.
  2) Vulkan experimental / pruebas.
- Agregar reportes y logs para saber qué backend se pidió realmente.

Nuevos / mejorados:
- motor_juegos/render_mode_status.py
- diagnostico_render.py
- DIAGNOSTICO_RENDER.bat
- LANZAR_OPENGL.bat
- LANZAR_VULKAN_EXPERIMENTAL.bat
- LANZADOR_GRAFICO_RENDER.bat

Logs:
- juego3d_v1_5/logs/render_backend_status.log

Uso:
- Jugar normal:
  LANZAR_OPENGL.bat

- Probar Vulkan experimental:
  LANZAR_VULKAN_EXPERIMENTAL.bat

- Elegir con ventana:
  LANZADOR_GRAFICO_RENDER.bat

- Revisar configuración sin iniciar juego:
  DIAGNOSTICO_RENDER.bat

Notas:
- OpenGL sigue siendo el modo estable.
- Vulkan sigue siendo experimental.
- Esta etapa ayuda a detectar si realmente se está lanzando OpenGL o Vulkan antes de seguir integrando present real.
