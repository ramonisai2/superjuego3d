Stage37 I - REPORTE DE PRESETS

Objetivo:
- Guardar el resultado del analisis en un archivo facil de revisar.
- Evitar perder la recomendacion al cerrar la consola.
- Mantener la comparacion de low, balanced y high simple.

Resultado:
- El analizador crea logs/preset_runtime_report.txt.
- El reporte incluye estado, sesiones, mejor candidato y recomendacion.
- El reporte incluye una tabla por preset con FPS promedio, FPS minimo, escala, vertices, uploads y streaming.
- Si no hay muestras, el reporte explica el flujo recomendado.

Uso recomendado:
1. Ejecutar PROBAR_PRESETS_OPENGL.bat.
2. Probar low, balanced y high.
3. Elegir analizar todo.
4. Revisar juego3d_v1_5/logs/preset_runtime_report.txt.

Nota:
- No cambia el render.
- No cambia OpenGL/Vulkan.
- No crea ZIP.
