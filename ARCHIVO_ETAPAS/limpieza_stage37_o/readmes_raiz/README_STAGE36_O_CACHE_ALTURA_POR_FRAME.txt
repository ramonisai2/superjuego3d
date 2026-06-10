Stage36 O - CACHE DE ALTURA POR FRAME

Objetivo
- Reducir consultas repetidas de altura mientras el jugador se mueve.
- Mantener la fisica y la escala del mundo sin cambios visibles.
- Evitar recalcular terreno/agua/rocas varias veces en posiciones casi iguales dentro del mismo frame.

Cambios
- get_total_height() usa un cache fino de 0.25 unidades.
- El cache se limpia al inicio de cada update.
- El cache tambien se limpia cuando se cargan o descargan rocas de chunks.
- Movimiento, NPCs y enemigos pueden reutilizar altura total durante el mismo frame.

Notas
- No cambia el tamano del boxel.
- No cambia recetas, mochila, dano, IA cercana ni render.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
