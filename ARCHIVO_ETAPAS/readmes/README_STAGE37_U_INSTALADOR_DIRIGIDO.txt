Stage37 U - INSTALADOR DIRIGIDO

Objetivo:
- Evitar instalar dependencias en el Python equivocado.
- Respetar JUEGO_PYTHON cuando se define una ruta fija.
- Mostrar el Python destino y el comando antes de instalar.

Resultado:
- INSTALAR_DEPENDENCIAS_JUEGO.bat usa JUEGO_PYTHON si existe.
- Si JUEGO_PYTHON no existe, usa py como respaldo.
- El instalador muestra sys.executable del destino.
- El instalador muestra el comando pip exacto antes de pedir SI.
- MOSTRAR_COMANDO_DEPENDENCIAS.bat explica el flujo con JUEGO_PYTHON.

Nota:
- No instala nada sin escribir SI.
- No abre el juego.
- No crea ZIP.
