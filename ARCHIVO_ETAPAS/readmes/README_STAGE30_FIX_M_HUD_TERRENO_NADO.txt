STAGE 30 FIX M - HUD DE TERRENO + NADO/FLOTACION

Objetivo:
- Poder depurar el mundo en pantalla: saber si estas en un lago, orilla/oasis,
  meseta, depresion o plano normal.
- Activar modo nado cuando el jugador entra en un lago.

Cambios:
1) HUD nuevo de terreno:
   - Zona actual: lago, orilla/oasis, meseta, depresion, plano normal.
   - Bioma aproximado.
   - Capa de altura: baja, media o alta.
   - Profundidad del agua si estas dentro de lago.
   - Fuerza de cuenca/meseta si estas fuera del agua.

2) Diagnostico procedural:
   - Se agregó env.get_world_context_at(x, z, seed).
   - Usa el mismo generador de terreno, agua, cuencas y mesetas para reportar el estado.

3) Modo nado/flotacion:
   - Si el punto actual cae dentro de agua, el jugador activa is_swimming.
   - La altura del jugador cambia a una flotacion sobre la superficie.
   - Hay un bob suave para simular flotar.
   - La velocidad baja en agua.

Notas:
- Esto es preliminar: sirve para depurar lagos, capas y agua.
- Aun no es animacion completa de brazos/piernas, pero ya distingue el modo de movimiento.
