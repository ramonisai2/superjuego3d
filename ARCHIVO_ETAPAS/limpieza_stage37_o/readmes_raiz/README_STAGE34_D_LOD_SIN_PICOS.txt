STAGE34 D - LOD SIN PICOS

Objetivo:
- Reducir tirones al cruzar fronteras de chunk.
- Evitar que varios chunks simples/LOD se creen de golpe en el hilo principal.
- Mantener OpenGL estable como modo jugable y current como terreno default.

Cambios:
- Se agrego una cola para chunks LOD simples.
- El gestor de chunks ahora encola LOD faltantes en vez de crearlos todos al instante.
- Por defecto se crean 2 LOD por tanda: JUEGO_LOD_CREAR_POR_TANDA=2.
- La ruta normal y la ruta stream bridge segura usan la misma cola.
- El HUD/perf puede mostrar chunk_lod cuando JUEGO_PERF_LOG o JUEGO_PERF_HUD estan activos.
- ANALIZAR_PERF_MOVIMIENTO.bat ahora separa lod= y compile=.

Motivo:
- La generacion current ya bajo mucho en Stage34 C.
- El siguiente sospechoso eran picos por crear/subir varios LOD simples mientras el jugador se mueve.

Decision:
- OpenGL estable sigue siendo el camino jugable.
- Vulkan sigue como laboratorio, no como solucion principal a los tirones actuales.
- No se cambio el metodo de terreno default.

Siguiente prueba:
- Ejecutar LANZAR_OPENGL.bat y caminar cruzando chunks.
- Si aun hay bajones, ejecutar el log de movimiento y revisar chunk_lod, chunk_compile y render3d.

No se hizo ZIP.
