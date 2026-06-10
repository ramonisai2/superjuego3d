STAGE32 VULKAN Q - PUENTE SDL/VULKAN SURFACE

Nombre clave:
PUERTA DE MAGMA

Objetivo:
- Preparar un puente controlado hacia SDL_Vulkan_CreateSurface.
- Detectar si pygame expone un SDL_Window* seguro.
- Evitar crasheos por casts inseguros.
- Decidir si la siguiente etapa requiere wrapper nativo o SDL2 directo.

Nuevos archivos:
- motor_juegos/vulkan_sdl_surface_bridge.py
- diagnostico_surface_bridge.py
- DIAGNOSTICO_SURFACE_BRIDGE.bat

Qué revisa:
- pygame y ventana.
- wm_info de pygame.
- libreria SDL2.
- funciones SDL_Vulkan_*.
- Vulkan instance.
- GPU.
- si hace falta wrapper nativo.

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico puente surface:
  DIAGNOSTICO_SURFACE_BRIDGE.bat

Lectura:
- Si marca native-next, pygame no da un SDL_Window* seguro.
- En ese caso Stage32 R debería crear una ventana SDL2 directa o usar un pequeño wrapper nativo.
