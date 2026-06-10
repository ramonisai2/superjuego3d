Stage37 L - COMPARACION JUSTA

Objetivo:
- Evitar que una prueba incompleta elija ganador.
- Exigir datos suficientes de low, balanced y high.
- Mantener balanced como respaldo mientras falten presets.

Resultado:
- El analizador pide al menos 4 muestras por preset.
- El reporte muestra presets listos y presets faltantes.
- El mejor candidato puede aparecer como parcial.
- LANZAR_OPENGL_RECOMENDADO.bat solo usa el ganador con confianza alta.
- Si faltan presets, el recomendado sigue siendo balanced.

Uso recomendado:
1. Limpiar log desde PROBAR_PRESETS_OPENGL.bat.
2. Probar low, balanced y high 1-2 minutos cada uno.
3. Analizar todo con la opcion 5.
4. Usar opcion 8 solo cuando el reporte diga comparacion suficiente.

Nota:
- No cambia el render.
- No cambia Vulkan.
- No crea ZIP.
