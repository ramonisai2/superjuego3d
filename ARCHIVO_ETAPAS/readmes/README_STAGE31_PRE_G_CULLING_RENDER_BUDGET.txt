STAGE31 PRE-G - CULLING BASICO + PRESUPUESTO DE RENDER

Base usada:
- Stage31 Pre-E lagos capa 3 + motor de agua.

Objetivo:
- Seguir optimizando antes de una futura migracion a Vulkan.
- Reducir trabajo desperdiciado sin cambiar todavia de API grafica.

Cambios principales:
1) Culling horizontal de chunks mejorado.
   - Mantiene siempre chunks cercanos para evitar huecos.
   - Descarta chunks claramente detras de la camara.
   - Descarta chunks fuera de distancia maxima.

2) Culling de entidades.
   - Enemigos, NPCs y restos de slime lejanos o claramente fuera de vista no se dibujan.
   - Los objetivos lock-on se siguen dibujando aunque esten fuera del cono simple.
   - NPCs resaltados tambien se mantienen visibles.

3) Menos picos al compilar chunks.
   - CHUNKS_COMPILAR_POR_FRAME pasa a 1 para evitar tirones cuando llegan chunks nuevos.

4) HUD debug de rendimiento en Admin Hub.
   - Cuando Admin Hub esta abierto muestra:
     FPS,
     chunks detallados dibujados,
     chunks LOD dibujados,
     chunks ocultos,
     entidades dibujadas/ocultas.

5) Preparacion para Vulkan.
   - Se separa conceptualmente el paso QUE dibujar del paso DIBUJAR.
   - Esto es un paso previo a una render queue real.

Notas:
- Esto NO es oclusion real todavia: si una montana tapa algo, no necesariamente se descarta.
- Si al girar aparecen huecos, subir back_margin en motor_juegos/environment.py.
- Si sigue pesado, la siguiente etapa debe ser mesh batching/render queue.
