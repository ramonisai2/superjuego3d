JUEGO 1.6 - Stage39 O - MAIN PRELOAD MODULE

Objetivo
--------
Reducir main.py y separar la precarga inicial de chunks antes de entrar al mundo.

Cambios
-------
- Se agrego juego3d_v1_5\main_preload.py.
- main.py importa preload_initial_chunks desde ese modulo.
- La funcion recibe dependencias explicitas: mundo_chunks, mundo_chunks_simple, render_backend, env, resource_runtime, radios y subdivisiones.
- La precarga sigue creando LOD alrededor y detalle cercano antes de iniciar engine.run().

Resultado de tamano
-------------------
- main.py queda en 964 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_preload.py
py auditar_tamano_py.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si el problema ocurre antes de entrar al mundo, durante "LOD alrededor" o "Detalle 9 chunks cercanos", abre primero:
juego3d_v1_5\main_preload.py
