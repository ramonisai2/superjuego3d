JUEGO 1.6 - Stage35 S - CACHE IA LOCAL

Objetivo
- Proteger FPS antes de conectar un modelo local real.
- Evitar respuestas IA repetidas para el mismo NPC, pregunta y estado.
- Mantener lineas cortas y limpias para la UI.

Cambios
- NPC_AI_REPLY_CACHE guarda respuestas por clave de NPC/pregunta/estado.
- La clave usa bloques de confianza para no invalidarse en cada saludo.
- _clean_ai_reply() limpia saltos de linea y limita longitud.
- npc_ai_cache_stats() expone estado de cache.
- clear_npc_ai_cache() limpia la cache.
- NPC.reply_to_player() acepta use_cache=True.

Notas
- No hay LLM todavia.
- El fallback determinista sigue activo si no se pasa responder.
- No se genero ZIP.
