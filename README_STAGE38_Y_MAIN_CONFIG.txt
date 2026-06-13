JUEGO 1.6 - Stage38 Y - MAIN CONFIG

Objetivo
- Empezar a partir main.py para que sea mas manejable con LLM local.
- Mover primero el bloque mas seguro: presets, constantes y lectura de variables JUEGO_*.
- Conservar los nombres que main.py ya usa para evitar cambios de comportamiento.

Cambios
- Nuevo archivo:
  juego3d_v1_5\main_config.py

- main.py ahora importa su configuracion desde main_config.py.
- main_config.py contiene:
  ANCHO / ALTO
  SEMILLA_MUNDO inicial
  GRAPHICS_PRESETS / GRAPHICS_SETTINGS
  radios de chunks y subdivisiones
  tuning adaptativo
  distancias de entidades
  tamanos de caches/celdas
  coordenadas de spawn

Notas
- Este es solo el primer corte.
- main.py sigue grande, pero ya perdio el bloque de configuracion.
- Siguiente corte recomendado: main_world_queries.py para altura, agua, celdas y recursos.
