JUEGO 1.6 - Stage35 W - BACKEND IA INYECTABLE

Objetivo
- Permitir enchufar un backend local real sin reescribir NPCs.
- Mantener fallback limpio si el backend falla.
- Evitar dependencia directa de llama.cpp, Ollama u otro motor.

Cambios
- LocalNPCModelAdapter acepta backend callable.
- status() reporta has_backend.
- reply() usa backend si enabled=True y backend existe.
- set_npc_local_model_backend() instala un callable.
- clear_npc_local_model_backend() vuelve a modo dry-run seguro.

Notas
- Todavia no se conecta un binario/modelo real.
- El backend recibe packet y prompt.
- No se genero ZIP.
