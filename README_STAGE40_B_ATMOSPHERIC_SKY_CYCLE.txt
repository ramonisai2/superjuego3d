JUEGO 1.6 - Stage40 B
ATMOSPHERIC SKY CYCLE

Objetivo
- Quitar sensacion de cielo muerto/vacio.
- Agregar ciclo dia/noche barato con sol, luna, estrellas y fog atmosferico.
- Mantener OpenGL estable como camino jugable.

Cambios
- Nuevo modulo: juego3d_v1_5\motor_juegos\atmospheric_sky.py
- environment.draw_procedural_skybox() ahora delega al cielo atmosferico.
- main_render3d.py usa el color de fog del cielo actual.
- render_stats expone sky_hour, sky_daylight y sky_night.

Variables utiles
- JUEGO_DAY_NIGHT_ENABLED=0 congela el cielo en dia.
- JUEGO_DAY_LENGTH_SECONDS controla duracion del ciclo completo.
- JUEGO_DAY_START_HOUR controla la hora inicial al abrir el juego.

Verificacion
- py_compile de atmospheric_sky.py, environment.py, main_render3d.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Abrir OpenGL estable.
- Mirar cielo/horizonte al iniciar.
- Probar temporalmente JUEGO_DAY_LENGTH_SECONDS=180 para ver transiciones mas rapido.
- Confirmar que el fog combina con el cielo y que de noche no queda todo ilegible.
