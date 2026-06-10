STAGE 31 PRE-K - MeshData para arboles rumbo a Vulkan

Objetivo:
- Continuar la migracion gradual hacia Vulkan sin romper OpenGL.
- Reducir dependencia de glBegin/glEnd y display lists legacy.

Cambios principales:
1) Los arboles principales ahora se convierten a MeshData simplificado:
   - arbol_bosque
   - arbol_pantano
   - arbol_seco

2) Los arboles ya no dependen del dibujado legacy inmediato cuando entran en el chunk mesh:
   - troncos -> batch tree_trunks
   - hojas/copa -> batch tree_leaves
   - musgo/raices -> batch tree_moss
   - sombras planas -> batch shadows

3) Se agrego soporte de batches translucidos genericos:
   - water
   - shadow

4) Se mantiene OpenGL como backend temporal:
   - MeshData todavia se sube a display list para renderizar.
   - Vulkan podra usar estos mismos datos despues como vertex/index buffers.

Notas:
- Los arboles son una version simplificada boxel; no copian 1:1 todo el arbol legacy.
- Esto prioriza rendimiento y arquitectura para Vulkan.
- Si se ve demasiado simple, se pueden agregar mas piezas al MeshData sin volver al renderer legacy.

Siguiente etapa recomendada:
- Stage31 Pre-L: indices/materiales por batch y estadisticas de vertices por material.
