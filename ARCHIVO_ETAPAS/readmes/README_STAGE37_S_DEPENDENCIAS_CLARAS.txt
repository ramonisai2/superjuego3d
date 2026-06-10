Stage37 S - DEPENDENCIAS CLARAS

Objetivo:
- Dejar claro que paquetes necesita el juego.
- Mostrar el comando de instalacion sin ejecutar nada automaticamente.
- Conectar la ayuda desde el menu de presets.

Resultado:
- Se agrega requirements_juego.txt.
- Se agrega MOSTRAR_COMANDO_DEPENDENCIAS.bat.
- VERIFICAR_ENTORNO_JUEGO.bat sugiere la ayuda si falta Python valido.
- PROBAR_PRESETS_OPENGL.bat agrega la opcion 11.
- setup.cfg incluye Pillow para herramientas de preview.

Nota:
- No instala dependencias automaticamente.
- No abre el juego.
- No crea ZIP.
