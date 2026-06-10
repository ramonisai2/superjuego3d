Stage36 S - PRESETS GRAFICOS

Objetivo
- Hacer ajustables las optimizaciones de distancia y LOD.
- Probar modo bajo para FPS y modo alto para ver mas lejos.
- Mostrar el preset activo en HUD.

Cambios
- Se agrega JUEGO_GRAPHICS_PRESET con valores low, balanced y high.
- El preset controla subdivisiones, LOD, distancia de entidades y niveles de detalle.
- El HUD muestra Graf: LOW/BALANCED/HIGH.
- El contador FPS se mueve a la esquina inferior derecha para no tapar badges.
- LANZAR_OPENGL.bat queda en balanced.
- Se agregan LANZAR_OPENGL_BAJO_FPS.bat y LANZAR_OPENGL_ALTO_DETALLE.bat.
- El lanzador grafico incluye botones OpenGL bajo FPS y OpenGL alto detalle.
- Si un preset viene mal escrito, el juego vuelve a balanced y el HUD muestra ese valor real.

Notas
- OpenGL estable sigue siendo la ruta jugable.
- Vulkan no se vuelve render principal.
- No cambia crafteo, mochila, IA ni escala boxel.
- No se genero ZIP.
