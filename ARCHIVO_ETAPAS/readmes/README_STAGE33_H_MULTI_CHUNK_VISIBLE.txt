STAGE33 H - VARIOS CHUNKS VISIBLES

Objetivo:
- Tomar el anillo de chunks MeshData de Stage33 G.
- Preparar un frame experimental con varios drawIndexed.
- Encadenar:
  multi chunk
  begin render pass
  drawIndexed por chunk visible
  end render pass
  present
- Mantener OpenGL como modo estable.

Nuevos archivos:
- motor_juegos/vulkan_multi_chunk_visible_probe.py
- lanzar_multi_chunk_visible_vulkan.py
- diagnostico_multi_chunk_visible_vulkan.py
- LANZAR_MULTI_CHUNK_VISIBLE_VULKAN.bat
- DIAGNOSTICO_MULTI_CHUNK_VISIBLE_VULKAN.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Probar varios chunks visibles:
  LANZAR_MULTI_CHUNK_VISIBLE_VULKAN.bat

- Diagnostico:
  DIAGNOSTICO_MULTI_CHUNK_VISIBLE_VULKAN.bat

Lectura:
- multi = anillo de chunks preparado.
- rp-loop = render pass preparado para varios chunks.
- cmd = command buffer/paquete de frame preparado.
- draw-loop = loop de drawIndexed por chunk preparado.
- present = present posterior al multi chunk preparado.
- multiVisibleOK = varios chunks visibles listos sin bloqueo nativo reportado.
- native = todavia hace falta wrapper nativo/backend Vulkan persistente real para present confiable.

Importante:
- Vulkan sigue siendo experimental.
- OpenGL sigue siendo la ruta jugable estable.
- Esta etapa no afirma que Vulkan ya renderiza el juego completo.

Siguiente etapa recomendada:
Stage33 I - anillo de chunks centrado en jugador/camara.
