JUEGO 1.6 - Stage39 F - PRESET LOGGING MODULE

Objetivo
- Reducir main.py moviendo logs de diagnostico de presets.
- Mantener las muestras de FPS, vertices, LOD, densidad y recursos.
- Dejar el bucle principal mas facil de leer para LLM local.

Cambios
- Se agrego juego3d_v1_5\main_preset_logging.py.
- main.py usa append_preset_runtime_sample, append_preset_session_start y world_detail_debug_status.
- No cambia el formato esperado por los analizadores de preset.

Notas
- No se genero ZIP.
