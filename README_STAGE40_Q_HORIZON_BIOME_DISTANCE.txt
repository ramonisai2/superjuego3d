JUEGO 1.6 - Stage40 Q
HORIZON BIOME DISTANCE

Objetivo
- Aumentar la distancia de dibujado en 1 chunk.
- Hundir un poco el horizonte lejano para que el mundo no parezca una mesa infinita.
- Tinte leve de cielo/fog por bioma distante para localizar desiertos y pantanos.

Cambios
- main_config.py sube radio_vision de cada preset en 1.
- far_terrain_lod.py aplica JUEGO_FAR_TERRAIN_HORIZON_SINK al relieve lejano por anillo.
- atmospheric_sky.py muestrea el bioma delante de la camara y mezcla un tinte suave.
- main_render3d.py actualiza el contexto de bioma antes de dibujar cielo/fog.

Variables utiles
- JUEGO_FAR_TERRAIN_HORIZON_SINK=1.15
- JUEGO_BIOME_SKY_TINT_ENABLED=1
- JUEGO_BIOME_SKY_SAMPLE_DISTANCE=260
- JUEGO_BIOME_SKY_TINT_STRENGTH=1.0

Notas
- OpenGL estable sigue siendo el camino jugable.
- Si bajan los FPS, probar primero LOW o bajar JUEGO_RADIO_VISION manualmente.
