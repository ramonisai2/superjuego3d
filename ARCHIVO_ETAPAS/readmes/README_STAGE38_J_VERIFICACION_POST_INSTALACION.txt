JUEGO 1.6 - STAGE38 J - VERIFICACION POST-INSTALACION

Objetivo:
- Confirmar que el Python reparado realmente pueda abrir el juego.
- Revisar el mismo Python destino despues de instalar dependencias.
- Evitar que una instalacion aparentemente correcta deje el juego sin abrir.

Cambios:
- INSTALAR_DEPENDENCIAS_JUEGO.bat verifica numpy, pygame y PyOpenGL despues de instalar.
- Si la verificacion falla, recomienda usar la opcion 3 para diagnostico detallado.
- Si la verificacion pasa, muestra que el Python destino esta listo para jugar.
- MOSTRAR_COMANDO_DEPENDENCIAS.bat y ESTADO_RAPIDO_JUEGO.bat aclaran esta verificacion.

Prueba:
- Se probo el flujo cancelando con NO.
- No se instalaron paquetes automaticamente.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
