# STAGE31 PRE-H - Render Backend para migracion a Vulkan

Esta etapa NO cambia aun el juego a Vulkan. El objetivo es preparar el motor para que Vulkan pueda entrar sin reescribir todo de golpe.

## Cambios reales

- Nuevo modulo: `motor_juegos/render_backend.py`
- Nuevo modulo: `motor_juegos/render_queue.py`
- Se crea un backend activo:
  - `OpenGLRenderBackend`
- Se deja un esqueleto futuro:
  - `VulkanRenderBackend`
- Las llamadas para dibujar chunks compilados pasan por `render_backend.draw_compiled_chunk(...)`.
- Las llamadas para liberar display lists pasan por `render_backend.release_gpu_handle(...)`.
- Los handles de chunks se registran con `render_backend.register_gpu_handle(...)`.
- El Admin Hub ahora muestra el backend actual: `Render[opengl]`.

## Por que esto importa

Antes el juego estaba mas atado a OpenGL directamente:

```text
main.py -> env.draw_compiled_chunk -> OpenGL display list
main.py -> glDeleteLists
```

Ahora empieza a quedar asi:

```text
main.py -> render_backend -> OpenGL actual
                         -> Vulkan futuro
```

## Vulkan todavia no esta activo

El backend Vulkan es solo un stub. Para activarlo de verdad hacen falta etapas posteriores:

1. Convertir chunks a mallas de vertices/indices.
2. Dejar de depender de display lists.
3. Crear buffers GPU por chunk.
4. Crear command buffers por frame.
5. Crear swapchain, pipeline, shaders y sincronizacion.

## Siguiente etapa recomendada

`Stage31 Pre-I - MeshData por chunk`

Objetivo:
- Que `environment.py` pueda producir datos de malla independientes de OpenGL.
- OpenGL los puede seguir dibujando por ahora.
- Vulkan podria consumir esos datos despues.

