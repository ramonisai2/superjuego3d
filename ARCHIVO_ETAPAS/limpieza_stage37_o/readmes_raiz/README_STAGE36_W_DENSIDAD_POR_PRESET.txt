Stage36 W - DENSIDAD POR PRESET

Objetivo
- Hacer que el modo bajo genere chunks nuevos mas livianos.
- Conservar balanceado como experiencia normal.
- Permitir alto detalle con mas vida visual sin tocar codigo.

Cambios
- El generador de chunks lee JUEGO_GRAPHICS_PRESET.
- low reduce hierba, decoracion, rocas y arboles de oasis.
- balanced mantiene valores cercanos al estado actual.
- high permite mas densidad visual.
- Se agrega JUEGO_WORLD_DETAIL_PRESET para forzar solo la densidad del mundo.
- Se agregan overrides JUEGO_GRASS_DENSITY, JUEGO_DECO_DENSITY, JUEGO_ROCK_DENSITY y JUEGO_OASIS_TREE_DENSITY.

Notas
- Afecta chunks generados despues de iniciar el juego.
- No cambia la escala del mundo ni la recoleccion por celda.
- No elimina recursos existentes; solo reduce cuantas piezas nacen en chunks nuevos.
- No se genero ZIP.
