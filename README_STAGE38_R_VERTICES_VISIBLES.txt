JUEGO 1.6 - Stage38 R - VERTICES VISIBLES

Objetivo:
- Medir la carga real que se dibuja en cada frame.
- Separar vertices visibles de detalle y vertices visibles de LOD.
- Evitar decidir optimizaciones solo con el ultimo mesh subido.

Cambios:
- Los chunks LOD simples ahora se devuelven como NeutralMeshHandle con:
  - vertex_count estimado.
  - index_count estimado.
  - byte_size estimado.
  - metadata de quads de terreno/agua.
- RenderFrameGraph suma por frame:
  - visible_chunk_vertices
  - visible_detail_vertices
  - visible_lod_vertices
  - visible_chunk_bytes
  - visible_chunk_batches
- El log de presets agrega:
  - visibleVerts
  - visibleDetailVerts
  - visibleLODVerts
  - visibleKB
- El reporte de presets muestra visibleV y lodV.

Lectura:
- verts = ultimo mesh subido recientemente.
- visibleVerts = vertices de chunks visibles en el frame.
- visibleLODVerts alto con FPS bajo apunta a LOD/horizonte.
- visibleDetailVerts alto con FPS bajo apunta a chunks cercanos o detalle de mundo.

Regla:
- No cambia gameplay.
- No cambia Vulkan como modo principal.
- No hace ZIP.
