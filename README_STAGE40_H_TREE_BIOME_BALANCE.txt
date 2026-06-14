JUEGO 1.6 - Stage40 H
TREE BIOME BALANCE

Objetivo
- Evitar que casi todos los bosques cercanos se lean como roble.
- Hacer visibles abedules y cipreses sin convertirlos en arboles comunes.
- Mantener pino, sauce, roble y arbol seco con identidad clara.

Cambios
- biomes.py abre el rango de sauce en humedad/orilla.
- biomes.py abre el rango de cipres en bosque humedo, fresco y raro.
- biomes.py abre el rango de abedul en bosque fresco claro.

Resultado esperado
- Roble sigue siendo el arbol comun.
- Sauce aparece mas cerca de humedad y zonas bajas.
- Pino sigue asociado a altura o frio.
- Abedul deja de ser casi invisible.
- Cipres marca mejor las zonas de bosque oscuro humedo.

Verificacion recomendada
- Ejecutar PREVISUALIZAR_VEGETACION_BIOMAS.bat.
- Revisar juego3d_v1_5\previews\vegetation_biomes_preview.png.
- Si abedul o cipres dominan demasiado, cerrar sus rangos antes de tocar densidad.
