Stage36 B - HUD IA NPC

Objetivo:
- Ver la telemetria de IA NPC dentro del juego cuando haga falta medir.
- Mantener la pantalla normal limpia.
- Ayudar a detectar si un modelo local afecta FPS.

Activacion:
- Definir JUEGO_DEBUG_NPC_AI=1 antes de lanzar el juego.

Cambios:
- Se agrega npc_ai_telemetry_lines().
- Se agrega draw_npc_ai_telemetry().
- Se agrega game/npc_ai_debug.py para formatear lineas sin depender de OpenGL.
- main.py dibuja el panel al final del HUD 2D.

Panel:
- Muestra requests, backend, cache, fallback y errores.
- Muestra tiempo promedio, maximo y ultimo en ms.
- Muestra cola pendiente/lista y entradas en cache.
- Muestra la ultima fuente y el ultimo error.

Notas:
- El panel esta apagado por defecto.
- No ejecuta IA por si mismo.
- No cambia el comportamiento de NPCs.
