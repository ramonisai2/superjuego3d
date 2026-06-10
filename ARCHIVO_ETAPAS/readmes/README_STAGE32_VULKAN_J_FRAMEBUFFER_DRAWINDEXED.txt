STAGE32 VULKAN J - FRAMEBUFFER + COMMAND BUFFER + DRAWINDEXED

Objetivo:
- Mantener OpenGL como modo jugable.
- Agregar una prueba Vulkan offscreen más completa antes de presentar imagen en pantalla.

Nuevo módulo:
- motor_juegos/vulkan_framebuffer_draw_probe.py

Qué intenta validar:
1) Vulkan importado.
2) GPU Vulkan detectada.
3) SPIR-V generado/cargado desde los shaders de prueba.
4) VkShaderModule vertex/fragment.
5) VkRenderPass.
6) Imagen de color offscreen.
7) Memoria de imagen ligada.
8) VkImageView.
9) VkFramebuffer.
10) VkPipelineLayout.
11) VkGraphicsPipeline.
12) VkCommandPool y VkCommandBuffer.
13) vkCmdBeginRenderPass.
14) vkCmdBindPipeline.
15) vkCmdDrawIndexed grabado en command buffer.

Modo normal jugable:
python main.py

Modo experimental Vulkan J PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_framebuffer_draw"; python main.py

Modo experimental Vulkan J CMD:
set JUEGO_RENDER_BACKEND=vulkan_framebuffer_draw
python main.py

Notas:
- Todavía no presenta imagen Vulkan en pantalla.
- Es una prueba offscreen para asegurarnos de que ya existe la base de render pass/framebuffer/pipeline/drawIndexed.
- OpenGL sigue siendo el render jugable del mundo.
- La siguiente etapa recomendada es Stage32 Vulkan K: swapchain/framebuffers reales y primer present experimental.
