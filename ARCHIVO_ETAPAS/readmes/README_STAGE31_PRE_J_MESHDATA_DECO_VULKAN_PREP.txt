STAGE 31 PRE-J - MESHDATA DE ROCA/DECORACION + PREPARACION VULKAN

Objetivo:
- Continuar la migracion interna hacia Vulkan sin cambiar todavia el backend real.
- Reducir dependencia de dibujo inmediato/display-list legacy para elementos del mundo.

Cambios principales:
1) MeshData ahora soporta triangulos ademas de quads.
2) Se agrego conteo de triangulos en ChunkMeshData.summary().
3) Las rocas del chunk ya se convierten a MeshData:
   - lados como quads,
   - tapas como triangulos.
4) Decoracion pequena ya se convierte a MeshData:
   - hongos,
   - cactus,
   - cristales,
   - flores,
   - arbustos verdes/secos.
5) Arboles y decoracion compleja siguen en modo legacy por ahora para no romper el estilo visual.
6) El backend OpenGL sigue usando display lists, pero ahora recibe mas datos neutrales que despues Vulkan puede convertir a buffers.

Por que importa:
- Vulkan no dibuja con glBegin/glEnd ni display lists.
- Esta etapa empieza a convertir objetos de mundo en batches de vertices/materiales.
- Reduce el acoplamiento del mundo con OpenGL.

Siguiente etapa recomendada:
Stage31 Pre-K - Arboles como MeshData simplificado + materiales por batch.
