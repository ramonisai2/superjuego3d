Stage40 T - WATER HUD POLISH

Objetivo
- Poner mejora de agua en la ruta de desarrollo visual.
- Reducir el peso visual de los paneles negros del HUD.
- Evitar que los lagos profundos parezcan agua corriendo por una pendiente.

Cambios
- renderer2d.py agrega draw_rounded_rect_2d().
- game/ui.py usa paneles redondeados y semitransparentes.
- environment.py distingue agua somera de agua profunda:
  - escorrentia/charcos siguen pegados al terreno.
  - lagos profundos pueden recuperar una superficie mas plana.
- El solape entre celdas de agua baja mucho para que no se marque tanto la cuadricula.
- El alpha del agua baja por defecto de 0.34 a 0.28.

Variables utiles
- JUEGO_WATER_LAKE_FLAT_DEPTH: profundidad desde la que un lago empieza a verse mas plano.
- JUEGO_WATER_LAKE_MAX_ABOVE_GROUND: limite visual sobre el suelo para lagos profundos.
- JUEGO_WATER_CELL_OVERLAP: solape entre celdas de agua.
- JUEGO_WATER_ALPHA: transparencia visual del agua.

Timeline dev de agua
- Separar visualmente lago, rio, charco y escorrentia.
- Agregar orilla mas clara y espuma/linea muy sutil solo donde el agua toca suelo.
- Dar reflejo barato segun cielo/hora.
- Reducir patron de cuadricula sin perder compatibilidad con chunks.
- Hacer que el HUD muestre tipo de agua en debug si hace falta.
