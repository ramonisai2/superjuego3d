Stage40 S - HORIZON PERF TELEMETRY

Objetivo
- Medir si el horizonte lejano sigue afectando FPS al moverse.
- Separar el costo de chunks vivos, LOD normal, uploads y parches distantes.
- Dar senales claras para ajustar sin adivinar.

Cambios
- El HUD debug muestra FarHorizon:
  - tiles visibles
  - parches construidos en el frame
  - parches cacheados
  - tamano de parche
  - subdivisiones
  - bioma distante usado por el cielo
- El log de presets agrega:
  - farTiles
  - farBuilt
  - farCache
  - farTile
  - farSub
  - farMax
  - skyHint
- El analizador de presets resume farT/farB y puede avisar si las peores caidas coinciden con construccion de horizonte lejano.

Lectura rapida
- farTiles alto con farBuilt 0 suele ser costo de dibujado estable.
- farTiles alto con farBuilt 1 durante caidas apunta a construccion de parches lejanos.
- uploads alto apunta mas a chunks/mallas que al horizonte lejano.
- visibleV/lodV alto apunta a geometria visible normal.

Tuning posible
- JUEGO_FAR_TERRAIN_MAX_VISIBLE baja cuantos parches se dibujan.
- JUEGO_FAR_TERRAIN_BUILD_PER_FRAME baja cuantos parches nuevos se construyen por frame.
- JUEGO_FAR_TERRAIN_SUBDIVISIONS baja detalle interno de cada parche.
