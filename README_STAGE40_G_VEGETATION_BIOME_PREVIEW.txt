JUEGO 1.6 - Stage40 G
VEGETATION BIOME PREVIEW

Objetivo
- Revisar la distribucion de arboles y sotobosque sin abrir el juego completo.
- Detectar rapido si un bioma queda vacio, saturado o raro.
- Mantener la revision visual barata usando solo numpy y PIL.

Archivos
- motor_juegos\vegetation_preview.py genera la imagen 2D.
- previsualizar_vegetacion_biomas.py ejecuta la herramienta.
- PREVISUALIZAR_VEGETACION_BIOMAS.bat la expone desde la raiz.
- INICIO_JUEGO.bat agrega una opcion de menu para usarla.

Salida
- juego3d_v1_5\previews\vegetation_biomes_preview.png

Lectura rapida
- Colores verdes grandes: familias de arboles por bioma.
- Colores de suelo: juncos, helechos, hierba alta, flor azul y maleza oscura.
- Azul: agua u orilla.

Notas
- Esta preview no agrega carga al runtime.
- Si se ajustan reglas de bioma o sotobosque, correr esta herramienta antes de probar OpenGL.
- OpenGL estable sigue siendo el camino jugable; Vulkan queda como laboratorio.
