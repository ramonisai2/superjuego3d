JUEGO 1.6 - STAGE38 M - CONFIANZA HONESTA

Objetivo:
- Evitar que una comparacion completa oculte caidas fuertes de FPS.
- Mantener el mejor preset recomendado, pero bajar la confianza si hay tirones.
- Actualizar la verificacion de estructura con piezas nuevas.

Cambios:
- preset_runtime_log_analyzer.py detecta presets con fps_min menor a 24.
- Si hay caidas fuertes, confidence queda low aunque existan muestras de low, balanced y high.
- recommended_graphics_preset.txt agrega severe_drop_presets.
- LANZAR_OPENGL_RECOMENDADO.bat muestra advertencia general cuando confidence no es ok.
- VERIFICAR_ESTRUCTURA_JUEGO.bat revisa SELECCIONAR_PYTHON_REPARACION.bat y helpers nuevos.
- VERIFICAR_ESTRUCTURA_JUEGO.bat usa checks directos para evitar salida duplicada en pruebas automaticas.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
