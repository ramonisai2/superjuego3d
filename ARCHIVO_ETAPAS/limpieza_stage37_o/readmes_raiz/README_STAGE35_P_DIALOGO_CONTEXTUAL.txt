JUEGO 1.6 - Stage35 P - DIALOGO CONTEXTUAL

Objetivo
- Hacer que los NPCs respondan segun su estado real.
- Usar necesidad, animo, actitud, oficio, confianza y memoria.
- Mantenerlo determinista y barato antes de meter un LLM local.

Cambios
- dialogue_tone_prefix() deriva el tono desde stance.
- contextual_dialogue_line() elige lineas por necesidad, animo y confianza.
- conversation_context() incluye tone.
- interactuar() registra cada linea como evento dialogue en memoria.
- export_npc_memory() usa version stage35_p_npc_memory_v2.

Notas
- No hay modelo de lenguaje todavia.
- Las respuestas son plantillas contextuales, no texto generado por IA.
- No se genero ZIP.
