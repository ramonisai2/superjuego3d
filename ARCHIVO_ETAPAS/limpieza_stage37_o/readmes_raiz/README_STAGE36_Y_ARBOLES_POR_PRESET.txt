Stage36 Y - ARBOLES POR PRESET

Objetivo
- Reducir costo visual de arboles en modo bajo.
- Mantener siluetas completas en balanced/high.
- Evitar tocar recoleccion de madera o posicion de arboles.

Cambios
- low usa 1 capa de arbol.
- low omite sombras planas de arbol.
- low omite copas secundarias.
- low omite musgo extra en arboles de pantano.
- balanced/high mantienen capas, sombras y adornos actuales.
- Se agrega override JUEGO_TREE_LAYERS.

Notas
- Afecta chunks convertidos a MeshData despues de iniciar.
- No cambia la cantidad de arboles generados; eso sigue en la densidad por preset.
- No cambia recoleccion, colisiones ni escala boxel.
- No se genero ZIP.
