STAGE32 VULKAN N - SURFACE READINESS / SDL PYGAME

Objetivo:
- Antes de intentar presentar Vulkan en pantalla, revisar si el entorno puede conectar:
  pygame/SDL2 + Vulkan + GPU.
- Mantener OpenGL como modo jugable estable.

Nuevos archivos:
- motor_juegos/vulkan_surface_readiness.py
- diagnostico_surface_vulkan.py
- DIAGNOSTICO_SURFACE_VULKAN.bat

Qué revisa:
- pygame disponible.
- versión de pygame.
- versión de SDL.
- driver de video SDL.
- binding Python de Vulkan.
- creación de VkInstance.
- detección de GPU.
- si conviene intentar el surface real en la siguiente etapa.

Cómo usar:
1) Para jugar normal:
   LANZAR_OPENGL.bat

2) Para probar Vulkan experimental:
   LANZAR_VULKAN_EXPERIMENTAL.bat

3) Para diagnóstico surface:
   DIAGNOSTICO_SURFACE_VULKAN.bat

También se puede ejecutar:
python diagnostico_surface_vulkan.py
python -m motor_juegos.vulkan_surface_readiness

Notas:
- Esta etapa todavía NO crea un VkSurfaceKHR real.
- Crear un surface real desde pygame/SDL puede depender de bindings/extensiones disponibles.
- Esta etapa evita crasheos y prepara Stage32 Vulkan O.

Siguiente etapa recomendada:
Stage32 Vulkan O - primer intento controlado de surface real usando SDL/pygame o ventana dedicada.
