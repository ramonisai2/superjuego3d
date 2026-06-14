Stage40 V - STRONGER HORIZON PATCHES

Objetivo
- Hacer que los parches baratos de horizonte se noten mas.
- Evitar que el horizonte vuelva a sentirse como una linea plana.
- No subir chunks reales ni aumentar fuerte la carga de CPU.

Cambios
- far_terrain_lod.py usa por defecto:
  - radio visual 4
  - 5 subdivisiones por parche
  - max_visible 64
  - cache 80
  - hundimiento menor
  - menos haze interno
  - escala vertical 1.75
- El HUD debug muestra radio y escala de altura del horizonte.
- El log de presets guarda farRadius y farScale.

Variables utiles
- JUEGO_FAR_TERRAIN_HEIGHT_SCALE: fuerza vertical del relieve lejano.
- JUEGO_FAR_TERRAIN_VERTICAL_LIFT: levanta o baja el bloque visual lejano.
- JUEGO_FAR_TERRAIN_HORIZON_SINK: hundimiento por anillo.
- JUEGO_FAR_TERRAIN_HAZE: cuanto se lava el color del parche.
- JUEGO_FAR_TERRAIN_RADIUS: cuantos anillos lejanos dibuja.
- JUEGO_FAR_TERRAIN_MAX_VISIBLE: limite de parches visibles.

Lectura
- Si el horizonte se ve plano: subir HEIGHT_SCALE o bajar HAZE.
- Si se ve como pared alta: bajar HEIGHT_SCALE o VERTICAL_LIFT.
- Si baja FPS: bajar MAX_VISIBLE antes que RADIO_VISION.
