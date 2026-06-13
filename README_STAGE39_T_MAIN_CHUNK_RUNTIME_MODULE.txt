JUEGO 1.6 - Stage39 T - MAIN CHUNK RUNTIME MODULE

Objetivo
--------
Reducir main.py separando streaming, LOD, worker y compilacion de chunks.

Cambios
-------
- Se agrego juego3d_v1_5\main_chunk_runtime.py.
- MainChunkRuntime opera sobre mundo_chunks, mundo_chunks_simple, cola_de_peticiones, cola_lod_peticiones y chunks_pendientes por referencia.
- El runtime conserva la ruta stream bridge segura y la ruta legacy de anillo LOD/detalle.
- La comunicacion con el worker y la compilacion de chunks pendientes viven en MainChunkRuntime.
- main.py conserva el timer de streaming y llama los metodos del runtime.

Resultado de tamano
-------------------
- main.py queda en 658 lineas.
- main_chunk_runtime.py queda en 282 lineas.
- Ningun archivo principal supera 1000 lineas.

Verificacion recomendada
------------------------
py -m py_compile juego3d_v1_5\main.py juego3d_v1_5\main_chunk_runtime.py
cmd /c VERIFICAR_ESTRUCTURA_JUEGO.bat

Nota para Continue/Ollama
-------------------------
Si vas a tocar carga de chunks al moverse, LOD, stream bridge, worker, chunks pendientes, liberacion de chunks o compilacion/upload de mallas, abre primero:
juego3d_v1_5\main_chunk_runtime.py
