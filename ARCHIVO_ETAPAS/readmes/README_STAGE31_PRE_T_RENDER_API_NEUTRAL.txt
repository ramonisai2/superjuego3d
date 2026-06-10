STAGE 31 PRE-T - RENDER API NEUTRAL

Objetivo:
- Seguir preparando el motor para Vulkan sin romper OpenGL.
- Crear una API de render mas estricta y neutral.

Cambios principales:
1) Nuevo modulo:
   juego3d_v1_5/motor_juegos/render_api.py

2) Se agregaron estructuras neutrales:
   - FrameClearConfig
   - FogConfig
   - CameraSnapshot
   - RendererBackendAPI

3) render_backend.py ahora expone operaciones mas parecidas a un backend real:
   - begin_frame()
   - end_frame()
   - clear()
   - configure_fog(...)
   - draw_skybox(...)
   - project_to_screen(...)
   - upload_chunk_mesh(...)
   - draw_compiled_chunk(...)
   - upload_entity_mesh(...)
   - draw_entity_static_mesh(...)
   - release_gpu_handle(...)
   - shutdown()

4) main.py ya no llama directamente al puente legacy para:
   - limpiar pantalla,
   - configurar rango de niebla,
   - dibujar skybox centrado en camara,
   - proyectar puntos 3D a pantalla.

5) OpenGL sigue siendo el backend activo.
   Vulkan sigue siendo stub, pero ahora la forma esperada del backend esta mas clara.

Por que importa para Vulkan:
- Vulkan no debe depender de llamadas sueltas en main.py.
- El juego debe pedir operaciones de alto nivel al backend.
- Despues Vulkan implementara la misma API con swapchain, command buffers, buffers y pipelines.

Siguiente etapa sugerida:
STAGE31 PRE-U - Buffers simulados / handles neutrales.
