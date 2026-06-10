JUEGO 1.6 - STAGE38 G - DIAGNOSTICO PYTHON

Objetivo:
- Saber por que no se encuentra un Python valido para jugar.
- Mostrar que paquetes faltan en cada candidato de Python.
- Evitar crear otra opcion en el menu principal.

Cambios:
- VERIFICAR_ENTORNO_JUEGO.bat agrega diagnostico detallado cuando falla Python de juego.
- El diagnostico prueba numpy, pygame, PyOpenGL y Pillow.
- ESTADO_RAPIDO_JUEGO.bat recomienda usar la opcion 3 para ver el detalle.
- version_info.py pasa a Stage38 G.

Lectura:
- Si un Python dice FALTAN: pygame, ese es el paquete que impide jugar.
- Si dice OK todos los paquetes, puede usarse como ruta local.
- Si dice No ejecuta o no existe, ese candidato no sirve en esa maquina.

Nota:
- No se instalan paquetes automaticamente.
- No se cambia gameplay.
- No se genera ZIP.
