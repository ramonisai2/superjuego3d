JUEGO 1.6 - Stage39 I - WORLD RUNTIME MODULE

Objetivo
- Reducir main.py moviendo consultas de altura, agua y contexto del jugador.
- Mantener nombres fachada para no romper Player, NPCs, enemigos y chunks.
- Centralizar caches de altura y agua por semilla.

Cambios
- Se agrego juego3d_v1_5\main_world_runtime.py.
- WorldRuntime administra get_total_height, is_water_position y update_player_world_context.
- main.py actualiza world_runtime.seed al elegir semilla desde el menu.

Notas
- No se genero ZIP.
