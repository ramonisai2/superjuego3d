Stage40 W - PLAYABLE PLAINS LINEAR CLOUDS

Objetivo
- Mantener accidentes geograficos visibles sin que todo el mundo sea una pendiente.
- Crear llanuras jugables donde el jugador pueda caminar, pelear y construir sin atorarse.
- Corregir las esquinas claras del cielo y quitar el movimiento circular de las nubes.

Cambios
- biomes.py agrega plain_strength, un campo procedural de llanuras amplias y suaves.
- Las llanuras reducen detalle local y promedian altura solo en bolsas controladas.
- environment.py etiqueta esas zonas como "Llanura jugable" en el contexto de HUD.
- atmospheric_sky.py reemplaza el cielo de 4 caras por un cilindro/domo segmentado.
- Las nubes ahora son laminas altas con flujo lineal de viento: entran desde el horizonte, cruzan lento y se ocultan al otro lado.
- version_info.py sube la etapa visible a Stage40 W.

Variables utiles
- JUEGO_SKYBOX_SEGMENTS: suavidad del cielo segmentado. Default 24.
- JUEGO_CLOUD_WIND_SPEED: velocidad de paso de las nubes.
- JUEGO_CLOUD_WIND_ANGLE: direccion del viento de nubes.
- JUEGO_CLOUD_DENSITY: cantidad/alpha general de nubes.
- JUEGO_CLOUD_COUNT: numero base de nubes logicas.

Lectura
- Si el mundo se siente demasiado plano: bajar la fuerza de plain_strength en biomes.py.
- Si aun hay esquinas visibles en el cielo: subir JUEGO_SKYBOX_SEGMENTS a 32.
- Si las nubes distraen: bajar JUEGO_CLOUD_DENSITY o JUEGO_CLOUD_WIND_SPEED.
- Si el jugador se atora mucho: aumentar suavizado de llanuras antes de tocar colisiones.
