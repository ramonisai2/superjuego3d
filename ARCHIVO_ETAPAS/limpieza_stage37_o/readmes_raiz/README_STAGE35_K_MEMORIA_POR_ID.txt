JUEGO 1.6 - Stage35 K - MEMORIA POR ID

Objetivo
- Dar a cada NPC una memoria ligera usando su ID estable.
- Recordar encuentros, confianza, ultima necesidad, intencion y una nota corta.
- Preparar conversaciones e IA compacta sin meter todavia un modelo de lenguaje.

Cambios
- Se agrego NPC_MEMORY_REGISTRY.
- npc_memory_for() crea o recupera memoria por npc.id.
- remember_npc_event() guarda eventos de interaccion y sube confianza.
- npc_memory_snapshot() expone un resumen limpio.
- NPC.interactuar() ya usa la memoria para contar encuentros.
- NPC.needs_snapshot() incluye el bloque memory.

Notas
- La memoria vive durante la sesion actual.
- Todavia no se escribe en el save del mundo.
- No se genero ZIP.
