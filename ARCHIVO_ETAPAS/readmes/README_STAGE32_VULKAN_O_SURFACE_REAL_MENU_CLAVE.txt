STAGE32 VULKAN O - SURFACE REAL CONTROLADO + NOMBRE CLAVE EN MENU

Nombre clave de la actualizacion:
PUENTE DE BASALTO

Objetivo:
- Continuar la migracion hacia Vulkan con un intento controlado de surface real.
- Mostrar en el menu inicial el nombre clave de la actualizacion.
- Mantener OpenGL como modo jugable estable.

Nuevos archivos:
- motor_juegos/version_info.py
- motor_juegos/vulkan_surface_real_probe.py
- diagnostico_surface_real_vulkan.py
- DIAGNOSTICO_SURFACE_REAL_VULKAN.bat

Cambios visuales/menu:
- El menu inicial ahora muestra:
  - Stage32 Vulkan O
  - Nombre clave: PUENTE DE BASALTO
  - Surface real controlado + menu con nombre clave

Diagnostico nuevo:
- DIAGNOSTICO_SURFACE_REAL_VULKAN.bat

Que prueba:
- pygame/SDL
- ventana pygame minima
- biblioteca SDL2
- funciones SDL_Vulkan_* si estan disponibles
- Vulkan instance
- deteccion de GPU

Nota importante:
- Esta etapa todavia NO reemplaza OpenGL.
- El surface real queda en intento controlado/seguro porque pygame no siempre expone el puntero SDL_Window necesario para SDL_Vulkan_CreateSurface.
- La ruta estable para jugar sigue siendo LANZAR_OPENGL.bat.

Siguiente etapa recomendada:
Stage32 Vulkan P - ventana dedicada Vulkan/SDL o wrapper nativo para obtener SDL_Window* real.
