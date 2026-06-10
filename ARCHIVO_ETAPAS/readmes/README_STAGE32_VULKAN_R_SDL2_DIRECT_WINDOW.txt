STAGE32 VULKAN R - SDL2 DIRECT WINDOW

Nombre clave:
YUNQUE DE OBSIDIANA

Objetivo:
- Probar una ruta SDL2 directa con ctypes, separada de pygame.
- Obtener un SDL_Window* real.
- Verificar funciones SDL_Vulkan_*.
- Preparar Stage32 S: intento real de SDL_Vulkan_CreateSurface.

Nuevos archivos:
- motor_juegos/vulkan_sdl2_direct_probe.py
- diagnostico_sdl2_direct_vulkan.py
- DIAGNOSTICO_SDL2_DIRECT_VULKAN.bat

Qué prueba:
- localizar SDL2.
- SDL_Init.
- SDL_CreateWindow con SDL_WINDOW_VULKAN.
- puntero SDL_Window*.
- funciones SDL_Vulkan_*.
- Vulkan instance.
- GPU.

Uso:
- Jugar normal:
  LANZAR_OPENGL.bat

- Diagnóstico SDL2 directo:
  DIAGNOSTICO_SDL2_DIRECT_VULKAN.bat

Lectura:
- Si aparece surface-next, podemos intentar el surface real en Stage32 S.
- Si falla SDL2 directo, habrá que usar un wrapper nativo o instalar runtime/dev de SDL2.
