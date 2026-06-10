STAGE33 U - PERF MOVIMIENTO

Motivo:
- El cambio a Vulkan no debe usarse a ciegas.
- Si los FPS bajan al moverse con mapa casi vacio, primero hay que medir si el golpe viene de chunks, render, update, IA o presentacion.

Correccion aplicada:
- La gestion de chunks ya no usa el temporizador de logs.
- Antes podia correr demasiadas veces entre cada log de 0.5 s.
- Ahora usa un temporizador independiente de 50 ms.

Lanzadores:
- LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat
- LANZAR_PERF_MOVIMIENTO_OPENGL_BRIDGE_LOG.bat
- ANALIZAR_PERF_MOVIMIENTO.bat

Uso recomendado:
1. Ejecuta LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat.
2. Camina 1-2 minutos cruzando chunks.
3. Cierra el juego.
4. Ejecuta LANZAR_PERF_MOVIMIENTO_OPENGL_BRIDGE_LOG.bat.
5. Camina igual.
6. Ejecuta ANALIZAR_PERF_MOVIMIENTO.bat.

Logs generados:
- juego3d_v1_5\logs\perf_movimiento_opengl_legacy.log
- juego3d_v1_5\logs\perf_movimiento_opengl_bridge_safe.log

Que mide:
- frame
- update
- chunk_total
- chunk_admin
- chunk_comm
- chunk_compile
- player_move
- world_context
- ai
- render3d
- render2d
- flip

Regla:
- Si chunk_total o chunk_compile suben mucho al moverse, el problema no es solo Vulkan.
- Si render3d sube, toca reducir dibujo/vertices/batches.
- Si flip sube, puede ser driver/vsync/presentacion.

Siguiente etapa recomendada:
Stage33 V - optimizar el cuello de botella que salga en ANALIZAR_PERF_MOVIMIENTO.
