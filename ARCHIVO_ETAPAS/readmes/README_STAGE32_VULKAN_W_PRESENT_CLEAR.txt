STAGE32 VULKAN W - PRIMER DESTELLO

Objetivo:
- Preparar la secuencia del primer present real:
  acquire image -> clear pass -> submit -> present.
- Mantener OpenGL como modo jugable estable.
- Decidir si ya se puede intentar present real visible o si hace falta wrapper nativo/backend persistente.

Nuevos archivos:
- motor_juegos/vulkan_present_clear_probe.py
- diagnostico_present_clear.py
- DIAGNOSTICO_PRESENT_CLEAR.bat

Uso:
- Jugar estable:
  LANZAR_OPENGL.bat

- Diagnóstico acquire/clear/present:
  DIAGNOSTICO_PRESENT_CLEAR.bat

Lectura:
- real-next = la siguiente etapa puede intentar present real visible.
- native = se necesita wrapper nativo o backend Vulkan persistente.
- swap/fb/clear/present = la ruta está planificada.

Notas:
- Esta etapa no reemplaza el render OpenGL.
- Depende de que Stage32 U/V funcionen en la PC del usuario.
- La siguiente etapa lógica es Stage32 X: backend Vulkan persistente para clear visible.
