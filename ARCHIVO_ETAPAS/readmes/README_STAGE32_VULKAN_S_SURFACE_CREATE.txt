STAGE32 VULKAN S - SDL_VULKAN_CREATESURFACE

Nombre clave:
FORJA DEL SURFACE

Objetivo:
- Primer intento controlado de crear un VkSurfaceKHR real.
- Usar ventana SDL2 directa con SDL_WINDOW_VULKAN.
- Obtener extensiones requeridas por SDL.
- Crear VkInstance con esas extensiones.
- Intentar SDL_Vulkan_CreateSurface si el binding Python permite obtener un handle crudo seguro.

Nuevos archivos:
- motor_juegos/vulkan_sdl_surface_create_probe.py
- diagnostico_surface_create.py
- DIAGNOSTICO_SURFACE_CREATE.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnosticar surface real:
  DIAGNOSTICO_SURFACE_CREATE.bat

Lectura de resultado:
- surfOK = se creo VkSurfaceKHR.
- ext + inst pero sin surfOK = falta acceso a raw VkInstance compatible con ctypes o wrapper nativo.
- Si no hay ext/inst = revisar Vulkan SDK/runtime/SDL2.

Notas:
- OpenGL sigue siendo la ruta jugable.
- Esta etapa no reemplaza el render del juego.
- El siguiente paso depende del resultado:
  A) si surfOK: Stage32 T puede crear swapchain real.
  B) si no surfOK por raw instance: crear wrapper nativo pequeño.
