JUEGO 1.6 - Stage39 G - SPAWN SAFETY MODULE

Objetivo
- Reducir main.py moviendo busqueda de spawn seco y reaparicion segura.
- Mantener NPCs/enemigos fuera del agua al aparecer.
- Mantener logs de busqueda segura con la semilla actual.

Cambios
- Se agrego juego3d_v1_5\main_spawn.py.
- main.py usa SpawnRuntime para find_dry_position, find_safe_player_position y set_player_respawn_point.
- Al elegir semilla desde el menu, main.py actualiza spawn_runtime.seed.

Notas
- No se genero ZIP.
