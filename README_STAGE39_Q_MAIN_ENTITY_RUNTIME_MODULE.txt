JUEGO 1.6 - Stage39 Q - MAIN ENTITY RUNTIME MODULE

Objetivo
--------
Reducir main.py separando interaccion NPC y actualizacion runtime de entidades.

Cambios
-------
- Se agrego juego3d_v1_5\main_entity_runtime.py.
- handle_npc_interaction() gestiona highlight, prompt, descripcion y dialogo del NPC cercano.
- update_entities_runtime() actualiza NPCs, enemigos y restos con presupuesto por distancia.
- main.py conserva el flujo principal y recibe los resultados visibles para el HUD.

Resultado de tamano
-------------------
- main.py queda en 919 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_entity_runtime.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar dialogo cercano de NPC, prompt de interaccion, highlights o actualizacion runtime de NPCs/enemigos/restos, abre primero:
juego3d_v1_5\main_entity_runtime.py
