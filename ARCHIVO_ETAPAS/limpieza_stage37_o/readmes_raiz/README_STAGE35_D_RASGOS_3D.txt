STAGE35 D - RASGOS 3D

Objetivo:
- Usar geometria 3D para rasgos importantes de la cabeza.
- Depender menos de la imagen para nariz y orejas.
- Preparar variantes futuras de raza como elfo o duende.

Cambios:
- Se agrego render_head_features().
- La nariz del avatar texturizado ahora se dibuja como pieza 3D.
- Se agregaron orejas 3D laterales.
- render_player_avatar acepta:
  - nose_style
  - ear_style
- NPCs guardan:
  - nose_style
  - ear_style
- Estilos preparados:
  - human
  - elf
  - duende
  - none

Notas:
- Por ahora los NPCs usan orejas humanas.
- Las texturas pueden seguir teniendo sombreado facial, pero la lectura principal de nariz/orejas ya viene del modelo.
- No se hizo ZIP.
