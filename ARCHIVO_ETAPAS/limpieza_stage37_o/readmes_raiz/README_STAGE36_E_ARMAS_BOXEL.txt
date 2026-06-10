Stage36 E - ARMAS BOXEL

Objetivo:
- Renderizar armas crafteadas como boxeles 3D.
- Mantener el mismo tamano visual de cubitos del juego.
- Diferenciar Palo, Palo con fibras y Palo con piedra.

Cambios:
- Se agrega render_crafted_weapon().
- render_player_avatar() acepta held_weapon.
- main.py pasa el arma equipada del jugador al render.

Visual:
- Palo: cuerpo de madera hecho con segmentos boxel.
- Palo con fibras: mismo palo con ataduras verdes.
- Palo con piedra: palo con fibras mas cabeza de piedra.

Notas:
- Usa draw_boxel() y BOXEL_UNIT.
- Por ahora se ve en tercera persona.
- No cambia dano, alcance ni durabilidad; solo visual.
