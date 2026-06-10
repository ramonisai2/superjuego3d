Stage36 U - HORIZONTE ADAPTATIVO

Objetivo
- Reducir carga de terreno visible cuando el FPS cae.
- Evitar regenerar o descargar chunks en caliente.
- Cubrir el recorte lejano con niebla mas cercana.

Cambios
- Se agrega JUEGO_ADAPTIVE_CHUNKS, activo por defecto.
- La distancia maxima de chunks dibujados baja segun la escala adaptativa.
- La niebla se acerca cuando el modo adaptativo entra en ahorro.
- F1 muestra distancia efectiva de chunks y fin de niebla.

Notas
- Los chunks siguen cargados; solo se dibujan menos si estan lejos.
- El radio cercano se conserva para evitar huecos al girar la camara.
- DEBUG_RENDER_ALL_CHUNKS ignora este recorte para depuracion.
- Se puede desactivar con JUEGO_ADAPTIVE_CHUNKS=0.
- No se genero ZIP.
