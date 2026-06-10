STAGE34 B - CURRENT OPTIMIZADO

Objetivo:
- Mantener current como metodo final candidato.
- Reducir trabajo repetido sin perder lagos, mesetas ni riachuelos.

Cambio:
- Terreno y agua ahora comparten campos ya calculados:
  - lake_basin
  - high_lake_basin
  - mesa_strength
- Antes el agua recalculaba esas formas grandes.

Resultado observado:
- current quedo cerca de 509 ms en el benchmark de chunk completo.
- fast_noise no gana cuando conserva identidad natural.
- fast_noise_lite sigue siendo solo referencia de rendimiento.

Default:
- current sigue activo por defecto.

No se hizo ZIP.
