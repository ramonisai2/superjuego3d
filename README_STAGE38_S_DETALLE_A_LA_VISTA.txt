JUEGO 1.6 - Stage38 S - DETALLE A LA VISTA

Objetivo:
- Bajar el costo de los chunks detallados cuando quedan detras de la camara.
- Mantener LOD/fondo visible para evitar huecos.
- Medir si el ajuste baja visibleDetailVerts sin romper la lectura del mapa.

Cambios:
- Los chunks LOD y los chunks detail ya no usan exactamente el mismo culling.
- Cada preset define:
  - detail_render_extra
  - detail_near_keep
  - detail_back_margin
- El HUD F1 muestra detail: distancia/near_keep.
- El log de presets agrega:
  - detailDist
  - detailNear
  - detailBack
- El reporte muestra detailDist/detailNear en peores muestras nuevas.

Valores base:
- low: detail extra 0.90, near keep 1.05 chunks, back margin 0.02.
- balanced: detail extra 1.05, near keep 1.25 chunks, back margin 0.08.
- high: detail extra 1.25, near keep 1.55 chunks, back margin 0.14.

Override manual:
- set JUEGO_DETAIL_CHUNK_RENDER_EXTRA=1.80
- set JUEGO_DETAIL_CHUNK_NEAR_KEEP=2.05
- set JUEGO_DETAIL_CHUNK_BACK_MARGIN=0.28

Lectura:
- Si visibleDetailVerts baja y no aparecen huecos, el ajuste ayuda.
- Si al girar aparece popping molesto, subir JUEGO_DETAIL_CHUNK_NEAR_KEEP.
- Si lodV sigue dominando, el siguiente frente es horizonte/LOD.

Regla:
- OpenGL estable sigue siendo el modo jugable.
- Vulkan no cambia de estado.
- No se hace ZIP.
