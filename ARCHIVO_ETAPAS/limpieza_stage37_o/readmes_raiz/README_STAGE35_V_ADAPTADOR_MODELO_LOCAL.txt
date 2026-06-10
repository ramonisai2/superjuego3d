JUEGO 1.6 - Stage35 V - ADAPTADOR MODELO LOCAL

Objetivo
- Preparar una interfaz reemplazable para un modelo local real.
- Mantener un modo dry-run que no depende de llama.cpp, Ollama ni red.
- Evitar que los NPCs dependan directamente del backend del modelo.

Cambios
- LocalNPCModelAdapter implementa reply(), status() y __call__().
- NPC_LOCAL_MODEL_ADAPTER es el adaptador global por defecto.
- get_npc_local_model_adapter() devuelve el adaptador activo.
- configure_npc_local_model() permite cambiar nombre, enabled y max_prompt_chars.
- npc_local_model_status() expone diagnostico del adaptador.
- NPC.reply_to_player() usa el adaptador por defecto si no se pasa responder.

Notas
- No hay modelo real conectado todavia.
- enabled=False responde en dry-run determinista.
- enabled=True reporta no_model_backend_configured hasta conectar un backend.
- No se genero ZIP.
