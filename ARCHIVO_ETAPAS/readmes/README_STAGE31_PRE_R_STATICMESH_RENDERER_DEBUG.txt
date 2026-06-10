STAGE 31 PRE-R - STATICMESH ENTITY RENDERER DEBUG

Objetivo:
- Continuar la migracion hacia Vulkan sin activar Vulkan todavia.
- Probar que EntityInstanceData + StaticMeshInfo + EntityMeshBufferData ya pueden producir entidades visibles sin depender 100% del render legacy.

Cambios principales:
1) Nuevo modulo:
   motor_juegos/entity_static_renderer.py

2) OpenGLRenderBackend ahora tiene una ruta experimental:
   draw_entity_static_mesh(buffer_data, instance)

3) FrameGraph ahora intenta usar esa ruta cuando esta activada.
   Si falla o esta apagada, usa el render legacy normal de entidades.

4) Por defecto el modo esta APAGADO para no romper el arte actual.
   Se activa ejecutando el juego con variable de entorno:

   Windows PowerShell:
     $env:JUEGO_STATIC_ENTITY_RENDER="1"; python main.py

   CMD:
     set JUEGO_STATIC_ENTITY_RENDER=1
     python main.py

5) Admin Hub muestra:
   - StaticDraw: entidades dibujadas con la ruta StaticMesh
   - Debug: 1 si el modo esta activo, 0 si esta apagado

Por que importa para Vulkan:
- Vulkan no va a dibujar llamando enemy.render() o npc.render().
- Necesita una ruta de datos: StaticMesh + InstanceData + buffers.
- Esta etapa prueba esa ruta en OpenGL antes de hacer el backend Vulkan real.

Nota visual:
- El modo StaticMesh es debug, mas simple que el render artistico actual.
- Sirve para validar arquitectura, no para reemplazar aun el arte final.
