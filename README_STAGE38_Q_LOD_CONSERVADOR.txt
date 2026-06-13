JUEGO 1.6 - Stage38 Q - LOD CONSERVADOR

Objetivo:
- Reducir los bajones que aparecen al moverse cuando hay muchos chunks LOD visibles.
- Mantener OpenGL estable como ruta jugable.
- Medir la distancia real de chunks en los logs de presets.

Cambios:
- Cada preset ahora tiene su propia distancia extra para chunks lejanos:
  - low: 1.10 chunks extra.
  - balanced: 1.35 chunks extra.
  - high: 1.65 chunks extra.
- Antes todos usaban 1.80 chunks extra.
- El log de presets agrega:
  - chunkDist: distancia real usada para dibujar chunks.
  - chunkExtra: extra configurado por preset.
- El reporte de presets muestra chunkDist y extra en el resumen y en las peores muestras.

Override manual:
- Para probar sin editar codigo:
  set JUEGO_CHUNK_RENDER_EXTRA=1.80
  set JUEGO_CHUNK_RENDER_MIN_EXTRA=1.35

Lectura esperada:
- Si suben los FPS al moverse, el cuello estaba en render/LOD visible.
- Si siguen las caidas con pocos chunks y pocos vertices, el siguiente frente es CPU/logica/movimiento.
- Si aparecen huecos o popping feo, subir un poco JUEGO_CHUNK_RENDER_EXTRA.

Regla:
- No cambia Vulkan.
- No hace ZIP.
- No cambia el metodo de terreno default.
