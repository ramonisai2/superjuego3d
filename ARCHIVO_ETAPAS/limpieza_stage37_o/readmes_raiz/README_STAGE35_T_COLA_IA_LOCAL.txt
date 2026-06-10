JUEGO 1.6 - Stage35 T - COLA IA LOCAL

Objetivo
- Preparar respuestas IA sin bloquear el juego.
- Procesar pocas solicitudes por tick cuando exista un modelo local.
- Mantener cache, saneamiento y fallback determinista.

Cambios
- NPC_AI_REPLY_QUEUE guarda solicitudes pendientes.
- NPC_AI_COMPLETED_REPLIES guarda respuestas listas.
- queue_npc_ai_reply() encola una solicitud.
- drain_npc_ai_queue() procesa con presupuesto max_items.
- pop_npc_ai_reply() recupera respuestas terminadas.
- NPC.queue_reply_to_player() y NPC.pop_queued_reply() exponen el flujo.

Notas
- No hay LLM todavia.
- El responder futuro recibe packet y prompt.
- No se genero ZIP.
