JUEGO 1.6 - Stage40 N
VEGETATION MULTISEED CHECK

Objetivo
- Evitar balancear la vegetacion usando una sola semilla.
- Confirmar que la cobertura se mantiene sana en varios mundos.
- Mantener una prueba barata sin abrir OpenGL.

Cambios
- vegetation_preview.py calcula muestras de cobertura para varias semillas.
- vegetation_biomes_report.txt ahora incluye la seccion MUESTRAS_MULTISEED.
- previsualizar_vegetacion_biomas.py imprime estabilidad y rango de cobertura.

Lectura
- stability=estable: todas las semillas muestreadas quedaron en rango sano.
- stability=revisar: alguna semilla salio vacia o saturada.

Nota
- La imagen principal sigue usando la semilla base 12345.
- Las muestras multisemilla usan una resolucion menor para mantenerse rapidas.
