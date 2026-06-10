STAGE 31 PRE-Y - VULKAN TRIANGLE / QUAD BUFFERS

Objetivo:
- Avanzar un paso mas hacia Vulkan sin romper el juego OpenGL.
- No renderiza todavia el mundo completo en Vulkan.
- Mantiene OpenGL como camino jugable.

Cambios principales:
1) Nuevo modulo:
   juego3d_v1_5/motor_juegos/vulkan_triangle_probe.py

2) La prueba Vulkan ahora intenta:
   - importar el paquete Python vulkan,
   - crear instancia Vulkan,
   - detectar GPU,
   - encontrar queue family grafica,
   - crear logical device,
   - crear un vertex buffer Vulkan para un triangulo + quad,
   - crear un index buffer Vulkan para triangulo + quad,
   - destruir buffers/device/instance sin crashear.

3) Nuevo backend experimental:
   JUEGO_RENDER_BACKEND=vulkan_triangle

   Este backend sigue dibujando el juego con OpenGL, pero al iniciar ejecuta
   el probe Vulkan de triangulo/quad. Asi el juego sigue jugable.

Como ejecutar normal:
   python main.py

Como probar esta etapa Vulkan:
   PowerShell:
      $env:JUEGO_RENDER_BACKEND="vulkan_triangle"; python main.py

   CMD:
      set JUEGO_RENDER_BACKEND=vulkan_triangle
      python main.py

Admin Hub:
- Muestra una linea nueva:
  VulkanPrep: probe / tri / buffers / devices

Notas:
- Esta etapa crea buffers Vulkan pero todavia no asigna memoria ni presenta imagen.
- La siguiente etapa deberia hacer memory allocation/map/upload real para el triangulo/quad.
