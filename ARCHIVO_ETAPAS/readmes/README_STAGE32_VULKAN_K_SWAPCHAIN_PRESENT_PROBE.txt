STAGE32 VULKAN K - SWAPCHAIN / PRESENT PROBE

Objetivo:
- Avanzar hacia Vulkan real preparando la etapa de surface/swapchain/present.
- Mantener OpenGL como ruta jugable estable.
- Agregar un probe seguro que detecta Vulkan y genera el plan de present sin crashear.

Nuevo modulo:
- juego3d_v1_5/motor_juegos/vulkan_swapchain_present_probe.py

Que prueba:
- importar vulkan
- crear VkInstance
- detectar GPU
- planificar:
  - surface
  - swapchain
  - framebuffers por imagen
  - acquire next image
  - queue present

Importante:
- Esta etapa todavia NO presenta imagen Vulkan en pantalla.
- Crear un VkSurfaceKHR real desde pygame/SDL en Python depende de bindings/extensiones de plataforma.
- Por eso esta build prepara la frontera segura antes del primer present real.

Prueba manual:
python -m motor_juegos.vulkan_swapchain_present_probe

Modo normal jugable:
python main.py

Siguiente etapa recomendada:
Stage32 Vulkan L - integracion SDL/surface real o ventana dedicada Vulkan para present real.
