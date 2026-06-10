STAGE 28 FIX I - CORRECCION DE CAIDA/REAPARICION DEL PERSONAJE

Culpable encontrado en respawn_debug.log:
- VERTICAL_OUT_OF_BOUNDS mostraba old_y muy negativo (-43, -63, -81).
- El jugador no moria: caia por debajo del terreno y el sistema vertical lo mandaba al origen.

Cambios:
1) La fisica vertical ahora pega al jugador directamente al suelo si los pies cruzan el terreno.
   Antes intentaba subirlo suavemente; mientras tanto seguia cayendo y activaba el reset.
2) La gravedad ya no se aplica cuando el jugador esta en el suelo.
3) Se guarda un ultimo punto seguro real (_last_safe_x/y/z).
4) Si vuelve a pasar VERTICAL_OUT_OF_BOUNDS, el jugador vuelve al ultimo punto seguro,
   no necesariamente a (0,0).
5) Player.respawn() ya no usa siempre (0,0); usa respawn_x/respawn_z.
6) El log sigue activo para confirmar si el bug queda corregido.

Que revisar:
- Caminar y correr varios segundos sin que el personaje parezca reaparecer/cayendo.
- Si vuelve a pasar, revisar respawn_debug.log buscando:
  VERTICAL_OUT_OF_BOUNDS, GROUND_SNAP_LARGE, TERRAIN_HEIGHT_WEIRD.
