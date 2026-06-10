STAGE 31 PRE-S - OPENGL LEGACY CLEANUP

Objetivo:
- Continuar la migracion hacia Vulkan sin saltar todavia a Vulkan real.
- Sacar llamadas OpenGL sueltas de main.py y moverlas a un puente temporal centralizado.

Cambios principales:
1) Nuevo archivo:
   juego3d_v1_5/motor_juegos/gl_legacy_bridge.py

2) main.py ya no importa directamente:
   - glPushMatrix/glPopMatrix/glTranslatef para el skybox
   - glGetDoublev/glGetIntegerv/gluProject para labels 2D
   - glFogf para rango de niebla
   - glClear para pantalla simple

3) Esas llamadas quedaron centralizadas en funciones puente:
   - set_fog_range(...)
   - draw_skybox_at_camera(...)
   - world_to_screen_legacy(...)
   - clear_color_depth()

4) Nuevo script de auditoria:
   juego3d_v1_5/tools/audit_opengl_legacy.py

   Ejecutar desde juego3d_v1_5:
   python tools/audit_opengl_legacy.py

5) Titulo de ventana actualizado a:
   JUEGO 1.6 - Stage 31 Pre-S OpenGL Legacy Cleanup

Por que esto ayuda a Vulkan:
- Vulkan no podra usar llamadas OpenGL sueltas repartidas por main.py.
- Esta etapa empieza a concentrar el render legacy para que luego OpenGLRenderBackend y VulkanRenderBackend puedan compartir interfaz.
- Todavia quedan llamadas OpenGL en environment.py, voxel_models.py, renderer2d.py y renderer3d.py; esas se migraran por etapas.

Siguiente etapa recomendada:
- Stage31 Pre-T - Render API neutral estricta:
  begin_frame/end_frame, clear, fog, skybox, project_to_screen, upload_mesh, draw_mesh, draw_instances.
