STAGE35 A - CUERPO NPC

Objetivo:
- Empezar la base de NPCs vivos por sistemas internos, no por frases.
- Dar a cada NPC necesidades reales y baratas de actualizar.
- Preparar datos que luego podran alimentar memoria, decisiones y un modelo local compacto.

Cambios:
- Cada NPC ahora tiene:
  - health / max_health
  - food
  - water
  - energy
  - security
  - social
  - stress
  - current_need
  - intent
- Las necesidades se actualizan con el tiempo mediante update_needs().
- El movimiento usa energy para bajar un poco la velocidad si el NPC esta cansado.
- needs_snapshot() entrega un resumen listo para debug, memoria o dialogo futuro.

Notas:
- No se cambiaron nombres, titulos, profesiones, hostilidad ni atributos especiales.
- No se cambio el sistema de conversaciones todavia.
- No se conecto ningun modelo de lenguaje en esta etapa.
- No se hizo ZIP.
