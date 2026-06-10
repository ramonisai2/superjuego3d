STAGE35 G - PROFESIONES HUMANAS

Objetivo:
- Crear al menos 8 profesiones humanas con colores y formas distintas.
- Mantener el sistema modular de cabeza, torso y pantalon.
- Reservar herramientas/armas boxel para una etapa posterior.

Profesiones agregadas:
- carpintero
- herrero
- granjero
- cazador
- minero
- mercader
- guardia
- curandero

Archivos de textura:
- player_skin_texture_atlas_humano_carpintero_joven.png
- player_skin_texture_atlas_humano_herrero.png
- player_skin_texture_atlas_humano_granjero.png
- player_skin_texture_atlas_humano_cazador.png
- player_skin_texture_atlas_humano_minero.png
- player_skin_texture_atlas_humano_mercader.png
- player_skin_texture_atlas_humano_guardia.png
- player_skin_texture_atlas_humano_curandero.png
- preview_profesiones_humanas_8.png

Cambios de sistema:
- HUMAN_PROFESSIONS define las profesiones humanas disponibles.
- HUMAN_PROFESSION_PROFILES define:
  - textura modular
  - color de acento
  - forma corporal
  - herramienta/arma reservada
- render_player_avatar acepta body_shape.
- Las herramientas/armas quedan guardadas en favorite_tool, pero no se dibujan aun.

Notas:
- Las herramientas/armas deben ser boxeles con lectura pixel-art.
- Por ahora estan reservadas para disenarlas con calma.
- No se hizo ZIP.
