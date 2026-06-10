STAGE32 VULKAN D - COMMAND BUFFER / COPY BUFFER PROBE

Objetivo:
- Avanzar un paso mas hacia Vulkan real sin romper el modo jugable OpenGL.
- Probar command pool, command buffer, vkCmdCopyBuffer y queue submit.

Modo normal:
python main.py

Modo experimental Vulkan D PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_command"; python main.py

Modo experimental Vulkan D CMD:
set JUEGO_RENDER_BACKEND=vulkan_command
python main.py

Que prueba:
- crea instancia Vulkan,
- detecta GPU,
- crea logical device,
- obtiene cola grafica,
- crea command pool,
- aloca command buffer,
- crea staging/source buffers,
- crea destination buffers,
- asigna y liga memoria,
- mapea staging y escribe bytes,
- graba vkCmdCopyBuffer,
- hace vkQueueSubmit,
- espera vkQueueWaitIdle,
- limpia recursos.

Que NO hace todavia:
- no renderiza el mundo con Vulkan,
- no crea pipeline grafico real,
- no presenta swapchain,
- no dibuja drawIndexed.

Admin Hub:
VulkanPrep ahora muestra cmd, cmdBuf, copy y sub.

Siguiente etapa sugerida:
Stage32 Vulkan E - pipeline grafico minimo + draw de triangulo/quad real.
