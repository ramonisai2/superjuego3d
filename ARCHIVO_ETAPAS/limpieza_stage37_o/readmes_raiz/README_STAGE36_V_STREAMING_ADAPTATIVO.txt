Stage36 V - STREAMING ADAPTATIVO

Objetivo
- Reducir trabajo de administracion de chunks cuando el FPS cae.
- Evitar que el streaming compita demasiado con movimiento y render.
- Mantener respuesta inmediata al cruzar a otro chunk.

Cambios
- Se agrega JUEGO_ADAPTIVE_STREAMING, activo por defecto.
- El intervalo de gestion de chunks sube de 50 ms a un valor mayor cuando la escala adaptativa baja.
- Al cruzar de chunk, la gestion se fuerza de inmediato para evitar huecos cercanos.
- El limite de LOD por tanda baja a 1 cuando el juego esta en ahorro.
- F1 muestra intervalo de streaming, limite LOD y si la actualizacion fue forzada.

Notas
- No descarga ni regenera mas terreno en caliente.
- No cambia el radio de chunks cargados.
- Se puede desactivar con JUEGO_ADAPTIVE_STREAMING=0.
- No se genero ZIP.
