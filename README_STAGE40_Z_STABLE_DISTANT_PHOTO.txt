Stage40 Z - STABLE DISTANT PHOTO

Objetivo
- Evitar que el fondo lejano parpadee cuando el jugador no se mueve.
- Mantener la idea de "fondo como fotografia" para horizonte e impostores.
- Reducir cambios bruscos del auto ahorro por pequenas oscilaciones de FPS.

Cambios
- main_adaptive_quality.py agrega histeresis al rescue_level.
- El rescate sube solo si el bajon se sostiene un momento.
- El rescate baja mucho mas lento para evitar baile visual.
- far_terrain_lod.py bloquea el conjunto de candidatos lejanos por centro de tile.
- forest_impostor_lod.py bloquea el conjunto de candidatos lejanos por centro de tile.
- La suavidad visual ya no forma parte de la clave principal del cache, evitando cache misses por cambio de rescate.

Lectura
- Si el jugador no cambia de zona/tile lejano, el fondo mantiene el mismo set visual.
- Si el FPS oscila cerca del limite, el HUD no deberia alternar RESC/OK a cada instante.
- El fondo puede cambiar al cruzar suficiente distancia, que es cuando corresponde refrescar la "foto".
