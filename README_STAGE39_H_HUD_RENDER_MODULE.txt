JUEGO 1.6 - Stage39 H - HUD RENDER MODULE

Objetivo
- Reducir main.py moviendo el render 2D del HUD runtime.
- Mantener UI, FPS, debug de Admin Hub, Z-target y prompts iguales.
- Dejar render_2d como fachada pequena para engine.run.

Cambios
- Se agrego juego3d_v1_5\main_hud_render.py.
- main.py usa render_runtime_hud con dependencias explicitas.

Notas
- No se genero ZIP.
