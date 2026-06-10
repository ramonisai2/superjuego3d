Stage37 X - CONFIG LOCAL PRIVADA

Objetivo:
- Evitar que rutas locales de Python entren al proyecto compartido.
- Mantener logs y previews como salidas temporales.
- Proteger configuraciones propias de cada PC.

Resultado:
- .gitignore ignora JUEGO_PYTHON_LOCAL.bat.
- .gitignore ignora juego3d_v1_5/logs/.
- .gitignore ignora juego3d_v1_5/previews/.
- version_info.py queda en Stage37 X.

Nota:
- No se borra ningun archivo existente.
- No instala dependencias.
- No abre el juego.
- No crea ZIP.
