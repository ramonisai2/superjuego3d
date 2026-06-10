JUEGO 1.6 - STAGE38 F - INSTALADOR CONSISTENTE

Objetivo:
- Hacer que las opciones de Python trabajen juntas.
- Evitar que el instalador ignore una ruta guardada.
- Mostrar de donde sale el Python destino antes de instalar.

Cambios:
- INSTALAR_DEPENDENCIAS_JUEGO.bat ahora carga JUEGO_PYTHON_LOCAL.bat si existe.
- El instalador muestra el origen de Python antes de pedir confirmacion.
- MOSTRAR_COMANDO_DEPENDENCIAS.bat aclara que el instalador usa la ruta guardada.
- ESTADO_RAPIDO_JUEGO.bat aclara lo mismo en la seccion SIGUIENTE PASO.

Prueba:
- Se probo el instalador cancelando con NO.
- No se instalaron paquetes durante la prueba.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
