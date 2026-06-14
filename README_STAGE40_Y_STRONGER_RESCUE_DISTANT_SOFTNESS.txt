Stage40 Y - STRONGER RESCUE DISTANT SOFTNESS

Objetivo
- Hacer que el auto ahorro inteligente se note mas.
- Simular un blur lejano barato sin postproceso caro.
- Aflojar un poco la niebla sin subir distancia real de render.

Cambios
- JUEGO_FRAME_RESCUE_FPS sube por defecto de 30 a 34.
- JUEGO_FRAME_EMERGENCY_FPS sube por defecto de 22 a 24.
- El rescate suave ahora recorta mas horizonte/bosque lejano y pausa construccion nueva de parches lejanos.
- El rescate fuerte/critico recorta con mas claridad max_visible/radio y pausa LOD nuevo.
- far_terrain_lod.py agrega JUEGO_FAR_TERRAIN_SOFTNESS para lavar contraste/color por distancia.
- forest_impostor_lod.py agrega JUEGO_FOREST_IMPOSTOR_SOFTNESS para suavizar bosques lejanos.
- main_adaptive_quality.py retrasa el inicio de fog y aleja un poco su final visual sin cambiar la distancia de chunks.

Variables utiles
- JUEGO_FRAME_RESCUE_FPS: umbral de rescate fuerte. Default 34.
- JUEGO_FRAME_EMERGENCY_FPS: umbral critico. Default 24.
- JUEGO_FAR_TERRAIN_SOFTNESS: suavizado visual de parches lejanos.
- JUEGO_FOREST_IMPOSTOR_SOFTNESS: suavizado visual de bosques lejanos.
- JUEGO_ADAPTIVE_FPS_HIGH: FPS donde recupera calidad. Default 48.

Lectura
- No es blur real de framebuffer; es suavizado artistico por distancia.
- Se conserva la distancia de render de chunks.
- Si se ve demasiado lavado, bajar SOFTNESS.
- Si aun no se nota rescate, subir JUEGO_FRAME_RESCUE_FPS a 38.
