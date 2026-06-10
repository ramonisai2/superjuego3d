STAGE32 VULKAN G - SHADER / SPIR-V PROBE

Objetivo:
- Preparar shaders minimos GLSL 450 para Vulkan.
- Probar si la PC tiene herramientas para compilar GLSL a SPIR-V.
- Mantener OpenGL como modo jugable normal.

Archivos nuevos:
- juego3d_v1_5/motor_juegos/vulkan_shader_probe.py
- juego3d_v1_5/assets/shaders/vulkan_probe/probe.vert
- juego3d_v1_5/assets/shaders/vulkan_probe/probe.frag

Modo normal jugable:
python main.py

Modo experimental Vulkan G en PowerShell:
$env:JUEGO_RENDER_BACKEND="vulkan_shader"; python main.py

Modo experimental en CMD:
set JUEGO_RENDER_BACKEND=vulkan_shader
python main.py

Que valida:
- paquete vulkan disponible,
- instancia Vulkan minima,
- GPUs detectadas,
- fuentes shader listas,
- deteccion de glslangValidator o glslc,
- generacion opcional de probe.vert.spv y probe.frag.spv.

Notas:
- Si no tienes glslangValidator/glslc, la etapa no debe romper el juego.
- OpenGL sigue como render jugable.
- La siguiente etapa logica es Stage32 Vulkan H: shader modules reales + pipeline layout real.
