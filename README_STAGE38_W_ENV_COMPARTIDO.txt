JUEGO 1.6 - Stage38 W - ENV COMPARTIDO

Objetivo
- Continuar la limpieza de valores y reglas repetidas.
- Centralizar la lectura de variables de entorno usadas por presets, detalle y streaming.
- Evitar que cada modulo tenga su propia conversion int/float/bool con fallbacks distintos.

Cambios
- Nuevo modulo:
  juego3d_v1_5\motor_juegos\env_config.py

- Helpers comunes:
  read_env_text
  read_env_bool
  read_env_int
  read_env_float

- Modulos conectados:
  main.py
  motor_juegos\environment.py
  motor_juegos\stream_bridge_budget.py

Criterio
- Los valores artisticos locales se quedan locales.
- Los valores de tuning que vienen del entorno se leen con la misma regla.
- Si una variable esta vacia o mal escrita, vuelve al default sin romper el juego.
