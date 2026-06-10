Stage37 P - AGUA A RAS

Objetivo:
- Corregir agua que se veia demasiado alta sobre el suelo.
- Mantener la lamina de agua pegada al terreno local.
- Aplicar el ajuste tambien a consultas de jugador/NPC y LOD.

Resultado:
- Se agrega _water_surface_y() en environment.py.
- El agua detallada usa la altura del terreno visual de la celda.
- El agua LOD usa el mismo ajuste.
- get_water_surface_at() devuelve el nivel ajustado al suelo cacheado.
- get_world_context_at() reporta profundidad visual coherente.
- main.py pasa CHUNK_SIZE/SUBDIVISIONES reales a las consultas de agua.

Nota:
- El margen por defecto es 0.018 sobre el suelo para evitar parpadeo/z-fighting.
- Se puede ajustar con JUEGO_WATER_SURFACE_MAX_ABOVE_GROUND.
- No se toca Vulkan.
- No se crea ZIP.
