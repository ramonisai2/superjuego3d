JUEGO 1.6 - Stage39 L - NPC MEMORY MODULE

Objetivo
- Reducir game\npc_manager.py moviendo memoria persistente de NPCs.
- Mantener confianza, encuentros, notas recientes e import/export.
- Conservar compatibilidad de imports desde npc_manager.py.

Cambios
- Se agrego juego3d_v1_5\game\npc_memory.py.
- npc_manager.py importa npc_memory_for, remember_npc_event, snapshots e import/export.
- need_status_text vive ahora en npc_memory.py.

Notas
- No se genero ZIP.
