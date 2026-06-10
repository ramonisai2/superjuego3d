Stage37 E - SESIONES DE PRESET

Objetivo
- Evitar mezclar pruebas viejas con pruebas nuevas.
- Marcar cada arranque del juego con una sesion.
- Poder limpiar el log antes de comparar presets.

Cambios
- Cada muestra de preset incluye session.
- Al iniciar partida se escribe event=session_start.
- El analizador ignora session_start como muestra de FPS.
- El analizador reporta cantidad de sesiones y ultima sesion.
- Se agrega LIMPIAR_LOG_PRESETS_GRAFICOS.bat.

Notas
- No cambia gameplay ni render.
- Para comparar limpio: limpiar log, jugar low, balanced y high unos segundos, luego analizar.
- No se genero ZIP.
