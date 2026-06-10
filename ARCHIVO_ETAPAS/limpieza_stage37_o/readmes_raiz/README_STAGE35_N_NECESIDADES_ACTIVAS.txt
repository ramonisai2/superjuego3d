JUEGO 1.6 - Stage35 N - NECESIDADES ACTIVAS

Objetivo
- Hacer que las rutinas de NPC tengan efecto real sobre sus necesidades.
- Evitar que los NPCs solo cambien de texto o destino.
- Mantenerlo barato, determinista y sin inventario real todavia.

Cambios
- apply_activity_effects() calcula cercania al ancla activa.
- Si el NPC esta cerca del objetivo correcto recupera:
  comida, agua, energia, seguridad o social.
- Descanso, seguridad y social reducen estres.
- En calma, trabajar cerca del ancla de oficio mantiene un poco energia/social.
- needs_snapshot() expone activity_effect y activity_progress.

Notas
- No hay edificios ni pathfinding real todavia.
- No hay LLM todavia.
- No se genero ZIP.
