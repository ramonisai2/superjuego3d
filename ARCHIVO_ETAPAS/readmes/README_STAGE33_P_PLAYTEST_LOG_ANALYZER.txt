STAGE33 P - LECTOR DE PLAYTEST

Objetivo:
- Leer automaticamente los logs de Stage33 O.
- Detectar si faltan logs, si hay errores y si el puente seguro imprimio [STREAM-BRIDGE].
- Decir que archivo conviene revisar sin pedir logs enormes.
- Mantener OpenGL legacy como ruta estable.

Nuevos archivos:
- motor_juegos/playtest_log_analyzer.py
- analizar_playtest_logs.py
- ANALIZAR_PLAYTEST_LOGS.bat

Uso recomendado:
1. Ejecutar LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat.
2. Ejecutar LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat.
3. Ejecutar ANALIZAR_PLAYTEST_LOGS.bat.

Lectura:
- legacy-log = existe log de OpenGL normal.
- bridge-log = existe log de OpenGL + puente seguro.
- bridge-markers = hay lineas [STREAM-BRIDGE].
- legacyErrN = errores detectados en legacy.
- bridgeErrN = errores detectados en bridge.
- logsOK = ambos logs existen y no se detectaron errores basicos.

Siguiente etapa recomendada:
Stage33 Q - ajustar el puente usando el resultado del analizador o los logs concretos.
