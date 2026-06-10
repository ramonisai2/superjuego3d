Stage36 Q - HOJAS IMPOSTOR

Objetivo
- Bajar la carga grafica de los arboles.
- Probar copas tipo pseudo 3D estilo consolas antiguas.
- Mantener tronco y silueta reconocible sin dibujar tantas cajas de hojas.

Cambios
- Se agrega _add_leaf_impostor_to_mesh().
- Las copas de arbol_bosque usan planos cruzados + nucleo pequeno.
- Las copas de arbol_pantano usan planos cruzados + menos musgo.
- Las copas de arbol_seco usan una copa quebrada de planos cruzados.
- Los troncos siguen siendo boxel.

Notas
- Es un impostor con planos de color, no una textura PNG todavia.
- Reduce quads de hojas por arbol dentro del mesh del chunk.
- No cambia recoleccion de madera ni posicion de arboles.
- OpenGL estable sigue siendo la ruta jugable.
- No se genero ZIP.
