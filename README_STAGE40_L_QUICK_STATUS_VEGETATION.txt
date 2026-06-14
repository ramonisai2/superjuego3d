JUEGO 1.6 - Stage40 L
QUICK STATUS VEGETATION

Objetivo
- Mostrar el diagnostico de vegetacion dentro de ESTADO_RAPIDO_JUEGO.bat.
- Ver cobertura, arboles, sotobosque y lectura sin abrir la imagen manualmente.
- Mantener el reporte de vegetacion como salida opcional, no como pieza obligatoria.

Cambios
- ESTADO_RAPIDO_JUEGO.bat lee:
  - juego3d_v1_5\previews\vegetation_biomes_report.txt
- Si el reporte existe, muestra:
  - cobertura_total
  - arboles
  - sotobosque
  - lectura
- Si falta, sugiere ejecutar INICIO_JUEGO.bat opcion 10.

Nota
- VERIFICAR_ESTRUCTURA_JUEGO.bat no exige este reporte porque es generado.
- La herramienta principal para actualizarlo sigue siendo PREVISUALIZAR_VEGETACION_BIOMAS.bat.
