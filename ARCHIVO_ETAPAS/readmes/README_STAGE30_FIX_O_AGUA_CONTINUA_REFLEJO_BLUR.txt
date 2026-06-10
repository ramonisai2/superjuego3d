STAGE 30 FIX O - AGUA CONTINUA ENTRE CHUNKS + REFLEJO BLUR

Problemas observados:
- El agua marcaba cortes/costuras entre chunks.
- La superficie del lago se veia demasiado muerta/plana.

Cambios principales:
1) Calculo de chunks con borde extra invisible:
   - El terreno, agua y mascara de orillas ahora se calculan con padding alrededor del chunk.
   - Luego se recorta el centro del chunk.
   - Esto reduce diferencias en los bordes entre chunks vecinos.

2) Solape minimo de quads de agua:
   - Las superficies de agua se extienden apenas un poco fuera de su celda.
   - Esto ayuda a tapar lineas negras/costuras entre celdas y chunks.

3) Reflejo blur barato:
   - Se agregaron bandas transparentes azul/blanco sobre el agua.
   - No usa shaders ni texturas.
   - Da vida al lago sin aumentar mucho la carga.

4) LOD simple actualizado:
   - Los chunks temporales simples tambien usan padding.
   - El agua simple tambien tiene solape y brillo leve.

Que revisar:
- Si el corte negro entre chunks de agua disminuye o desaparece.
- Si el agua se ve un poco mas viva sin volverse pesada.
- Si el LOD temporal no rompe mas el agua al cambiar de simple a detallado.
