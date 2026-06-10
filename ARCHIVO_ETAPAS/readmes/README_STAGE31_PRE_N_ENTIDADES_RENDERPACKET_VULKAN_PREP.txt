STAGE 31 PRE-N - ENTIDADES COMO RENDERPACKET / VULKAN PREP

Objetivo:
- Continuar la migracion hacia Vulkan sin cambiar todavia el backend real.
- Sacar mas dibujo directo desde main.py y pasarlo por el FrameGraph.

Cambios principales:
1) El jugador en tercera persona ahora entra como RenderPacket tipo "player".
2) Enemigos entran como RenderPacket tipo "enemy".
3) NPCs entran como RenderPacket tipo "npc".
4) Restos de slime entran como RenderPacket transparente tipo "slime_remnant".
5) El FrameGraph ahora ejecuta chunks y entidades en pases ordenados.
6) Se agrego pass transparente inicial para entidades transparentes.
7) El HUD/Admin muestra TransEnt para entidades transparentes renderizadas.

Importante:
- Las entidades todavia usan callbacks legacy para llamar sus metodos render().
- Esto es temporal y seguro: permite ordenar el frame sin reescribir todos los modelos.
- La siguiente etapa deberia convertir entidades simples a MeshData/InstanceData.

Ruta Vulkan:
main.py -> RenderFrameGraph -> RenderPacket -> OpenGL actual
                                    -> Vulkan futuro
