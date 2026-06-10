STAGE35 C - SKINS MODULARES

Objetivo:
- Dividir la apariencia de NPCs en tres zonas reutilizables:
  - head
  - torso
  - pants
- Permitir que pocos atlas generen muchas combinaciones de NPCs.
- Preparar caras y torsos masculinos/femeninos sin cambiar el sistema de atributos.

Cambios:
- El render texturizado ahora puede cargar varios atlas por entidad.
- render_player_avatar acepta skin_zones.
- Las piernas usan skin_zones["pants"].
- Torso y brazos usan skin_zones["torso"].
- Cabeza usa skin_zones["head"].
- Se agrego cache de texturas para no recargar PNGs cada frame.
- NPCs ahora tienen:
  - skin_preset
  - skin_zones
  - visual_profession
  - face_type
  - torso_type
- Se agregaron presets:
  - base
  - carpintero_viejo
  - ropa_carpintero

Notas:
- La profesion logica del NPC no se reemplaza; visual_profession es solo visual.
- La skin de carpintero viejo puede usarse completa o mezclada por zonas.
- Mas adelante se pueden agregar variantes femeninas de cara y torso con el mismo sistema.
- No se hizo ZIP.
