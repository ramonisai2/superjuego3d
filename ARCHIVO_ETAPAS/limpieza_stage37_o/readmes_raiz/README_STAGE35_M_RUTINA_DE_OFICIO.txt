JUEGO 1.6 - Stage35 M - RUTINA DE OFICIO

Objetivo
- Dar a los NPCs una rutina simple basada en oficio y necesidades.
- Evitar IA pesada por ahora: solo actividad, anclas y objetivos baratos.
- Preparar el terreno para comportamiento mas creible por profesion.

Cambios
- Cada NPC crea anclas deterministas:
  work_anchor, rest_anchor y social_anchor.
- activity_for_need() traduce necesidades a actividad.
- choose_activity_target() mueve el destino hacia el ancla adecuada.
- needs_snapshot() expone activity, activity_detail y work_anchor.
- La memoria guarda last_activity.

Notas
- No hay LLM todavia.
- No se agregan edificios ni pathfinding real todavia.
- No se genero ZIP.
