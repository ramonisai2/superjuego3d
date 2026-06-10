STAGE 30 FIX U - SKIN LIMPIA DEL PERSONAJE

Problema corregido:
- La primera versión usaba directamente la imagen completa del atlas con etiquetas, bordes y guías.
- Eso hacía que el personaje pareciera tener la plantilla pegada al cuerpo.

Cambios:
- Se creó una nueva textura limpia: juego3d_v1_5/player_skin_texture_atlas.png
- Ya no tiene letras, bordes ni guías visibles.
- Se reajustaron los rectángulos UV en game/voxel_models.py.
- El personaje mantiene animación básica de caminata y nado.
- Si la textura no carga, el modelo vuelve al render voxel de colores como respaldo.

Notas:
- Esta es una primera skin limpia; todavía puede requerir ajustes de orientación de algunas caras.
- Si algún lado se ve volteado, se corrige cambiando el orden UV de esa cara.
