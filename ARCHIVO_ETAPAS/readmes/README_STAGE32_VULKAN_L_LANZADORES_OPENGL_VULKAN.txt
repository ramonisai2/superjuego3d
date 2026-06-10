STAGE32 VULKAN L - LANZADORES OPENGL / VULKAN

Objetivo:
- Poder iniciar el juego en OpenGL estable o Vulkan experimental sin escribir variables de entorno a mano.

Nuevos lanzadores en la carpeta principal:
- LANZAR_OPENGL.bat
- LANZAR_VULKAN_EXPERIMENTAL.bat
- LANZADOR_GRAFICO_RENDER.bat

Tambien estan dentro de juego3d_v1_5:
- LANZAR_OPENGL.bat
- LANZAR_VULKAN_EXPERIMENTAL.bat
- LANZADOR_GRAFICO_RENDER.bat
- lanzar_opengl.sh
- lanzar_vulkan_experimental.sh
- lanzador_grafico.py

Uso recomendado:
1) Para jugar normal:
   LANZAR_OPENGL.bat

2) Para probar Vulkan experimental:
   LANZAR_VULKAN_EXPERIMENTAL.bat

3) Para elegir con ventana:
   LANZADOR_GRAFICO_RENDER.bat

Notas:
- OpenGL sigue siendo el modo jugable estable.
- Vulkan todavía es experimental y puede volver a OpenGL o fallar si la PC/Python no tiene soporte completo.
- Esta etapa no busca renderizar todo el mundo con Vulkan; prepara una forma cómoda de probar ambas rutas.

Siguiente etapa recomendada:
Stage32 Vulkan M - integrar el modo Vulkan elegido del lanzador con reportes claros en pantalla/log.
