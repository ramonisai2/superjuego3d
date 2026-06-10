STAGE33 S - COMPARADOR DE PRESETS DEL PUENTE

Objetivo:
- Comparar safe, balanced y aggressive con logs separados.
- Elegir candidato sin cambiar el default automaticamente.
- Mantener OpenGL legacy como ruta jugable estable.

Playtests nuevos:
- LANZAR_PLAYTEST_OPENGL_BRIDGE_SAFE_LOG.bat
- LANZAR_PLAYTEST_OPENGL_BRIDGE_BALANCED_LOG.bat
- LANZAR_PLAYTEST_OPENGL_BRIDGE_AGGRESSIVE_LOG.bat

Cada uno genera:
- juego3d_v1_5\logs\playtest_opengl_bridge_safe.log
- juego3d_v1_5\logs\playtest_opengl_bridge_balanced.log
- juego3d_v1_5\logs\playtest_opengl_bridge_aggressive.log

Comparador:
- COMPARAR_PRESETS_STREAM_BRIDGE.bat

Orden recomendado:
1. Probar safe.
2. Si safe se siente bien, probar balanced.
3. Usar aggressive solo para medir margen.
4. Ejecutar el comparador.

Nota:
- No se hizo ZIP.
- El juego sigue mostrando si usa OPENGL ESTABLE o VULKAN EXPERIMENTAL.
- El default seguro sigue siendo safe hasta que los logs digan otra cosa.

Siguiente etapa recomendada:
Stage33 T - aplicar default recomendado solo si balanced gana limpio.
