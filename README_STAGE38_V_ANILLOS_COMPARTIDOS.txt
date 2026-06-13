JUEGO 1.6 - Stage38 V - ANILLOS COMPARTIDOS

Objetivo
- Continuar la limpieza de valores reciclables sin tocar valores artisticos locales.
- Sacar el margen repetido de culling de anillos de chunks a una utilidad comun.
- Mantener OpenGL estable como ruta jugable y Vulkan como infraestructura experimental.

Cambios
- Nuevo modulo:
  juego3d_v1_5\motor_juegos\chunk_math.py

- Constante compartida:
  CHUNK_RING_CULL_MARGIN = 0.35

- Funciones compartidas:
  chunk_coord
  generate_square_chunk_ring
  passes_chunk_ring_cull
  generate_visible_chunk_ring

- Pruebas actualizadas para usar la misma matematica:
  vulkan_multi_chunk_probe.py
  vulkan_player_chunk_ring_probe.py
  vulkan_chunk_streaming_probe.py

Criterio
- Reciclar valores por significado, no por coincidencia.
- El margen 0.35 define el mismo concepto en varias pruebas: no cortar diagonales utiles del anillo de chunks.
- Colores, coordenadas de modelos y detalles artisticos se quedan locales mientras no exista una razon clara para compartirlos.
