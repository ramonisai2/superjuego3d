STAGE34 E - MOVIMIENTO MAS LIGERO

Objetivo:
- Reparar los cambios de prueba que afectaban la medicion real de FPS.
- Bajar costo de movimiento/contexto sin cambiar el terreno ni el avatar.

Cambios:
- DEBUG_RENDER_ALL_CHUNKS ahora queda apagado por defecto.
- Si se quiere forzar ese modo debug, usar JUEGO_DEBUG_RENDER_ALL_CHUNKS=1.
- DEBUG_RENDER_ALL_ENTITIES tambien queda controlado por JUEGO_DEBUG_RENDER_ALL_ENTITIES=1.
- Las consultas de agua usadas por altura/spawn ahora tienen cache espacial.
- El contexto de mundo/HUD/nado ya no se recalcula cada frame si el jugador casi no se movio.
- La lectura de altura cacheada ahora detecta si el mapa viene de LOD o detalle.

Motivo:
- El log de anoche mostraba FPS bajo incluso cuando render3d no era el mayor problema.
- player_move, world_context y ai estaban cargando demasiado por consultas repetidas.
- El modo debug de todos los chunks encendido podia ensuciar cualquier prueba de rendimiento.
- La cache de altura podia caer a calculo procedural si leia un LOD con resolucion distinta.

Siguiente prueba:
- Ejecutar LANZAR_OPENGL.bat para sensacion normal.
- Para medir, ejecutar LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat y luego ANALIZAR_PERF_MOVIMIENTO.bat.
- Comparar si bajan world_context, player_move y ai.

No se hizo ZIP.
