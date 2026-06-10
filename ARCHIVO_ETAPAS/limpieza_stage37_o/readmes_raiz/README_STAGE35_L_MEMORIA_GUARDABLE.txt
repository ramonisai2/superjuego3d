JUEGO 1.6 - Stage35 L - MEMORIA GUARDABLE

Objetivo
- Hacer que la memoria por ID de los NPCs pueda guardarse y cargarse.
- Mantener compatibilidad con partidas antiguas que no tengan npc_memory.
- Preparar persistencia real para conversaciones e IA compacta futura.

Cambios
- npc_manager.py agrega:
  export_npc_memory(), import_npc_memory() y clear_npc_memory().
- save_system.py escribe npc_memory dentro de world_save.json.
- load_game_data() restaura npc_memory cuando existe.
- get_save_summary() muestra cuantas memorias NPC trae el save.

Notas
- No se guardan NPCs completos todavia, solo recuerdos por ID.
- El sistema sigue usando OpenGL estable como ruta jugable.
- No se genero ZIP.
