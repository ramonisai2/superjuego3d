JUEGO 1.6 - Stage40 P
VEGETATION REPORT STAMP

Objetivo
- Evitar usar un reporte de vegetacion viejo sin darnos cuenta.
- Guardar la etapa que genero vegetation_biomes_report.txt.
- Hacer que ESTADO_RAPIDO_JUEGO.bat avise si el reporte coincide con la etapa actual.

Cambios
- vegetation_preview.py escribe update_stage en vegetation_biomes_report.txt.
- ESTADO_RAPIDO_JUEGO.bat muestra:
  - reporte_etapa
  - reporte_actualizado
- El resumen final muestra si el reporte de vegetacion esta actualizado.

Uso recomendado
- Si reporte_actualizado=NO, ejecutar PREVISUALIZAR_VEGETACION_BIOMAS.bat.
- Despues ejecutar ESTADO_RAPIDO_JUEGO.bat otra vez.
