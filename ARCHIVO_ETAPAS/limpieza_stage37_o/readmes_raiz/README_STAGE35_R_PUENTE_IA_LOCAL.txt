JUEGO 1.6 - Stage35 R - PUENTE IA LOCAL

Objetivo
- Preparar el puente para conectar un modelo local compacto en el futuro.
- No ejecutar todavia ningun modelo.
- Mantener dialogo determinista como fallback.

Cambios
- build_npc_dialogue_prompt() convierte el paquete IA en prompt corto.
- npc_local_ai_reply() acepta un responder opcional.
- NPC.dialogue_prompt() expone el prompt.
- NPC.reply_to_player() usa responder si existe; si no, cae a interactuar().

Notas
- El juego sigue funcionando sin IA externa.
- El responder futuro recibira packet y prompt.
- No se genero ZIP.
