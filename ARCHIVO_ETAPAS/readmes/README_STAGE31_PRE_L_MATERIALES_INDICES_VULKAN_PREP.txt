STAGE 31 PRE-L - MATERIALES + INDICES PARA VULKAN PREP

Objetivo:
- Continuar la migracion hacia Vulkan sin romper el backend OpenGL actual.
- Ordenar las mallas por material y preparar datos mas cercanos a vertex/index buffers.

Cambios principales:
1) Nuevo archivo:
   motor_juegos/materials.py

   Define materiales neutrales:
   - terrain
   - rock
   - tree_trunk
   - tree_leaf
   - plant
   - water
   - shadow
   - default

2) MeshBatch ahora guarda indices.
   Aunque OpenGL actual sigue renderizando quads/triangulos en display lists,
   cada batch ya calcula indices triangulados para Vulkan futuro.

3) ChunkMeshData ahora reporta:
   - vertices
   - indices
   - quads
   - triangulos
   - bytes estimados
   - resumen por material

4) RenderBackend ahora mide mas datos:
   - mesh_vertices
   - mesh_indices
   - mesh_bytes
   - material_batches
   - uploads_frame

5) El Admin Hub muestra una segunda linea de debug:
   Mesh: V / I / Q / Batches / RAM~GPU / Uploads

6) build_gpu_list_from_mesh_data ahora dibuja por orden de material:
   - opacos primero
   - translucidos al final: water/shadow

Importancia para Vulkan:
- Vulkan no usa display lists ni glBegin/glEnd.
- Necesita buffers de vertices/indices, materiales y orden de pipelines.
- Esta etapa deja esa informacion preparada mientras OpenGL sigue funcionando.

Siguiente etapa recomendada:
Stage31 Pre-M - RenderPacket/FrameGraph simple.
- Convertir cada chunk visible en paquetes de render por material.
- Separar completamente: decidir que dibujar vs como dibujarlo.
