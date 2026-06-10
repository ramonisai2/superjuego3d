Stage36 Z - ROCAS POR PRESET

Objetivo
- Reducir costo de rocas en modo bajo.
- Mantener rocas mas irregulares en balanced/high.
- No tocar colisiones ni recoleccion de piedra.

Cambios
- low usa rocks_simple con cajas directas.
- balanced/high conservan lados irregulares y tapas trianguladas.
- Se agrega override JUEGO_ROCK_DETAIL.

Notas
- Afecta chunks convertidos a MeshData despues de iniciar.
- No cambia cantidad de rocas; eso sigue en la densidad por preset.
- No cambia el indice de recoleccion ni la hitbox de terreno.
- No se genero ZIP.
