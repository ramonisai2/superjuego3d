Stage36 L - LOGICA BARATA POR CELDAS

Objetivo
- Reducir calculos caros mientras el jugador se mueve.
- Mantener el comportamiento visual y jugable igual.
- Preparar el camino para logica por celdas/chunks sin cambiar el render.

Cambios
- La recoleccion compara distancia al cuadrado para piedra, madera y fibra.
- El Z Target filtra primero por distancia al cuadrado y solo calcula angulo si el objetivo puede entrar.
- La seleccion cercana de enemigos y la interaccion con NPCs evitan raiz cuadrada.
- El combate filtra rango de golpe con distancia al cuadrado.
- Los slimes evitan calcular distancia real cuando el jugador esta fuera de aggro.

Notas
- No cambia el tamano del boxel ni la escala del mundo.
- No cambia recetas, mochila ni dano de armas.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
