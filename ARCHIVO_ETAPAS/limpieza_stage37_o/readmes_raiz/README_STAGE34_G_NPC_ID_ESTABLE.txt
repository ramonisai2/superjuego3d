STAGE34 G - NPC ID ESTABLE

Objetivo:
- Dar a cada NPC una identidad unica generada por algoritmo.
- Separar la identidad del NPC de su semilla de atributos.
- No cambiar nombre, titulo, profesion, hostilidad, dano ni rasgos especiales.

Cambios:
- NPC.id ya no es solamente el seed.
- Nuevo algoritmo build_npc_id(seed, x, z, source, slot).
- El seed se conserva como NPC.seed para que siga siendo el ADN del personaje.
- NPCs de chunk usan source chunk_x_z y slot de generacion.
- NPCs creados desde Admin Hub usan source admin.
- NPCs legendarios usan source legendary.

Notas:
- Las conversaciones quedan igual por ahora.
- El sistema nuevo de conversaciones/memoria puede usar este ID mas adelante.
- No se hizo ZIP.
