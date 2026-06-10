STAGE 31 PRE-M - RENDERPACKET / FRAMEGRAPH SIMPLE - VULKAN PREP

Objetivo:
- Continuar la migracion hacia Vulkan sin romper OpenGL.
- Cambiar mentalidad de "dibujar directo" a "armar paquetes de render por frame".

Cambios principales:
1) Nuevo modulo:
   motor_juegos/frame_graph.py

2) Nuevas estructuras:
   - RenderPacket
   - RenderPass
   - RenderFrameGraph

3) Los chunks visibles ahora pasan por un FrameGraph simple:
   - world_lod
   - world_detail

4) El render de chunks queda organizado asi:
   culling -> RenderPacket -> RenderPass -> execute_chunks(OpenGLBackend)

5) El Admin Hub muestra nuevas estadisticas:
   - Pass: cantidad de pases de render
   - Pack: cantidad de paquetes de render visibles

Por que importa para Vulkan:
- Vulkan necesita ordenar el frame por passes y command buffers.
- Esta etapa empieza esa estructura sin apagar el backend OpenGL.
- Los chunks todavia usan handles OpenGL, pero ya viajan dentro de paquetes neutrales.

Pendiente:
- Migrar entidades a RenderPacket completo.
- Separar pass opaco/transparente real para agua/sombras.
- Convertir OpenGL display lists a buffers propios.
- Crear backend Vulkan experimental real en etapa futura.
