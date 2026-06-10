STAGE32 VULKAN H - SHADER MODULE + PIPELINE LAYOUT PROBE

Objetivo:
- Avanzar desde shaders GLSL/SPIR-V hacia objetos Vulkan reales.
- Mantener OpenGL como modo jugable.

Nuevo modulo:
- motor_juegos/vulkan_shader_module_probe.py

Que prueba:
1) Reutiliza Stage32 Vulkan G para escribir shaders GLSL y generar SPIR-V si existe glslangValidator o glslc.
2) Crea instancia Vulkan.
3) Detecta GPU y queue grafica.
4) Crea logical device.
5) Si hay SPIR-V valido, crea:
   - VkShaderModule vertex
   - VkShaderModule fragment
6) Crea un VkPipelineLayout minimo sin descriptor sets ni push constants.
7) Destruye recursos al terminar para evitar fugas.

Modo normal jugable:
python main.py

Modo experimental Vulkan H:
PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_shader_module"; python main.py

CMD:
set JUEGO_RENDER_BACKEND=vulkan_shader_module
python main.py

Admin Hub:
- VulkanPrep ahora muestra mods y layout:
  mods = shader modules creados
  layout = pipeline layout creado

Nota:
- Si no tienes glslangValidator o glslc, el probe puede fallar en SPIR-V.
- Eso no rompe el juego: OpenGL sigue siendo el render jugable.

Siguiente etapa recomendada:
Stage32 Vulkan I - render pass + graphics pipeline real usando esos shader modules.
