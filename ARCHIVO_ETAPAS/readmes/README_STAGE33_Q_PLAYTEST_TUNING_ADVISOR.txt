STAGE33 Q - RECOMENDADOR DE AJUSTES

Objetivo:
- Leer el analisis de logs de Stage33 P.
- Decir la siguiente accion concreta.
- Evitar tocar parametros sin datos reales.
- Indicar si hay que mandar logs y cual archivo mandar.

Nuevos archivos:
- motor_juegos/playtest_tuning_advisor.py
- recomendar_ajustes_playtest.py
- RECOMENDAR_AJUSTES_PLAYTEST.bat

Uso recomendado:
1. Ejecutar los dos playtests:
   LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat
   LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat

2. Ejecutar:
   ANALIZAR_PLAYTEST_LOGS.bat

3. Ejecutar:
   RECOMENDAR_AJUSTES_PLAYTEST.bat

Codigos:
- RUN_BOTH = faltan ambos logs.
- RUN_LEGACY = falta log legacy.
- RUN_BRIDGE = falta log bridge.
- FIX_LEGACY = falla OpenGL estable.
- FIX_BRIDGE = falla puente seguro.
- RERUN_BRIDGE_FLAG = el bridge no mostro [STREAM-BRIDGE].
- RERUN_LONGER = prueba demasiado corta.
- ENABLE_NEXT = datos suficientes para seguir.

Siguiente etapa recomendada:
Stage33 R - si ENABLE_NEXT, hacer presupuestos configurables del puente.
