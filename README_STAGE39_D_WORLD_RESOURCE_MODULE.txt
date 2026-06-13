JUEGO 1.6 - Stage39 D - WORLD RESOURCE MODULE

Objetivo
- Seguir reduciendo main.py para trabajar mejor con LLM local.
- Separar indices de piedra, madera, fibra y colliders de roca.
- Mantener la recoleccion basica fuera del bucle principal.

Cambios
- Se agrego juego3d_v1_5\main_resources.py.
- WorldResourceRuntime administra recursos por chunk, cooldowns de pickup y colisionadores de roca.
- main.py delega add/remove de recursos y pickup del jugador a resource_runtime.

Notas
- No cambia la ruta jugable: OpenGL estable sigue recomendado.
- No se genero ZIP.
