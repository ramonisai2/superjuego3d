JUEGO 1.6 - Stage40 M
QUICK STATUS UPDATE INFO

Objetivo
- Mostrar la etapa actual dentro de ESTADO_RAPIDO_JUEGO.bat.
- Evitar buscar manualmente version_info.py o los README para saber donde quedamos.
- Hacer que el estado rapido sea el tablero principal del proyecto.

Cambios
- ESTADO_RAPIDO_JUEGO.bat agrega la seccion ACTUALIZACION.
- La seccion lee motor_juegos\version_info.py y muestra:
  - stage
  - subtitle
  - description
- El resumen final tambien muestra la actualizacion actual.

Nota
- Usa el Python de previews porque ya puede importar modulos simples del proyecto.
- Si falta Python para previews, el estado rapido lo avisa sin fallar la estructura.
