STAGE 31 PRE-I - MESHDATA VULKAN PREP

Objetivo:
- Continuar la migracion hacia Vulkan sin romper OpenGL.
- Empezar a sacar el mundo del modelo mental de "display list OpenGL".
- Introducir datos de malla neutrales que luego Vulkan pueda transformar en buffers.

Cambios principales:
1) Nuevo archivo:
   motor_juegos/mesh_data.py

   Contiene:
   - MeshBatch
   - ChunkMeshData
   - conteo de vertices/quads

2) Nuevo flujo para chunks detallados:
   antes:
     datos procedurales -> env.build_gpu_list_from_data -> OpenGL display list

   ahora:
     datos procedurales -> ChunkMeshData -> render_backend.upload_chunk_mesh -> OpenGL display list

3) OpenGL sigue funcionando igual visualmente, pero ahora la subida del chunk pasa por:
   render_backend.upload_chunk_mesh(mesh_data)

4) Vulkan todavia no esta activo.
   El VulkanRenderBackend sigue como stub, pero ya sabemos que recibira ChunkMeshData
   cuando sea momento de crear vertex buffers / index buffers.

5) Terreno, agua y pasto ya entran a MeshBatch.
   Rocas y decoraciones aun quedan como legacy dentro de ChunkMeshData.
   Esto es intencional para no romper el juego de golpe.

Siguiente etapa recomendada:
- Stage31 Pre-J: migrar rocas/decoraciones a MeshData o crear batching por material.
- Despues: VertexBuffer conceptual para OpenGL/Vulkan.

Notas:
- Esta version debe verse casi igual que Pre-H.
- La mejora principal es interna/arquitectonica, no visual.
- Es un paso necesario antes de Vulkan real.
