STAGE35 B - NPCS CON SKIN

Objetivo:
- Hacer que los NPCs usen la skin del jugador como base visual.
- Mantener diferencias visibles por profesion o estado especial.
- No cambiar identidad, nombres, atributos ni conversaciones.

Cambios:
- render_player_avatar ahora acepta accessory_color, legendary y debug_hitbox.
- NPC.render usa render_player_avatar en lugar del humanoide voxel plano.
- Si la textura no carga, el render cae automaticamente al humanoide voxel anterior.
- Los NPCs conservan color de profesion como acento/accesorio.
- Los NPCs ahora pasan walk_phase y move_amount para animar brazos/piernas al caminar.

Notas:
- Todos comparten la misma skin base por ahora.
- La siguiente mejora visual puede ser variaciones por NPC: ropa, pelo, accesorios o tonos.
- No se hizo ZIP.
