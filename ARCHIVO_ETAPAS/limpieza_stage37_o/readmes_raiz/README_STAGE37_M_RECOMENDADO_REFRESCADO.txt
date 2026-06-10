Stage37 M - RECOMENDADO REFRESCADO

Objetivo:
- Evitar que LANZAR_OPENGL_RECOMENDADO.bat use una recomendacion vieja.
- Recalcular el analisis justo antes de arrancar.
- Avisar cuando la confianza sigue baja.

Resultado:
- LANZAR_OPENGL_RECOMENDADO.bat ejecuta el analizador antes de leer recommended_graphics_preset.txt.
- Si faltan pruebas completas, muestra una advertencia.
- Si la confianza es baja, el preset usado sigue siendo balanced.
- Si la confianza es alta, usa el ganador del analisis actualizado.

Uso recomendado:
1. Probar low, balanced y high.
2. Usar LANZAR_OPENGL_RECOMENDADO.bat u opcion 8 del menu.
3. El lanzador refresca el analisis automaticamente.

Nota:
- No cambia OpenGL estable.
- No activa Vulkan.
- No crea ZIP.
