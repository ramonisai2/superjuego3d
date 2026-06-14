JUEGO 1.6 - Stage40 A
REAL FAR TERRAIN LOD

Objetivo
- Reducir la sensacion de mundo plano/vacio sin usar montanas falsas.
- Dibujar relieve lejano real basado en el mismo seed y la misma generacion del mundo.
- Mantener el costo bajo con tiles de baja resolucion y cache OpenGL.

Cambios
- Nuevo modulo: juego3d_v1_5\motor_juegos\far_terrain_lod.py
- main_render3d.py dibuja el relieve lejano despues del cielo y antes de chunks normales.
- main.py pasa SEMILLA_MUNDO al render 3D.

Reglas
- No hay colision, recursos ni decoraciones en el relieve lejano.
- Si el jugador se acerca, los chunks normales reemplazan visualmente ese fondo.
- El sistema no inventa montanas: usa calculate_runtime_terrain_properties_with_fields().

Variables utiles
- JUEGO_FAR_TERRAIN_ENABLED=0 apaga el sistema.
- JUEGO_FAR_TERRAIN_RADIUS controla cuantas capas lejanas se ven.
- JUEGO_FAR_TERRAIN_SUBDIVISIONS controla detalle por tile.
- JUEGO_FAR_TERRAIN_BUILD_PER_FRAME controla cuantos tiles nuevos se compilan por frame.
- JUEGO_FAR_TERRAIN_TILE_SIZE controla el tamano de cada tile lejano.

Verificacion
- py_compile de main.py, main_render3d.py, far_terrain_lod.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Abrir en OpenGL estable.
- Subir a una meseta o zona alta.
- Mirar el horizonte mientras se camina.
- Confirmar que el relieve lejano no desaparece de golpe al acercarse.
