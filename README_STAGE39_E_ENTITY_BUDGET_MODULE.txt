JUEGO 1.6 - Stage39 E - ENTITY BUDGET MODULE

Objetivo
- Reducir main.py sin cambiar comportamiento visible.
- Separar el presupuesto de actualizacion de NPCs y enemigos.
- Mantener las entidades cercanas con IA completa y las lejanas con actualizacion espaciada.

Cambios
- Se agrego juego3d_v1_5\game\entity_update_budget.py.
- main.py usa update_npc_with_budget y update_enemy_with_budget.
- Las distancias e intervalos siguen entrando desde main_config.py.

Notas
- Esto ayuda al FPS cuando hay muchas entidades lejos.
- No se genero ZIP.
