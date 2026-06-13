JUEGO 1.6 - Stage38 X - CONTEXTO LLM

Objetivo
- Ayudar a trabajar con LLM local, Ollama, VS Code y Continue.
- Detectar archivos Python demasiado grandes para ventanas de contexto pequenas.
- Planear divisiones por responsabilidad sin romper imports existentes.

Resultado actual
- main.py supera 1000 lineas.
- game\npc_manager.py supera 1000 lineas.
- motor_juegos\environment.py supera 1000 lineas.

Herramienta nueva
- AUDITAR_TAMANO_PY.bat
- juego3d_v1_5\auditar_tamano_py.py
- Reporte: juego3d_v1_5\logs\tamano_py_report.txt

Regla recomendada
- Intentar que archivos principales nuevos queden por debajo de 1000 lineas.
- No partir por partir: cada modulo debe tener una responsabilidad clara.
- Mantener fachadas pequenas para conservar imports antiguos.
- Mover un bloque por etapa, compilar, probar y recien despues seguir.

Primeros candidatos
- main.py:
  main_config.py, main_world_queries.py, main_runtime_state.py, main_rendering.py, main_loop.py

- game\npc_manager.py:
  npc_identity.py, npc_needs.py, npc_ai.py, npc_render.py

- motor_juegos\environment.py:
  terrain_runtime.py, world_detail.py, water_surface.py, chunk_mesh_builder.py
