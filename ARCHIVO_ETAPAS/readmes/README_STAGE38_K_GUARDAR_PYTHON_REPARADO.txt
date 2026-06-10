JUEGO 1.6 - STAGE38 K - GUARDAR PYTHON REPARADO

Objetivo:
- Evitar repetir busqueda de Python despues de reparar dependencias.
- Guardar el Python destino solo si ya paso verificacion de juego.
- Mantener la decision bajo control del usuario.

Cambios:
- INSTALAR_DEPENDENCIAS_JUEGO.bat pregunta si debe guardar la ruta despues de verificarla.
- Si el usuario escribe GUARDAR, se crea JUEGO_PYTHON_LOCAL.bat.
- Si no se guarda, se puede usar la opcion 7 mas tarde.
- MOSTRAR_COMANDO_DEPENDENCIAS.bat y ESTADO_RAPIDO_JUEGO.bat explican el nuevo cierre.

Prueba:
- Se probo el camino de cancelacion con NO.
- No se instalaron paquetes automaticamente.
- No se creo JUEGO_PYTHON_LOCAL.bat durante la prueba.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
