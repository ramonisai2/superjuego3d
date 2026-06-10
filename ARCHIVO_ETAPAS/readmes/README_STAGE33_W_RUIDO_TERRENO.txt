STAGE33 W - RUIDO TERRENO

Objetivo:
- Probar si un ruido economico tipo Perlin/value-noise puede abaratar elevaciones.
- No reemplazar el terreno actual todavia.
- Comparar costo y sensacion visual.

Archivos nuevos:
- PROBAR_RUIDO_TERRENO.bat
- LANZAR_OPENGL_FAST_NOISE.bat

Uso:
1. Ejecuta PROBAR_RUIDO_TERRENO.bat para ver benchmark actual vs fast_noise.
2. Ejecuta LANZAR_OPENGL_FAST_NOISE.bat para ver el mundo con elevacion economica.
3. Compara contra LANZAR_OPENGL.bat.

Notas:
- El metodo actual sigue siendo el default.
- fast_noise se activa solo con JUEGO_TERRAIN_MODE=fast_noise.
- En la prueba inicial: actual ~49.23 ms, fast_noise ~6.55 ms, ventaja x7.52.
- El modo fast_noise muestra una etiqueta "Terreno: FAST_NOISE" en pantalla.
- Si se ve bien y mejora, la siguiente etapa seria hacer un hibrido:
  ruido barato para altura base + tus lagos/mesetas/biomas para identidad.

No se hizo ZIP.
