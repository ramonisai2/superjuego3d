STAGE 31 PRE-C - CHUNKS REDUCIDOS + 9 ADYACENTES

Cambios principales:
- El jugador nuevo ya no aparece en la esquina del chunk 0,0.
- En nueva partida aparece cerca del centro del chunk inicial:
  X = CHUNK_SIZE / 2, Z = CHUNK_SIZE / 2.
- Se mantiene CHUNK_SIZE reducido a 64.
- Ahora se generan/renderizan con detalle los 9 chunks cercanos:
  chunk actual + 8 adyacentes.
- El radio visible mantiene LOD simple alrededor.
- Se quitó un poco la agresividad:
  RADIO_DETALLE = 1
  MAX_COLA_PETICIONES = 3
  CHUNKS_COMPILAR_POR_FRAME = 2
  SUBDIVISIONES_LOD = 10

Qué revisar:
- Si apareces más centrado y no justo en una costura/esquina de chunk.
- Si al iniciar ya hay más mundo detallado alrededor.
- Si la carga sigue aceptable.
- Si el popping mejora sin volver demasiado pesado el rendimiento.
