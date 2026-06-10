JUEGO 1.6 - STAGE38 C - ESTADO RAPIDO

Objetivo:
- Unir varias comprobaciones diarias en una sola pantalla.
- Confirmar estructura principal sin abrir el juego.
- Confirmar si hay Python valido para jugar y para previews.
- Refrescar el preset grafico recomendado cuando sea posible.

Cambios:
- Se agrega ESTADO_RAPIDO_JUEGO.bat en la raiz.
- INICIO_JUEGO.bat agrega la opcion 12.
- El reporte se guarda en juego3d_v1_5\logs\estado_rapido_juego.txt.
- version_info.py pasa a Stage38 C.

Uso recomendado:
- Abrir INICIO_JUEGO.bat.
- Elegir opcion 12 antes de una sesion larga.
- Si Python para juego falla, usar las opciones 6 o 7 del menu principal.
- Si faltan muestras de presets, probar low, balanced y high desde el menu de presets.

Nota:
- No se cambia gameplay.
- No se cambia el render principal.
- OpenGL estable sigue siendo la ruta jugable.
- No se genera ZIP.
