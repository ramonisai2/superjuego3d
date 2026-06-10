STAGE32 VULKAN F - DRAW PROBE / PIPELINE INTEGRADO

Objetivo:
- Avanzar desde command/copy/pipeline plan hacia un probe integrado de drawIndexed.
- Mantener OpenGL como modo jugable.
- Probar que la ruta Vulkan ya puede preparar:
  - instancia,
  - GPU,
  - queue grafica,
  - logical device,
  - plan de render pass,
  - plan de framebuffer,
  - plan de pipeline layout,
  - plan de graphics pipeline,
  - plan de command buffer,
  - plan de draw indexed.

Nuevo modulo:
- motor_juegos/vulkan_draw_probe.py

Nuevo backend experimental:
- JUEGO_RENDER_BACKEND=vulkan_draw

Uso normal:
python main.py

Uso experimental en PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_draw"; python main.py

Uso experimental en CMD:
set JUEGO_RENDER_BACKEND=vulkan_draw
python main.py

Notas importantes:
- Esta etapa todavia NO presenta imagen Vulkan en pantalla.
- OpenGL sigue siendo el render jugable.
- En Python, surface/swapchain/presentacion real depende de extensiones de ventana/plataforma.
- Esta etapa deja preparada la frontera para la siguiente fase: conectar swapchain real + shaders SPIR-V + render pass compatible.

Admin Hub:
La linea VulkanPrep ahora puede mostrar:
- draw: probe de draw integrado
- rp: render pass plan
- pipe: pipeline plan
- idx: drawIndexed plan

Siguiente etapa sugerida:
Stage32 Vulkan G - shaders SPIR-V minimos + pipeline real experimental.
