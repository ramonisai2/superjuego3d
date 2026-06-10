STAGE 31 PRE-W - VULKAN BACKEND PROBE

Esta etapa es el primer paso de Vulkan real, pero todavia NO renderiza el mundo con Vulkan.

Cambios:
- Nuevo archivo: motor_juegos/vulkan_bootstrap.py
- VulkanRenderBackend ahora hace un probe real:
  - intenta importar el paquete Python vulkan,
  - intenta crear una instancia Vulkan minima,
  - enumera GPUs compatibles,
  - destruye la instancia de prueba.
- create_render_backend ahora acepta:
  - opengl: modo jugable normal,
  - vulkan_probe: solo para probar si Vulkan arranca.
- main.py ahora lee la variable JUEGO_RENDER_BACKEND.

Uso normal:
python main.py

Prueba de Vulkan en PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_probe"; python main.py

Prueba de Vulkan en CMD:
set JUEGO_RENDER_BACKEND=vulkan_probe
python main.py

Nota:
- Si se usa vulkan_probe, el juego no entra a render jugable porque este backend solo prueba arranque.
- Si se usa JUEGO_RENDER_BACKEND=vulkan, el juego vuelve a OpenGL para no romperse.
- Para una prueba real puede requerirse instalar:
  pip install vulkan

Siguiente etapa recomendada:
Stage31 Pre-X - Vulkan abre ventana/surface/swapchain y limpia pantalla.
