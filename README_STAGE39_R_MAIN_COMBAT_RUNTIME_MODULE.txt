JUEGO 1.6 - Stage39 R - MAIN COMBAT RUNTIME MODULE

Objetivo
--------
Reducir main.py separando combate, proyectiles y marcado visual de objetivos.

Cambios
-------
- Se agrego juego3d_v1_5\main_combat_runtime.py.
- update_combat_runtime() maneja ataque con mano/arma, lanzamiento de piedra, sonidos de golpe/lanzamiento y actualizacion de proyectiles.
- El marcado visual de enemigo cercano y Z-lock queda junto al combate.
- main.py conserva el estado devuelto: stone_projectiles, z_target, z_target_type y last_attack_time.

Resultado de tamano
-------------------
- main.py queda en 897 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_combat_runtime.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar golpe, lanzamiento de piedra, proyectiles, sonidos de ataque, selected/z_locked o asistencia de objetivo cercano, abre primero:
juego3d_v1_5\main_combat_runtime.py
