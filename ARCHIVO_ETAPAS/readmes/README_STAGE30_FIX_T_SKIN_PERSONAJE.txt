STAGE 30 FIX T - SKIN DEL PERSONAJE

Cambios principales:
- El jugador en tercera persona ahora intenta usar la skin bitmap generada.
- Se añadió el archivo player_skin_texture_atlas.png dentro de juego3d_v1_5.
- El render del jugador usa textura por cara (cabeza, torso, brazos y piernas).
- Si por alguna razón la textura no carga, el juego vuelve al modelo voxel de colores como respaldo.
- Se conservan animación básica de caminar y pose de nado.

Notas:
- La skin está calibrada para la plantilla atlas generada en esta conversación.
- Si más adelante se cambia la skin por otra plantilla distinta, habrá que reajustar los rectángulos UV en game/voxel_models.py.
