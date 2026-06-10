STAGE33 O - PRUEBA JUGABLE GUIADA

Objetivo:
- Probar OpenGL legacy y OpenGL + puente seguro con logs separados.
- Evitar pedir logs enormes o ambiguos.
- Mantener OpenGL legacy como ruta estable.
- Hacer que el puente seguro imprima lineas [STREAM-BRIDGE] cada 0.5s.

Uso recomendado:
1. Ejecutar:
   LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat

2. Caminar 1-2 minutos, cruzando chunks.

3. Ejecutar:
   LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat

4. Hacer la misma ruta aproximada.

Logs:
- Legacy:
  juego3d_v1_5/logs/playtest_opengl_legacy.log

- Puente seguro:
  juego3d_v1_5/logs/playtest_opengl_bridge.log

Si algo falla:
- Si falla OpenGL normal, mandar playtest_opengl_legacy.log.
- Si falla solo el puente seguro, mandar playtest_opengl_bridge.log.
- Buscar lineas [STREAM-BRIDGE] para ver calls, center, req, lod, freeD, freeL, cancel, queue, pending, loadedD y loadedL.

Siguiente etapa recomendada:
Stage33 P - leer el log de playtest y ajustar el puente segun datos reales.
