STAGE32 VULKAN P - VENTANA DEDICADA VULKAN

Nombre clave:
VENTANA DE OBSIDIANA

Objetivo:
- Crear una prueba controlada con ventana pygame dedicada para revisar si SDL/Vulkan estan listos para surface real.
- Mantener OpenGL como modo estable/jugable.
- Preparar Stage32 Q: wrapper real de surface o puente nativo.

Nuevos archivos:
- motor_juegos/vulkan_dedicated_window_probe.py
- diagnostico_vulkan_ventana.py
- DIAGNOSTICO_VULKAN_VENTANA.bat

Qué prueba:
- pygame y ventana dedicada.
- driver de video SDL.
- import de Vulkan.
- VkInstance y GPU.
- detección de librería SDL2.
- funciones SDL_Vulkan_* disponibles.
- si parece listo para intentar surface real.

Uso:
- Jugar normal:
  LANZAR_OPENGL.bat

- Lanzador gráfico:
  LANZADOR_GRAFICO_RENDER.bat

- Diagnóstico ventana Vulkan:
  DIAGNOSTICO_VULKAN_VENTANA.bat

Notas:
- Esta etapa todavía no reemplaza OpenGL.
- Si el diagnóstico dice surf-ready, la siguiente etapa puede intentar un surface real más agresivo.
- Si no, necesitaremos wrapper nativo/SDL2 directo.
