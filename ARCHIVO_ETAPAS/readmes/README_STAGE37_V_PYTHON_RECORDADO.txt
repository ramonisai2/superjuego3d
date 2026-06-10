Stage37 V - PYTHON RECORDADO

Objetivo:
- Evitar escribir JUEGO_PYTHON cada vez.
- Guardar una ruta local para los lanzadores.
- Mantener el selector automatico como respaldo.

Resultado:
- Se agrega CONFIGURAR_PYTHON_JUEGO.bat.
- El asistente valida numpy y pygame antes de guardar.
- Si valida, crea JUEGO_PYTHON_LOCAL.bat.
- SELECCIONAR_PYTHON_JUEGO.bat lee JUEGO_PYTHON_LOCAL.bat automaticamente.
- PROBAR_PRESETS_OPENGL.bat agrega la opcion 13.

Nota:
- JUEGO_PYTHON_LOCAL.bat no se crea hasta que el usuario configure una ruta.
- No instala dependencias.
- No abre el juego.
- No crea ZIP.
