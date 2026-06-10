Stage36 N - IA LEJANA POR TANDAS

Objetivo
- Reducir trabajo de NPCs y enemigos que estan lejos del jugador.
- Mantener respuesta inmediata en entidades cercanas, seleccionadas o fijadas.
- Evitar que el mapa vacio pierda FPS por actualizaciones invisibles.

Cambios
- NPCs cercanos actualizan cada frame.
- NPCs lejanos acumulan tiempo y actualizan por intervalos.
- Enemigos cercanos, seleccionados o fijados actualizan cada frame.
- Enemigos lejanos actualizan por tandas cortas.
- El Admin Hub conserva actualizacion completa cuando se usa para depurar.

Notas
- No cambia dano, rango, recetas, mochila ni render.
- No cambia escala boxel ni tamano de personajes.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
