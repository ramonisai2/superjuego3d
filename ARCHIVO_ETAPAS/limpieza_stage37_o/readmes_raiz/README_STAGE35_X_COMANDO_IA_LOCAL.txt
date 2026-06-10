JUEGO 1.6 - Stage35 X - COMANDO IA LOCAL

Objetivo
- Preparar comunicacion con un proceso local de IA.
- No depender todavia de llama.cpp, Ollama ni otro motor especifico.
- Mantener timeout y fallback seguro para no bloquear el juego.

Cambios
- LocalCommandNPCBackend ejecuta un comando local sin shell.
- El backend envia JSON por stdin:
  packet, prompt y max_chars.
- El comando puede responder texto plano o JSON con {"reply": "..."}.
- configure_npc_command_backend() instala el backend en el adaptador global.
- npc_local_model_status() reporta el estado del command_backend.

Notas
- No se configuro ningun modelo real.
- No se genero ZIP.
