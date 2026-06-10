Stage37 F - ANALISIS POR SESION

Objetivo
- Comparar presets sin mezclar datos viejos.
- Permitir analizar todo el historial o solo la ultima sesion.
- Mantener el flujo simple con archivos .bat.

Cambios
- El analizador acepta JUEGO_PRESET_ANALYZE_SESSION=all/latest/id.
- ANALIZAR_PRESETS_GRAFICOS.bat analiza todo el log.
- Se agrega ANALIZAR_PRESETS_ULTIMA_SESION.bat.
- El resultado muestra latest_session y analyzed_session.

Notas
- Si no hay muestras, sigue avisando sin romper.
- No cambia gameplay ni render.
- No se genero ZIP.
