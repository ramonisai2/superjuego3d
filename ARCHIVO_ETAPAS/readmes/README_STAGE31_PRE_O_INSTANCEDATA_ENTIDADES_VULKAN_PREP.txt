STAGE 31 PRE-O - INSTANCEDATA DE ENTIDADES / VULKAN PREP

Objetivo:
- Seguir la migracion hacia Vulkan sin romper el render OpenGL actual.
- Las entidades todavia se dibujan con callbacks legacy, pero ahora tambien generan datos de instancia neutrales.

Cambios:
1) Nuevo modulo:
   motor_juegos/instance_data.py

2) Nuevas estructuras:
   - EntityInstanceData
   - InstanceFrameData

3) El FrameGraph ahora guarda instancias por frame para:
   - jugador,
   - enemigos,
   - NPCs,
   - restos de slime transparentes.

4) Admin Hub muestra estadisticas de instancias:
   - total,
   - tipos,
   - transparentes,
   - player/enemy/npc.

Por que importa para Vulkan:
- Vulkan trabaja bien con buffers de instancias.
- Este paso empieza a separar: entidad del juego -> datos de render -> backend.
- OpenGL sigue funcionando como respaldo.

Siguiente etapa recomendada:
Stage31 Pre-P - StaticMesh / EntityMeshCatalog para que slimes, NPCs y jugador tengan mallas reutilizables.
