JUEGO 1.6 - STAGE38 L - SELECTOR DE REPARACION

Objetivo:
- Reutilizar la eleccion inteligente de Python fuera del instalador.
- Mostrar en estado rapido el mismo comando que usaria la opcion 6.
- Reducir duplicacion entre scripts.

Cambios:
- Se agrega SELECCIONAR_PYTHON_REPARACION.bat.
- INSTALAR_DEPENDENCIAS_JUEGO.bat usa ese selector.
- ESTADO_RAPIDO_JUEGO.bat revisa ese selector y muestra comando exacto elegido por opcion 6.
- El estado rapido tambien muestra origen del Python destino y paquetes faltantes.

Prueba:
- Se probo instalador cancelando con NO.
- Se probo estado rapido con el comando exacto.
- No se instalaron paquetes automaticamente.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
