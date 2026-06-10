Stage37 C - LOG DE PRESETS

Objetivo
- Guardar muestras compactas de rendimiento por preset.
- Comparar low/balanced/high sin depender solo de sensacion.
- Tener datos listos si hay bajones al moverse.

Cambios
- Se crea logs/preset_runtime_samples.log.
- Cada muestra guarda preset, FPS, FPS promedio, escala adaptativa, chunks, entidades, vertices, uploads, streaming y densidad.
- El log se escribe cada 3 segundos por defecto.
- Se puede apagar con JUEGO_PRESET_SAMPLE_LOG=0.
- Se puede ajustar intervalo con JUEGO_PRESET_SAMPLE_LOG_INTERVAL.

Notas
- El log es compacto y no guarda informacion personal.
- No cambia gameplay ni render.
- No se genero ZIP.
