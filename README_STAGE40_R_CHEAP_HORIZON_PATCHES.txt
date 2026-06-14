Stage40 R - CHEAP HORIZON PATCHES

Objetivo
- Responder al bajon de FPS visto al subir la distancia de dibujado real.
- Mantener horizonte y biomas lejanos, pero sin obligar al juego a cargar mas chunks vivos.
- Cambiar las baldosas lejanas finas por parches grandes y baratos.

Cambios
- Los presets vuelven a radios estables de chunks:
  - low: 2
  - balanced: 2
  - high: 3
- far_terrain_lod.py ahora usa por defecto parches de 384 unidades con 4 subdivisiones.
- El horizonte lejano construye solo 1 parche nuevo por frame.
- El cache lejano baja a 48 parches por defecto.
- Se limita la cantidad visible de parches lejanos a 40 por defecto.
- El tinte de cielo/fog por bioma distante ya no recalcula cada frame: se muestrea cada 0.75 s, o antes si el jugador se mueve/mira lo suficiente.

Notas de tuning
- JUEGO_FAR_TERRAIN_TILE_SIZE permite agrandar o reducir el parche lejano.
- JUEGO_FAR_TERRAIN_SUBDIVISIONS controla cuanto detalle tiene cada parche.
- JUEGO_FAR_TERRAIN_MAX_VISIBLE limita cuantas piezas de horizonte se dibujan.
- JUEGO_BIOME_SKY_SAMPLE_INTERVAL controla cada cuanto se actualiza el tinte por bioma.

Lectura
- La distancia jugable real vuelve a ser conservadora.
- La distancia visual se simula con muestras grandes del terreno real.
- Esto debe dar mas horizonte por menos CPU que subir el radio de chunks.
