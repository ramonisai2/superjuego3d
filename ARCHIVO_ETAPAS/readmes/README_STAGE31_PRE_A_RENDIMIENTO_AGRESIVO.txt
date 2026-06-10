STAGE 31 PRE-A - RENDIMIENTO AGRESIVO

Objetivo:
- Ahorrar recursos antes de meter culling mas complejo.
- Reducir carga de CPU/GPU en chunks, vegetacion y decoracion.

Cambios principales:
1) Chunks:
   - Solo el chunk actual se genera con detalle completo.
   - El anillo visible alrededor usa LOD simple barato.
   - La prediccion hacia adelante crea solo LOD simple, no detalle pesado.

2) Resolucion:
   - SUBDIVISIONES bajo de 96 a 64 para el chunk detallado.
   - SUBDIVISIONES_LOD bajo a 12 para chunks simples.

3) Cola de generacion:
   - MAX_COLA_PETICIONES bajo a 1.
   - Esto evita saturar CPU cuando el jugador corre o cambia rapido de zona.

4) Vegetacion y decoracion:
   - Pasto reducido aproximadamente a 35%.
   - Flores/arbustos/decoracion reducidos aproximadamente a 35%.
   - Rocas reducidas aproximadamente a 55%.
   - Arboles de oasis reducidos mucho mas.

5) Arboles:
   - Troncos redondos usan menos segmentos.
   - Mantienen forma, pero con menos geometria.

Notas:
- Esta version es agresiva y puede verse mas vacia a distancia.
- Sirve para comprobar si el problema principal era exceso de chunks detallados/vegetacion.
- Despues de probar esto podemos revisar culling real: no renderizar lo que queda fuera de camara, detras del jugador o tapado por relieve.
