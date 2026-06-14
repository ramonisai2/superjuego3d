Stage41 A - DISTANT IMPOSTOR RING WORLD TINT

Objetivo
- Evitar que los impostores de arbol aparezcan cerca como fantasmas flotantes.
- Empujar el telon lejano mas lejos del jugador.
- Hacer que el ciclo dia/noche afecte el color del mundo, no solo el cielo.

Cambios
- forest_impostor_lod.py aumenta tile_size default a 160.
- forest_impostor_lod.py aumenta inner_radius default a 2.
- forest_impostor_lod.py agrega JUEGO_FOREST_IMPOSTOR_MIN_DISTANCE.
- far_terrain_lod.py aumenta radio default a 5 e inner_radius default a 2.
- main_render3d.py calcula un tinte atmosferico global desde SkyProfile.
- gl_legacy_bridge.py dibuja una capa 2D barata sobre el 3D antes del HUD:
  - noche: azul oscuro
  - amanecer/atardecer: rojizo/calido
- main_hud_render.py muestra tintStrength/tintWorld en F1.
- main_preset_logging.py guarda skyWorldTint.

Variables utiles
- JUEGO_FOREST_IMPOSTOR_MIN_DISTANCE: distancia minima de impostores de bosque. Default 260.
- JUEGO_FOREST_IMPOSTOR_TILE_SIZE: tamano de tile lejano. Default 160.
- JUEGO_FOREST_IMPOSTOR_INNER_RADIUS: anillo muerto alrededor del jugador. Default 2.
- JUEGO_FAR_TERRAIN_RADIUS: radio de parches lejanos. Default 5.
- JUEGO_FAR_TERRAIN_INNER_RADIUS: anillo muerto de parches lejanos. Default 2.

Lectura
- Los impostores quedan reservados para distancia media/lejana.
- La escena 3D se oscurece/tine despues de dibujar mundo y arma, antes del HUD.
- No cambia materiales ni chunks; es un efecto barato de pantalla.
