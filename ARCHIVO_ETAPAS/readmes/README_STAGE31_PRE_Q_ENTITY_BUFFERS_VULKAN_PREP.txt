STAGE 31 PRE-Q - ENTITY BUFFERS / VULKAN PREP

Objetivo:
- Continuar la migracion hacia Vulkan sin cambiar todavia el backend real.
- Convertir las mallas estaticas de entidades a datos de buffer neutrales.

Cambios principales:
1) Nuevo modulo:
   motor_juegos/entity_mesh_buffers.py

2) Nuevas estructuras:
   - EntityMeshBufferData
   - EntityMeshBufferCache

3) Ahora StaticMeshInfo del catalogo de entidades puede convertirse a:
   - vertices,
   - indices,
   - batches por material,
   - estimacion de bytes.

4) render_backend.py ahora tiene:
   - upload_entity_mesh(...)

5) OpenGL todavia dibuja entidades con el sistema legacy, pero al mismo tiempo
   crea/cachea buffers neutrales de entidad.

6) VulkanRenderBackend ya tiene el punto de entrada documentado para reemplazar
   esos datos por VkBuffer reales mas adelante.

Importante:
- Esta etapa NO activa Vulkan real.
- Esta etapa prepara la ruta correcta:

  EntityInstanceData
      +
  StaticMeshInfo
      -> EntityMeshBufferData
      -> OpenGL legacy ahora
      -> Vulkan buffers despues

Siguiente etapa recomendada:
- Stage31 Pre-R: Renderer de entidades por StaticMesh opcional/debug.
- Luego Stage31 Pre-S: command buffer simulado y limites de frame.
