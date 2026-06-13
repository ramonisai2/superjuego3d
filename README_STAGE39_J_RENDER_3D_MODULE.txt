JUEGO 1.6 - Stage39 J - RENDER 3D MODULE

Objetivo
- Reducir main.py moviendo render 3D y armado del frame graph.
- Mantener render_3d como fachada pequena para engine.run.
- Devolver render_stats, z_target_screen y npc_label_screen de forma explicita.

Cambios
- Se agrego juego3d_v1_5\main_render3d.py.
- render_runtime_3d administra skybox, fog, chunks visibles, entidades y arma en primera persona.
- main.py ya no importa FogConfig ni render_player_avatar/render_first_person_weapon.

Notas
- No se genero ZIP.
