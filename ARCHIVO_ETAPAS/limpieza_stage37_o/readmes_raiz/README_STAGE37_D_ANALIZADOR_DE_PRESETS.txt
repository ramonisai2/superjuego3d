Stage37 D - ANALIZADOR DE PRESETS

Objetivo
- Leer logs/preset_runtime_samples.log sin revisar lineas a mano.
- Comparar low/balanced/high por FPS, caidas y carga renderizada.
- Recomendar un candidato segun muestras reales.

Cambios
- Se agrega motor_juegos/preset_runtime_log_analyzer.py.
- Se agrega ANALIZAR_PRESETS_GRAFICOS.bat.
- El analizador resume FPS promedio, FPS minimo, escala adaptativa, vertices, uploads, chunks ocultos, entidades ocultas y streaming.
- El analizador da una recomendacion corta.

Notas
- Necesita que el juego haya corrido unos segundos para tener muestras.
- No cambia gameplay ni render.
- No se genero ZIP.
