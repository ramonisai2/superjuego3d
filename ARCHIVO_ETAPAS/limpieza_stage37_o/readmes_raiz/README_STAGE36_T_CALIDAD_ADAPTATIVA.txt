Stage36 T - CALIDAD ADAPTATIVA

Objetivo
- Suavizar bajones de FPS sin cambiar de render principal.
- Reducir detalle lejano solo cuando el juego lo necesite.
- Mantener OpenGL estable como ruta jugable.

Cambios
- Se agrega JUEGO_ADAPTIVE_QUALITY, activo por defecto.
- El juego calcula un promedio suave de FPS.
- Si el promedio baja, reduce distancia de entidades, etiquetas y restos.
- Si el promedio se recupera, sube la calidad poco a poco.
- El HUD muestra Auto OK/AHORR/RECUP junto al contador FPS.
- F1 muestra escala adaptativa y FPS promedio.

Notas
- No cambia el tamano de chunks ni regenera terreno en caliente.
- No afecta entidades fijadas con Z target ni NPCs destacados.
- Se puede desactivar con JUEGO_ADAPTIVE_QUALITY=0.
- Vulkan sigue como laboratorio, no como ruta principal.
- No se genero ZIP.
