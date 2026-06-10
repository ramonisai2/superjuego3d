JUEGO 1.6 - STAGE38 H - REQUISITO OPENGL

Objetivo:
- Evitar aceptar un Python que tenga pygame pero no PyOpenGL.
- Alinear los chequeos con requirements_juego.txt.
- Mantener previews separadas, porque no necesitan abrir OpenGL.

Cambios:
- SELECCIONAR_PYTHON_JUEGO.bat ahora exige numpy, pygame y PyOpenGL por defecto.
- VERIFICAR_ENTORNO_JUEGO.bat usa el mismo requisito para abrir el juego.
- ESTADO_RAPIDO_JUEGO.bat reporta PyOpenGL como parte del requisito de juego.
- CONFIGURAR_PYTHON_JUEGO.bat solo guarda rutas que puedan importar PyOpenGL.
- ADMINISTRAR_PYTHON_JUEGO.bat prueba tambien PyOpenGL en la ruta guardada.
- ESTADO_RAPIDO_JUEGO.bat usa checks directos para evitar avisos de etiquetas internas.
- ADMINISTRAR_PYTHON_JUEGO.bat sale si recibe entrada vacia.

Nota:
- No se instalan paquetes automaticamente.
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
