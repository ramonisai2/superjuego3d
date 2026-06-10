JUEGO 1.6 - STAGE38 D - SIGUIENTE PASO

Objetivo:
- Hacer que el estado rapido no solo reporte datos.
- Mostrar una accion recomendada al final.
- Priorizar primero lo que impide jugar, luego previews y luego comparacion grafica.

Cambios:
- ESTADO_RAPIDO_JUEGO.bat ahora calcula una prioridad.
- Si falta Python para juego, recomienda instalar dependencias o guardar ruta.
- Si falta Python para previews, lo marca como herramienta incompleta.
- Si el preset tiene confianza baja, muestra que presets faltan por probar.
- Si todo esta listo, recomienda jugar con OpenGL estable o recomendado.

Nota:
- No se cambia gameplay.
- No se cambia OpenGL ni Vulkan.
- No se genera ZIP.
