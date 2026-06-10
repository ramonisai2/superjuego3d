STAGE 31 PRE-P - STATICMESH CATALOG / VULKAN PREP

Objetivo:
- Seguir preparando el motor para Vulkan sin abandonar OpenGL todavía.
- Separar geometría estática de entidades y datos de instancia.

Cambios principales:
1) Nuevo módulo:
   motor_juegos/entity_mesh_catalog.py

2) Nuevo concepto:
   StaticMeshInfo
   StaticBoxPart
   EntityMeshCatalog

3) Catálogo inicial de meshes neutrales:
   - mesh_player_boxel
   - mesh_npc_humanoid
   - mesh_slime_basic
   - mesh_unknown_box

4) EntityInstanceData ahora incluye:
   - mesh_id

5) RenderFrameGraph ahora adjunta static_mesh al payload de cada entidad.
   Por ahora el dibujo sigue usando render_fn legacy/OpenGL, pero ya existe
   la información necesaria para que Vulkan use geometry buffers + instance buffers.

Por qué importa:
- Vulkan no conviene dibujar cada entidad como función suelta.
- Vulkan funciona mejor con:
  StaticMesh + InstanceData + Material + RenderPass.
- Esta etapa empieza a separar:
  geometría reutilizable de entidades
  vs
  posición/rotación/escala de cada entidad.

Siguiente etapa recomendada:
Stage31 Pre-Q - convertir el catálogo StaticMesh a MeshData/buffers simulados,
y preparar upload_entity_mesh(...) en render_backend.
