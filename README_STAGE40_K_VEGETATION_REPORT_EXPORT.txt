JUEGO 1.6 - Stage40 K
VEGETATION REPORT EXPORT

Objetivo
- Guardar los numeros de la preview de vegetacion para comparar cambios entre etapas.
- Evitar depender de la consola o de memoria.
- Dar una recomendacion rapida cuando la cobertura se vea vacia, sana o saturada.

Cambios
- vegetation_preview.py genera:
  - vegetation_biomes_preview.png
  - vegetation_biomes_report.txt
- previsualizar_vegetacion_biomas.py imprime tambien la ruta del reporte.

Salida
- juego3d_v1_5\previews\vegetation_biomes_report.txt

Uso recomendado
- Ejecutar PREVISUALIZAR_VEGETACION_BIOMAS.bat despues de tocar biomas, arboles o sotobosque.
- Comparar cobertura_total, arboles y sotobosque antes de aumentar densidad.
- Si lectura=saturado, bajar reglas antes de agregar mas elementos.
