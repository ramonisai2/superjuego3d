STAGE 30 FIX Q - NADO / ENTRADA AL LAGO

Problema encontrado por el log:
- El sistema detectaba agua con HEIGHT_WATER_SURFACE_USED.
- Pero la superficie del agua subia la altura virtual del terreno.
- El bloqueo de pendientes lo interpretaba como una pared y lanzaba STEEP_SLOPE_BLOCKED.
- Resultado: el jugador no podia entrar al lago y no activaba bien el nado.

Correccion:
- El movimiento ahora consulta si el siguiente paso cae en agua.
- Si el siguiente punto es agua, la subida hacia la superficie del lago NO cuenta como pendiente bloqueada.
- Se registra WATER_ENTRY_SLOPE_ALLOWED cuando permite entrar al agua aunque haya salto vertical de superficie.
- El modo nado/flotacion sigue controlado por el HUD/contexto del mundo.

Que probar:
- Caminar hacia el lago de frente.
- Ver si aparece NADANDO en el HUD.
- Revisar que STEEP_SLOPE_BLOCKED ya no se repita al borde del agua.
- Revisar que las mesetas de tierra sigan bloqueando subidas muy verticales.
