STAGE 30 FIX R - REGLA DE ESCALADO 3X SALTO

Cambios principales:
- El bloqueo de pendientes ahora usa una regla basada en la altura real del salto.
- La altura de salto se estima con: jump_height = jump_force^2 / (2 * gravedad).
- El jugador puede subir/deslizarse por desniveles hasta aprox. 3 veces su altura de salto.
- Si el desnivel supera ese limite, se bloquea como risco/meseta y el jugador debe rodear o buscar una rampa natural.
- La entrada al agua sigue siendo excepcion: si el siguiente punto es agua, no se bloquea como pared.

Logs nuevos:
- CLIMB_LIMIT_BLOCKED: cuando una pared/meseta supera el limite escalable.
- WATER_ENTRY_SLOPE_ALLOWED: cuando se permite entrar al agua aunque la superficie virtual suba.

Que probar:
1) Colinas normales: deberian poder subirse.
2) Mesetas altas: no deberian escalarse de frente si superan el limite.
3) Lagos: deberias poder entrar y activar nado.
4) Si una meseta no se puede escalar, rodearla deberia permitir encontrar una subida natural.
