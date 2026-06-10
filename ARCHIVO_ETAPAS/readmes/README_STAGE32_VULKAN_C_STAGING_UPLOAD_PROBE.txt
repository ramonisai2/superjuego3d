STAGE32 VULKAN C - STAGING / UPLOAD PROBE

Objetivo:
- Avanzar un paso mas hacia Vulkan real sin romper OpenGL.
- Probar buffers tipo staging HOST_VISIBLE/HOST_COHERENT.
- Probar vkMapMemory + escritura de bytes desde Python.

Modo normal jugable:
    python main.py

Modo experimental Vulkan staging/upload:
PowerShell:
    $env:JUEGO_RENDER_BACKEND="vulkan_staging"; python main.py

CMD:
    set JUEGO_RENDER_BACKEND=vulkan_staging
    python main.py

Cambios principales:
- Nuevo modulo: motor_juegos/vulkan_staging_upload_probe.py
- Nuevo backend experimental: opengl+vulkan_staging_upload_probe
- OpenGL sigue dibujando el juego.
- Vulkan intenta crear instancia, device, buffers, memoria, bind, map y escritura.
- Admin Hub ahora puede mostrar map/writeKB junto a VulkanPrep.

Importante:
- Esta etapa aun no ejecuta command buffers ni drawIndexed.
- No renderiza el mundo con Vulkan todavia.
- Sirve para validar que la PC/driver/Python pueden hacer upload basico.

Siguiente etapa sugerida:
- Stage32 Vulkan D: command pool + command buffer + copy buffer simulado/preparado.
