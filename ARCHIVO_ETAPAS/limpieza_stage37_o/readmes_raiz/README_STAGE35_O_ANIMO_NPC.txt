JUEGO 1.6 - Stage35 O - ANIMO NPC

Objetivo
- Convertir necesidades, estres, confianza y oficio en estado conversable.
- Preparar una capa compacta para dialogos futuros con IA local.
- Evitar meter un modelo de lenguaje antes de tener estado interno solido.

Cambios
- mood_for_npc() calcula mood, stance y mood_detail.
- Cada NPC guarda mood, stance y mood_detail.
- needs_snapshot() incluye conversation_context.
- La memoria guarda last_mood y last_stance.
- interactuar() muestra estado y actitud.

Notas
- No hay LLM todavia.
- No se agrego combate ni inventario por profesion.
- No se genero ZIP.
