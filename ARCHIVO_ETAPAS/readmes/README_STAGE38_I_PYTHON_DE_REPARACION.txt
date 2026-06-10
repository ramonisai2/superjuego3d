JUEGO 1.6 - STAGE38 I - PYTHON DE REPARACION

Objetivo:
- Evitar instalar dependencias en el primer Python al azar.
- Elegir el Python que ya tenga mas paquetes del juego instalados.
- Mostrar que paquetes faltan antes de pedir confirmacion.

Cambios:
- INSTALAR_DEPENDENCIAS_JUEGO.bat ahora puntua candidatos de Python.
- Si no hay ruta local ni JUEGO_PYTHON, elige el candidato con mas paquetes presentes.
- El instalador muestra el origen y paquetes faltantes del Python destino.
- MOSTRAR_COMANDO_DEPENDENCIAS.bat recomienda usar el instalador inteligente.
- ESTADO_RAPIDO_JUEGO.bat aclara que la opcion 6 elige el mejor candidato.

Prueba:
- Se probo cancelando la instalacion.
- No se instalaron paquetes automaticamente.

Nota:
- No se cambia gameplay.
- No se cambia render.
- No se genera ZIP.
