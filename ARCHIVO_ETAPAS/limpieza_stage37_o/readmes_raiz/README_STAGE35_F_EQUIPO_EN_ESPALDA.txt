STAGE35 F - EQUIPO EN ESPALDA

Objetivo:
- Limpiar los NPCs de cubos 3D que tapaban la textura.
- Quitar el peto frontal de color de profesion.
- Quitar el cabello 3D encima del atlas.
- Reservar la espalda para una herramienta o arma favorita.

Cambios:
- render_player_avatar acepta:
  - show_hair_volume
  - front_gear
  - back_tool
- Los NPCs usan:
  - show_hair_volume=False
  - front_gear="none"
  - back_tool=favorite_tool
- Se agrego render_back_tool().
- Cada NPC ahora tiene favorite_tool:
  - carpintero: hammer
  - recolector: axe
  - guardia/hostil: sword
  - otros: tool

Notas:
- El jugador puede seguir usando el render con volumen completo.
- Los NPCs dependen mas de su textura modular y menos de cubos frontales.
- No se hizo ZIP.
