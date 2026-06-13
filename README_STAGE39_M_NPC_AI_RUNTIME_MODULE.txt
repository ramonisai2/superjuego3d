JUEGO 1.6 - Stage39 M - NPC AI RUNTIME MODULE

Objetivo
--------
Reducir game\npc_manager.py separando el runtime de dialogo e IA local de NPCs.

Cambios
-------
- Se agrego juego3d_v1_5\game\npc_ai_runtime.py.
- Cache, cola, telemetria, prompts y adaptadores de modelo local viven en ese modulo.
- game\npc_manager.py conserva la clase NPC y reexporta/importa funciones publicas para no romper imports antiguos.
- game\npc_memory.py sigue siendo el dueno de memoria, confianza, notas e import/export.
- game\npc_identity.py sigue siendo el dueno de nombres, profesiones, skins por zonas e IDs estables.

Archivos principales
--------------------
- juego3d_v1_5\game\npc_ai_runtime.py
- juego3d_v1_5\game\npc_manager.py
- juego3d_v1_5\game\npc_memory.py
- juego3d_v1_5\game\npc_identity.py

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\game\npc_manager.py juego3d_v1_5\game\npc_ai_runtime.py juego3d_v1_5\main.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar dialogo, cache, cola, backend local o telemetria de NPCs, abre primero:
juego3d_v1_5\game\npc_ai_runtime.py

Si vas a tocar movimiento, necesidades o render del humanoide NPC, abre:
juego3d_v1_5\game\npc_manager.py
