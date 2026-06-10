Stage38 B - ESTRUCTURA VERIFICABLE

Objetivo:
- Confirmar que la limpieza no escondio piezas importantes.
- Revisar archivos y carpetas clave desde un .bat.
- Conectar esa verificacion al menu principal.

Resultado:
- Se agrega VERIFICAR_ESTRUCTURA_JUEGO.bat.
- INICIO_JUEGO.bat agrega la opcion 11.
- El verificador revisa launchers, LEEME, requirements, main.py, motor_juegos, assets y ARCHIVO_ETAPAS.
- Si falta algo, lo marca como FALTA y devuelve codigo de error.

Nota:
- No abre el juego.
- No instala dependencias.
- No borra ni mueve archivos.
- No crea ZIP.
