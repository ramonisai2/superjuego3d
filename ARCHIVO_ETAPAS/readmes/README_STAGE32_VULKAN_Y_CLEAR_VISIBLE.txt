STAGE32 VULKAN Y - FARO DEL CLEAR

Objetivo:
- Preparar una ruta dedicada para el primer clear visible Vulkan.
- Separar el experimento Vulkan del modo jugable OpenGL.
- Validar si el backend persistente ya está listo para clear visible.
- Dejar listo el salto a Stage32 Z: modo Vulkan jugable experimental.

Nuevos archivos:
- motor_juegos/vulkan_visible_clear_runner.py
- lanzar_vulkan_clear_visible.py
- diagnostico_vulkan_clear_visible.py
- LANZAR_VULKAN_CLEAR_VISIBLE.bat
- DIAGNOSTICO_VULKAN_CLEAR_VISIBLE.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar ruta clear visible:
  LANZAR_VULKAN_CLEAR_VISIBLE.bat

- Diagnóstico rápido:
  DIAGNOSTICO_VULKAN_CLEAR_VISIBLE.bat

Lectura:
- clearDone = la ruta segura de clear visible pasó.
- native = hace falta wrapper nativo para present real confiable.
- clear-next = backend persistente listo para intentar clear visible real.

Notas:
- OpenGL sigue siendo el juego estable.
- Vulkan sigue experimental.
- Esta etapa prepara el modo Vulkan visible, pero no sustituye todavía el render del juego.
