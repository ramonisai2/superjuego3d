Stage36 R - FPS HUD E IMPOSTORES BAJOS

Objetivo
- Ver FPS sin abrir el panel F1.
- Llevar la idea de impostores a decoracion pequena.
- Reducir geometria de arbustos, flores y hongos.

Cambios
- Se agrega draw_fps_counter() al HUD.
- render_2d() muestra FPS siempre en una placa pequena.
- Se agrega _add_deco_impostor_to_mesh().
- Hongos usan planos cruzados para tallo y sombrero.
- Flores usan planos cruzados para tallo y flor.
- Arbustos verdes y secos usan planos cruzados en vez de rocas/cajas complejas.

Notas
- Los chunks LOD lejanos siguen sin decoracion; estos impostores aplican al chunk detallado.
- El estilo queda mas pseudo 3D/retro.
- No cambia recoleccion ni posiciones de decoracion.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
