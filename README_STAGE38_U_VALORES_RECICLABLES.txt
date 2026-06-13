JUEGO 1.6 - Stage38 U - VALORES RECICLABLES

Objetivo:
- Revisar si hay valores repetidos que conviene reciclar.
- Evitar crear constantes globales para todo sin necesidad.
- Dejar una herramienta para repetir la auditoria.

Cambio directo:
- main.py ya no repite las densidades base 0.35, 0.35 y 0.55 para recursos.
- Ahora usa:
  - env.GRASS_DENSITY
  - env.DECO_DENSITY
  - env.ROCK_DENSITY

Nueva herramienta:
- juego3d_v1_5\auditar_valores_reciclables.py
- AUDITAR_VALORES_RECICLABLES.bat
- INICIO_JUEGO.bat opcion 14

Reporte:
- juego3d_v1_5\logs\valores_reciclables_report.txt

Lectura:
- Repetido no siempre significa malo.
- Buenos candidatos:
  - distancias de render.
  - densidades de mundo.
  - tamanos base del mundo.
  - umbrales de logs.
  - strings de estado compartidos.
- Malos candidatos:
  - 0, 1, 2 usados como aritmetica local.
  - colores artisticos puntuales.
  - coordenadas pequenas de modelos voxel/boxel.
  - valores que se repiten pero significan cosas distintas.

Regla:
- Reciclar por significado, no por coincidencia.
- No hacer ZIP.
