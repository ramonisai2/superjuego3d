JUEGO 1.6 - Stage40 I
SHRUB MUSHROOM GROUND LIFE

Objetivo
- Completar el suelo con arbustos y hongos sin crear geometria pesada.
- Usar modelos baratos que ya existian en el mesh.
- Dar pistas visuales de humedad, sequedad y bosque fresco.

Cambios
- environment.py agrega reglas de aparicion para:
  - hongo: humedad alta, temperatura fresca y rareza positiva.
  - arbusto_verde: humedad media/alta, temperatura viva y rareza positiva.
  - arbusto_seco: zonas secas, calidas y bajas.
- vegetation_preview.py muestra estos tres tipos en la leyenda y en la imagen.

Resultado esperado
- Bosques humedos tienen hongos ocasionales.
- Praderas y bordes verdes pueden tener arbustos.
- Zonas secas dejan de verse completamente planas.

Verificacion recomendada
- Ejecutar PREVISUALIZAR_VEGETACION_BIOMAS.bat.
- Revisar que hongos y arbustos aparezcan como detalle, no como alfombra.
- Si hay saturacion, bajar primero las probabilidades en environment.py.
