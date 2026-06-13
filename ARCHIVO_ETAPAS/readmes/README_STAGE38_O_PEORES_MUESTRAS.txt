JUEGO 1.6 - STAGE38 O - PEORES MUESTRAS

Objetivo:
- Ver donde ocurren los peores tirones reales.
- Mostrar contexto de carga junto al FPS bajo.
- Preparar la siguiente investigacion de rendimiento.

Cambios:
- preset_runtime_log_analyzer.py agrega una lista de peores muestras reales.
- El reporte muestra preset, fps, vertices, chunks visibles, chunks LOD, uploads, chunks ocultos y sesion.
- Las muestras vacias de arranque siguen ignoradas.

Uso:
- Revisar juego3d_v1_5\logs\preset_runtime_report.txt.
- Mirar la seccion Peores muestras reales.
- Si hay uploads altos, revisar streaming/carga.
- Si hay vertices altos, revisar LOD/detalle.
- Si hay fps bajos con poca carga, revisar movimiento/contexto/CPU.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
