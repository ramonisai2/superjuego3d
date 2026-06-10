STAGE35 H - UNIDAD BOXEL

Objetivo:
- Evitar que cada accesorio use medidas arbitrarias.
- Definir una unidad comun para boxels generados.
- Preparar herramientas, armas, orejas y narices con escala consistente.

Regla:
- BOXEL_UNIT = 0.055
- Los detalles nuevos deben usar draw_boxel(cx, cy, cz, ux, uy, uz, color).
- ux, uy y uz son cantidades enteras de boxels.

Cambios:
- Se agrego BOXEL_UNIT.
- Se agrego draw_boxel().
- Nariz 3D usa boxels 1x1x1.
- Orejas humanas/elfo/duende usan multiplos de boxel.
- Herramientas/armas reservadas usan multiplos de boxel.

Notas:
- No se reescalo de golpe el cuerpo completo del jugador/NPC para evitar romper proporciones.
- La regla aplica a rasgos, accesorios, herramientas, armas y piezas nuevas.
- No se hizo ZIP.
