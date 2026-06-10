Stage36 A - TELEMETRIA IA NPC

Objetivo:
- Medir el costo de las respuestas IA de NPCs.
- Separar cache, backend, fallback y rechazos de cola.
- Detectar errores del backend sin romper la conversacion.

Cambios:
- Se agrega NPC_AI_TELEMETRY.
- Se agrega npc_ai_telemetry_stats().
- Se agrega clear_npc_ai_telemetry().
- npc_ai_runtime_stats() ahora incluye telemetry.

Metricas:
- requests: respuestas registradas.
- backend_replies: respuestas generadas por backend.
- fallback_replies: respuestas seguras cuando el backend no responde.
- cache_hits: respuestas servidas desde cache.
- queue_rejected: peticiones rechazadas por cola llena.
- errors: fallos registrados.
- total_ms, max_ms, last_ms y avg_ms.
- last_source y last_error.

Notas:
- No cambia el contenido de los dialogos.
- No conecta ningun modelo nuevo.
- Sirve para cuidar FPS antes de activar IA local real.
