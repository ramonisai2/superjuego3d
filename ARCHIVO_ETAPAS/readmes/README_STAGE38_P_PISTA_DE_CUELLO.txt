JUEGO 1.6 - STAGE38 P - PISTA DE CUELLO

Objetivo:
- Convertir las peores muestras en una pista accionable.
- Distinguir entre render/LOD, streaming/carga y CPU/logica.
- Ayudar a decidir el siguiente ajuste de rendimiento.

Cambios:
- preset_runtime_log_analyzer.py calcula bottleneck_hint.
- El reporte muestra la pista junto a la recomendacion.
- recommended_graphics_preset.txt guarda bottleneck_hint.

Lectura:
- Render/LOD: muchos vertices o chunks LOD, pocos uploads.
- Streaming: uploads altos durante los tirones.
- CPU/logica: poca carga visible pero FPS bajo.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
