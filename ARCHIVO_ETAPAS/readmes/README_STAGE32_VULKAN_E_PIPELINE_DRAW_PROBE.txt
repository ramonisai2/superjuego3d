STAGE32 VULKAN E - PIPELINE GRAFICO MINIMO / DRAW PROBE

Objetivo:
- Preparar la siguiente pieza real para Vulkan: pipeline grafico minimo y draw simple.
- Mantener OpenGL como modo jugable estable.

Cambios:
- Se agrega motor_juegos/vulkan_pipeline_draw_probe.py
- El modulo prepara geometria neutral para triangulo + quad.
- Valida importacion del paquete vulkan.
- Intenta crear una instancia Vulkan y detectar GPU.
- Prepara el contrato de:
  - shader plan,
  - pipeline layout,
  - render pass plan,
  - pipeline plan,
  - draw plan.

Modo normal:
python main.py

Prueba manual del modulo:
python -m motor_juegos.vulkan_pipeline_draw_probe

Nota:
Esta etapa todavia NO dibuja el mundo con Vulkan. Sirve para preparar el paso siguiente:
Stage32 Vulkan F - render pass/swapchain compatible + primer clear/draw conectado al backend.
