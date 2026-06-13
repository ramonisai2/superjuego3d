JUEGO 1.6 - Stage39 S - MAIN RUNTIME LOGGING

Objetivo
--------
Reducir main.py separando logs de consola y muestras de preset.

Cambios
-------
- main_preset_logging.py ahora contiene update_runtime_logs().
- update_runtime_logs() imprime FOV/chunk/vida/stamina/enemigos.
- Tambien imprime el resumen STREAM-BRIDGE cuando esta activo.
- Las muestras de preset siguen usando append_preset_runtime_sample().

Resultado de tamano
-------------------
- main.py queda en 881 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_preset_logging.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar logs de consola, stream bridge print, preset_runtime_samples.log o campos de rendimiento del preset, abre primero:
juego3d_v1_5\main_preset_logging.py
