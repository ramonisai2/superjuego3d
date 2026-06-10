JUEGO 1.6 - Stage35 U - ESTADO IA LOCAL

Objetivo
- Hacer visible el estado del puente IA local.
- Diagnosticar cola, cache y respuestas pendientes por NPC.
- Preparar UI/logs antes de conectar un modelo real.

Cambios
- npc_ai_runtime_stats() agrupa cache y cola.
- npc_ai_pending_for() busca solicitud pendiente por npc_id.
- npc_ai_status_for() resume estado por NPC.
- NPC.ai_status() expone queued/ready/idle.
- needs_snapshot() incluye ai_status.

Notas
- No hay LLM todavia.
- No se agrego UI nueva todavia.
- No se genero ZIP.
