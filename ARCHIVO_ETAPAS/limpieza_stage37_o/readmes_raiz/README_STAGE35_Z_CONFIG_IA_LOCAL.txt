Stage35 Z - CONFIG IA LOCAL

Objetivo:
- Guardar y cargar la configuracion del puente de IA local.
- Evitar repetir a mano comando, timeout y limite de prompt.
- No ejecutar ningun modelo automaticamente al cargar archivos.

Cambios:
- Se agrega npc_local_model_config_snapshot().
- Se agrega save_npc_local_model_config().
- Se agrega load_npc_local_model_config().
- Se agrega apply_npc_local_model_config().

Comportamiento seguro:
- load_npc_local_model_config() solo lee y normaliza si apply_config es False.
- apply_npc_local_model_config() instala el backend, pero no ejecuta el comando.
- El comando solo corre con probe_npc_local_model_backend() o al pedir una respuesta real.

Archivo default:
- juego3d_v1_5/npc_local_ai_config.json

Notas:
- El timeout se limita entre 0.1 y 30 segundos.
- max_prompt_chars se limita entre 120 y 6000.
- El comando se guarda como lista, no como texto shell.
