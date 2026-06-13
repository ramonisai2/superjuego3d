JUEGO 1.6 - STAGE38 N - ARRANQUE NO ES CAIDA

Objetivo:
- Evitar que una muestra vacia al iniciar sesion cuente como caida real.
- Mantener la advertencia de caidas cuando el mundo ya esta dibujando.
- Hacer mas justa la confianza del preset recomendado.

Cambios:
- preset_runtime_log_analyzer.py ignora muestras con fps 0, verts 0, chunks 0 y entidades 0.
- El reporte muestra cuantas muestras vacias fueron ignoradas.
- recommended_graphics_preset.txt agrega ignored_empty_startup_samples.
- version_info.py pasa a Stage38 N.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
