JUEGO 1.6 - Stage39 N - ENVIRONMENT SPLIT MODULES

Objetivo
--------
Bajar motor_juegos\environment.py por debajo de 1000 lineas sin cambiar la API publica del mundo.

Cambios
-------
- Se agrego motor_juegos\world_detail.py.
- Se agrego motor_juegos\chunk_mesh_builder.py.
- environment.py conserva terreno, agua, cache de altura, render legacy, cielo, LOD y culling.
- world_detail.py contiene presets/densidades de pasto, decoracion, rocas, arboles oasis y planos impostores.
- chunk_mesh_builder.py convierte quads, grass, rocks, deco y water a ChunkMeshData neutral.

Resultado de tamano
-------------------
- main.py: 989 lineas.
- motor_juegos\environment.py: 963 lineas.
- game\npc_manager.py: 452 lineas.
- Ningun archivo principal supera la meta de 1000 lineas segun auditar_tamano_py.py.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\motor_juegos\environment.py juego3d_v1_5\motor_juegos\world_detail.py juego3d_v1_5\motor_juegos\chunk_mesh_builder.py juego3d_v1_5\main.py
py auditar_tamano_py.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar densidad, impostores, perfiles low/balanced/high o variables JUEGO_GRASS_*:
motor_juegos\world_detail.py

Si vas a tocar como se transforman rocas, arboles, plantas o agua a MeshData:
motor_juegos\chunk_mesh_builder.py

Si vas a tocar altura, agua procedural, contexto de mundo, skybox, LOD simple o culling:
motor_juegos\environment.py
