JUEGO 1.6 - Stage39 B - MAIN SCREENS

Objetivo
- Continuar reduciendo main.py por responsabilidad.
- Sacar pantallas simples de menu y carga a un modulo propio.
- Hacer que el modulo nuevo reciba engine/render_backend/r2d/ancho/alto de forma explicita.

Cambios
- Nuevo archivo:
  juego3d_v1_5\main_screens.py

- Movido desde main.py:
  draw_simple_screen
  show_loading_screen
  show_start_menu

- Limpieza:
  main.py ya no importa get_render_mode_status, get_save_summary ni UPDATE_CODENAME/UPDATE_SUBTITLE.

Resultado
- main.py queda mas enfocado en loop, mundo y render.
- El siguiente corte recomendado: main_world_queries.py o main_chunk_streaming.py.
