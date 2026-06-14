JUEGO 1.6 - Stage40 C
CHEAP LOGICAL CLOUDS

Objetivo
- Quitar sensacion de cielo vacio sin subir mucho el costo grafico.
- Agregar nubes baratas con movimiento por viento y color segun la hora.
- Mantenerlas como capa atmosferica: sin colision, sin recursos, sin chunks.

Cambios
- atmospheric_sky.py ahora dibuja dos capas de nubes con tarjetas translucidas.
- Las nubes cambian color/intensidad con dia, amanecer/atardecer y noche.
- main_render3d.py agrega sky_clouds_enabled y sky_clouds_drawn a render_stats.

Variables utiles
- JUEGO_CLOUDS_ENABLED=0 apaga las nubes.
- JUEGO_CLOUD_DENSITY controla cuantas nubes se ven.
- JUEGO_CLOUD_COUNT controla el conteo base.
- JUEGO_CLOUD_WIND_SPEED controla el movimiento.

Verificacion
- py_compile de atmospheric_sky.py, main_render3d.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Probar OpenGL estable.
- Mirar al cielo de dia y al atardecer.
- Si se ve saturado, bajar JUEGO_CLOUD_DENSITY.
- Si casi no se nota, subir JUEGO_CLOUD_COUNT o JUEGO_CLOUD_DENSITY.
