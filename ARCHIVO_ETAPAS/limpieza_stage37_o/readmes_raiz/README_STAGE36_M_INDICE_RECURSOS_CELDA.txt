Stage36 M - INDICE DE RECURSOS POR CELDA

Objetivo
- Evitar recorrer listas completas de recursos en chunks cercanos.
- Mantener la recoleccion automatica igual para el jugador.
- Reducir trabajo repetido al consultar altura sobre rocas.

Cambios
- Piedra, madera y fibra se registran en celdas internas de 4 unidades.
- La recoleccion revisa solo las celdas cercanas al jugador.
- Las rocas que pueden elevar el suelo se registran en un indice de colision por celda.
- get_total_height() consulta solo la celda de roca cercana en lugar de escanear chunks vecinos completos.
- Al descargar un chunk se limpian sus recursos y rocas del indice.

Notas
- No cambia la escala del mundo ni el tamano del boxel.
- No cambia recetas, mochila, dano ni render.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
