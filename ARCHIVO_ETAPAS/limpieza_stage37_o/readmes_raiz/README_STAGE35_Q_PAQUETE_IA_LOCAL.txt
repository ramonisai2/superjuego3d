JUEGO 1.6 - Stage35 Q - PAQUETE IA LOCAL

Objetivo
- Preparar un paquete compacto para dialogos futuros con IA local.
- No ejecutar todavia ningun modelo de lenguaje.
- Mantener identidad, oficio, necesidades y recuerdos controlados por el juego.

Cambios
- compact_memory_notes() resume recuerdos recientes.
- npc_ai_context_packet() construye un dict serializable con:
  identidad, estado, oficio, memoria y reglas de dialogo.
- NPC.ai_context_packet() expone el paquete desde cada NPC.
- needs_snapshot() marca ai_context_ready=True.

Notas
- No hay LLM todavia.
- El paquete evita mandar datos de mas y ayuda a no cambiar nombres ni atributos.
- No se genero ZIP.
