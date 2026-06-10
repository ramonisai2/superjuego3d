Stage37 K - OPENGL RECOMENDADO

Objetivo:
- Usar el resultado del analisis para arrancar con el preset recomendado.
- Mantener balanced como respaldo si faltan muestras.
- Evitar convertir una prueba incompleta en decision permanente.

Resultado:
- El analizador crea logs/recommended_graphics_preset.txt.
- Si la comparacion tiene suficientes muestras, guarda low, balanced o high.
- Si faltan muestras, guarda balanced con confianza baja.
- Se agrega LANZAR_OPENGL_RECOMENDADO.bat.
- PROBAR_PRESETS_OPENGL.bat agrega la opcion 8.

Uso recomendado:
1. Probar low, balanced y high desde PROBAR_PRESETS_OPENGL.bat.
2. Analizar todo con la opcion 5.
3. Usar la opcion 8 o LANZAR_OPENGL_RECOMENDADO.bat.

Nota:
- OpenGL sigue siendo la ruta estable.
- Vulkan sigue experimental.
- No crea ZIP.
