STAGE 28 FIX K - PANTALLA DE CARGA + LOD DE CHUNKS

Objetivo:
- Evitar zonas negras grandes mientras se genera el mundo.
- Reducir la carga visual causada por chunks, vegetacion y arboles.
- Simular mejor el popping antes de que empiece el mundo jugable.

Cambios principales:
1) Pantalla de carga real antes de entrar al mundo.
   - Prepara los 9 chunks cercanos al spawn antes de iniciar el gameplay.

2) Chunks simples temporales.
   - Cuando un chunk detallado todavia no esta listo, se dibuja una version LOD simple.
   - Esa version tiene terreno y agua simple, sin arboles/pasto/rocas pesadas.
   - Cuando llega el chunk detallado, reemplaza al simple.

3) Chunks lejanos mas baratos.
   - Al alejarte, los chunks complejos se limpian.
   - Si vuelven a ser necesarios, primero aparece su LOD simple y luego el detalle.

4) Se mantiene el arreglo de caida/reaparicion.

Nota:
- Los lagos siguen siendo el siguiente punto fuerte a mejorar; esta version se enfoca en rendimiento/carga visual.
