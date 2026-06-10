STAGE 28 FIX H - LOG PARA CICLO DE REAPARICION

Objetivo:
- Encontrar el culpable del ciclo de reaparicion del personaje.

Archivo de log:
- Se crea automaticamente como: respawn_debug.log
- Queda en la carpeta desde donde se ejecuta el juego. Si usas el lanzador:
  JUEGO 1.6/juego3d_v1_5/respawn_debug.log

Eventos importantes que registra:
- GAME_START: modo de arranque, semilla, si hay save.
- LOAD_SAVE_RAW: coordenadas crudas del guardado.
- LOAD_SAVE_APPLIED: coordenadas aplicadas al jugador.
- SAFE_SEARCH_START: inicio de busqueda de posicion segura.
- SAFE_BASE_CHECK: revisa si la posicion inicial esta en agua/altura valida.
- SAFE_CANDIDATE_REJECT_WATER: candidato rechazado por agua.
- SAFE_CANDIDATE_REJECT_HEIGHT: candidato rechazado por altura rara.
- SAFE_CANDIDATE_ACCEPTED: posicion segura encontrada.
- RESPAWN_POINT_SET: punto de respawn actualizado.
- DAMAGE / DEATH_TRIGGER: dano y muerte del jugador.
- RESPAWN_START / RESPAWN_DONE: respawn por muerte.
- VERTICAL_OUT_OF_BOUNDS: el jugador cayo al vacio o subio a altura rara.
- VERTICAL_RESET_DONE: reset por altura rara.
- HEIGHT_WATER_SURFACE_USED: el agua se uso como suelo.
- TERRAIN_HEIGHT_WEIRD: altura del terreno sospechosa.

Posible culpable detectado:
- En versiones anteriores, Player.respawn() mandaba siempre a (0,0), ignorando respawn_x/respawn_z.
- Tambien FirstPersonCamera.process_keyboard() mandaba a (0,0) si pos_y < -10 o pos_y > 200.
- Esta build registra ambos casos y evita que el reset silencioso vuelva siempre al origen.

Como probar:
1) Ejecuta el juego con JUEGO 1.6/LANZADOR_RAPIDO.bat
2) Provoca el bug o carga la partida donde aparece el ciclo.
3) Cierra el juego.
4) Abre respawn_debug.log y busca:
   - VERTICAL_OUT_OF_BOUNDS repetido
   - RESPAWN_START repetido
   - SAFE_SEARCH_FALLBACK_ORIGIN
   - HEIGHT_WATER_SURFACE_USED cerca del spawn
5) Pasa ese log para revisar el culpable exacto.
