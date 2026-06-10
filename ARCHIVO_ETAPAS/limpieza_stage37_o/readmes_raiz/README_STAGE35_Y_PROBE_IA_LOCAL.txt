Stage35 Y - PROBE IA LOCAL

Objetivo:
- Probar el puente de IA local antes de usarlo en conversaciones reales.
- Medir si el backend responde, cuanto tarda y que error deja si falla.
- Mantener fallback seguro cuando no hay modelo conectado.

Cambios:
- Se agrega probe_npc_local_model_backend().
- La prueba usa un paquete NPC minimo y un prompt corto.
- El resultado incluye ok, reply, elapsed_ms, used_backend, calls_added, last_error y status.

Uso esperado:
- Primero configurar el backend con configure_npc_command_backend().
- Luego llamar probe_npc_local_model_backend().
- Si ok es true, el puente puede responder.
- Si ok es false, revisar last_error y command_backend.last_error.

Notas:
- No conecta automaticamente ningun motor externo.
- No cambia el comportamiento de juego por defecto.
- No guarda memoria ni modifica NPCs reales.
