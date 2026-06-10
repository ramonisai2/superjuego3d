Stage36 X - GEOMETRIA POR PRESET

Objetivo
- Reducir vertices por pieza en modo bajo.
- Mantener balanced/high con siluetas mas completas.
- Bajar costo de hierba, flores, arbustos, hongos y copas impostor.

Cambios
- low usa 1 plano para hierba.
- low usa 1 plano para decoracion pequena tipo flor, arbusto y hongo.
- low usa 2 planos en copas impostor de arbol.
- balanced/high conservan los planos cruzados actuales.
- Se agregan overrides JUEGO_GRASS_PLANES, JUEGO_DECO_PLANES y JUEGO_LEAF_PLANES.

Notas
- Afecta chunks que se convierten a MeshData despues de iniciar.
- No cambia recoleccion, colisiones ni escala boxel.
- No elimina recursos; solo baja vertices de la representacion visual.
- No se genero ZIP.
