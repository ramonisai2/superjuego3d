STAGE 31 PRE-B - CHUNKS REDUCIDOS

Objetivo:
- Probar chunks mas pequeños para bajar la carga por bloque de mundo.
- Reducir popping grande y zonas negras al generar.

Cambios principales:
1) CHUNK_SIZE: 100 -> 64
2) SUBDIVISIONES detalle: 64 -> 48
3) SUBDIVISIONES_LOD: 12 -> 8
4) RADIO_VISION: 1 -> 2
   - Hay mas chunks simples alrededor, pero cada uno es mucho mas barato.
5) RADIO_DETALLE se mantiene en 0:
   - Solo el chunk actual se detalla completo.
   - Los demas se quedan en LOD simple hasta que te acerques.

Que revisar:
- Si desaparecen o bajan las zonas negras grandes.
- Si el popping es menos brusco.
- Si al cruzar chunks no hay tirones fuertes.
- Si el mundo se ve demasiado corto de distancia o si el radio 2 simple alcanza.

Nota:
- Esta version prioriza rendimiento sobre detalle visual lejano.
- Si va mejor, despues podemos probar culling real: no renderizar lo que esta fuera de camara o tapado.
