JUEGO 1.6 - Stage35 I - EQUIPO BOXEL

Objetivo
- Activar el equipo visible en la espalda de los NPCs humanos.
- Mantener martillos, armas y herramientas con la misma unidad BOXEL_UNIT.
- Separar identidad visual de gameplay: por ahora no modifican ataques ni inventario.

Cambios
- NPC.favorite_tool se conserva como dato de profesion.
- NPC.back_tool convierte ese dato en pieza visible.
- render_back_tool acepta:
  hammer, axe, pickaxe, hoe, bow, staff, satchel, sword.

Notas
- Todas las piezas nuevas se dibujan con draw_boxel().
- Las herramientas son visuales y quedan listas para un sistema futuro de profesiones/oficios.
- No se genero ZIP.
