STAGE33 R - PRESUPUESTOS DEL PUENTE

Objetivo:
- Hacer configurable el puente seguro sin tocar codigo.
- Probar perfiles safe, balanced y aggressive.
- Mantener OpenGL legacy como ruta estable.

Variables:
- JUEGO_STREAM_BRIDGE_PRESET=safe|balanced|aggressive
- JUEGO_STREAM_DETAIL_RADIUS
- JUEGO_STREAM_LOD_RADIUS
- JUEGO_STREAM_MAX_REQUESTS

Perfiles:
- safe: detalle 1, LOD 2, max requests 2.
- balanced: detalle 1, LOD 2, max requests 3.
- aggressive: detalle 2, LOD 3, max requests 4.

Uso:
- Ver presupuesto actual:
  LANZAR_STREAM_BRIDGE_BUDGET_PROBE.bat

- OpenGL + puente seguro safe:
  LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat

- OpenGL + puente seguro balanced:
  LANZAR_OPENGL_STREAM_BRIDGE_BALANCED.bat

- OpenGL + puente seguro aggressive:
  LANZAR_OPENGL_STREAM_BRIDGE_AGGRESSIVE.bat

Recomendacion:
- Probar safe primero.
- Si va fluido y sin huecos, probar balanced.
- Aggressive solo si hay buen rendimiento.

Siguiente etapa recomendada:
Stage33 S - comparar logs por preset y elegir valor por defecto.
