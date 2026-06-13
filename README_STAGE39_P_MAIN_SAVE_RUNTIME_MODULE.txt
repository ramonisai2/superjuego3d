JUEGO 1.6 - Stage39 P - MAIN SAVE RUNTIME MODULE

Objetivo
--------
Reducir main.py separando los atajos de guardado y recarga en caliente.

Cambios
-------
- Se agrego juego3d_v1_5\main_save_runtime.py.
- main.py importa handle_save_hotkeys().
- F5 guarda la partida con save_game().
- F9 carga la partida si la semilla coincide y reposiciona al jugador en suelo seguro.

Resultado de tamano
-------------------
- main.py queda en 940 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_save_runtime.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar F5, F9, guardado runtime, recarga en caliente o reposicion segura tras cargar, abre primero:
juego3d_v1_5\main_save_runtime.py
