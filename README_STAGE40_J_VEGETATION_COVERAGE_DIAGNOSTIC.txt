JUEGO 1.6 - Stage40 J
VEGETATION COVERAGE DIAGNOSTIC

Objetivo
- Medir si la vegetacion esta vacia, sana o saturada sin abrir el juego 3D.
- Usar la misma preview offline de vegetacion.
- Tener numeros rapidos antes de tocar densidades o reglas de bioma.

Cambios
- vegetation_preview.py calcula cobertura total del terreno visible.
- La imagen agrega un bloque de diagnostico con:
  - cobertura total.
  - porcentaje de arboles.
  - porcentaje de sotobosque.
  - lectura: vacio, sano o saturado.
- previsualizar_vegetacion_biomas.py imprime los mismos datos en consola.

Lectura
- vacio: conviene agregar detalle o subir probabilidades.
- sano: rango recomendable para seguir probando en OpenGL.
- saturado: bajar densidad antes de agregar mas vegetacion.

Nota
- Esta metrica es de preview 2D, no de FPS. Sirve para detectar exceso visual antes del playtest.
