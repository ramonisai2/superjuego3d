JUEGO 1.6 - STAGE 28: LAGOS ORGANICOS / AGUA INTERIOR

Objetivo de esta build:
- Probar una direccion visual del mundo con 80% tierra y 20% agua interior aproximada.
- No se agrega mar ni oceano.
- El agua aparece como lagos organicos cerrados, humedales y algunos lagos enormes.
- Algunos lagos enormes pueden tener brazos estrechos tipo rios interiores.
- Hay lagos a diferentes alturas: bajos, de valle, de meseta y de montana.

Cambios tecnicos:
- motor_juegos/biomes.py
  - Agregada calculate_water_properties().
  - Agregado get_water_color().
  - El agua no usa un nivel global de mar; se genera con terrazas locales de altura.

- motor_juegos/environment.py
  - Los chunks ahora generan water_data ademas de terreno, pasto, rocas y decoraciones.
  - Se dibuja una superficie transparente para lagos.
  - Se oscurece el fondo bajo el agua.
  - Se agregan orillas humedas/barrosas.
  - Restauradas funciones auxiliares importantes si faltaban en el source:
    get_terrain_height_at(), get_cached_height_at(), get_water_surface_at() y draw_procedural_skybox().

- main.py
  - Titulo de ventana actualizado a Stage 28.
  - El jugador/NPCs usan la superficie del lago como suelo temporal de prueba para evitar caminar bajo el agua.

Limitaciones conocidas:
- Todavia no hay natacion.
- Todavia no hay fisica real de agua.
- Algunas zonas pueden parecer lagos extremadamente grandes; eso es intencional para probar superlagos, pero se puede ajustar.
- Los rios son brazos visuales simples, no una simulacion hidrologica real.

Como probar:
1. Abrir terminal en la carpeta juego3d_v1_5.
2. Instalar dependencias si hace falta:
   pip install pygame PyOpenGL numpy
3. Ejecutar:
   python main.py

Que observar:
- Si el mundo se siente mas terrestre y natural, sin costa marina.
- Si los lagos organicos se ven interesantes o demasiado abundantes.
- Si los superlagos parecen regiones memorables o si parecen oceano por accidente.
- Si las orillas y pantanos ayudan a la identidad visual.


STAGE 28 FIX A - LAGOS MENOS BUGGEADOS
- Correccion visual: el agua ya no intenta cubrir zonas enormes como una sola sabana plana.
- Las celdas de agua se aceptan solo si pertenecen a una terraza coherente.
- El fondo bajo el lago ahora se hunde visualmente y usa color cafe/verdoso/turbio.
- La transparencia del agua bajó para poder leer mejor el fondo.
- Se mantuvo la regla: sin mar, lagos interiores, tierra dominante.
- Todavia es un prototipo: no hay simulacion real de rios, solo brazos organicos conectados a cuencas.
