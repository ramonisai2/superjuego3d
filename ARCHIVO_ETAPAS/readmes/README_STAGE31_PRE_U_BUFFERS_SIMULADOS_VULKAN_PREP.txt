STAGE 31 PRE-U - BUFFERS SIMULADOS / HANDLES NEUTRALES VULKAN PREP

Objetivo:
- Seguir preparando la migracion a Vulkan sin activar Vulkan todavia.
- Dejar de tratar los chunks como enteros/direct display lists de OpenGL desde el resto del motor.

Cambios principales:
1) Nuevo modulo:
   juego3d_v1_5/motor_juegos/gpu_resources.py

2) Nuevas estructuras neutrales:
   - NeutralBufferDesc
   - NeutralMeshHandle
   - NeutralTextureHandle
   - ResourceFrameStats

3) OpenGL sigue usando display lists internamente, pero ahora las envuelve en NeutralMeshHandle.

Antes:
   chunk -> display list OpenGL -> handle entero

Ahora:
   chunk -> MeshData -> NeutralMeshHandle -> backend_handle OpenGL

4) render_backend.upload_chunk_mesh(...) ahora devuelve un handle neutral.

5) render_backend.draw_compiled_chunk(...) acepta el nuevo handle neutral y extrae internamente el handle OpenGL.

6) render_backend.release_gpu_handle(...) libera el recurso usando el backend_handle interno y actualiza estadisticas.

7) Estadisticas nuevas para preparar diagnostico:
   - live_mesh_handles
   - live_mesh_bytes
   - neutral_mesh_created
   - neutral_mesh_released

Por que importa para Vulkan:
- Vulkan no puede usar display lists.
- Necesita handles de recursos: buffers, imagenes, materiales, descriptor sets.
- Esta etapa hace que el motor empiece a hablar con recursos neutrales en vez de OpenGL directo.

Estado:
- Vulkan real todavia NO esta activo.
- OpenGL sigue siendo el backend funcional.
- Esta etapa es una capa de compatibilidad para facilitar la siguiente migracion.

Siguiente etapa recomendada:
Stage31 Pre-V - shaders/materiales basicos y pipeline descriptors simulados.
