Stage37 Q - PYTHON SEGURO

Objetivo:
- Evitar que los lanzadores usen un Python sin dependencias.
- Detectar numpy/pygame antes de abrir el juego.
- Mostrar un error claro si falta el entorno correcto.

Resultado:
- Se agrega SELECCIONAR_PYTHON_JUEGO.bat.
- LANZAR_OPENGL.bat usa el selector.
- LANZAR_OPENGL_BAJO_FPS.bat usa el selector.
- LANZAR_OPENGL_ALTO_DETALLE.bat usa el selector.
- LANZAR_OPENGL_RECOMENDADO.bat usa el selector.
- PROBAR_PRESETS_OPENGL.bat usa el selector al abrir presets.
- LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat usa el selector.
- PREVISUALIZAR_TERRENO.bat usa el selector con numpy/PIL.

Nota:
- El selector respeta JUEGO_PYTHON si el usuario quiere forzar una ruta.
- No instala dependencias.
- No crea ZIP.
