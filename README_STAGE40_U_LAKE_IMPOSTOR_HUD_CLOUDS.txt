Stage40 U - LAKE IMPOSTOR HUD CLOUDS

Objetivo
- Hacer que el lago se vea mas bonito aunque la malla procedural siga siendo simple.
- Bajar mas la presencia negra del HUD.
- Confirmar y reforzar las nubes atmosfericas.

Cambios
- Los paneles del HUD son mas transparentes.
- El agua base baja su alpha para mostrar menos cuadricula.
- Cuando hay suficiente agua profunda en un chunk se agrega una lamina impostora:
  - no cambia colision ni logica de agua.
  - ayuda a leer el conjunto como lago.
  - tapa parte del patron de baldosas.
- Las nubes ya existian en atmospheric_sky.py, pero eran muy sutiles.
- Ahora las nubes tienen mas densidad, tamano y alpha por defecto.

Variables utiles
- JUEGO_WATER_IMPOSTOR_MIN_DEPTH: profundidad minima para contar como lago visual.
- JUEGO_WATER_IMPOSTOR_MIN_CELLS: cantidad minima de celdas profundas.
- JUEGO_WATER_IMPOSTOR_MIN_FILL: evita cubrir demasiada tierra si el agua esta dispersa.
- JUEGO_WATER_IMPOSTOR_ALPHA: opacidad de la lamina impostora.
- JUEGO_WATER_ALPHA: opacidad de la malla base de agua.
- JUEGO_CLOUD_DENSITY: densidad de nubes.
- JUEGO_CLOUD_COUNT: cantidad base de nubes.

Nota
- Esta etapa no intenta resolver toda la identidad del agua.
- El siguiente frente sigue siendo diferenciar lago, rio, charco y escorrentia con reglas visuales propias.
