Stage37 G - SESIONES NOMBRADAS

Objetivo:
- Hacer mas facil comparar low, balanced y high.
- Evitar adivinar de que lanzador salio cada corrida.
- Mantener OpenGL estable como ruta jugable principal.

Resultado:
- LANZAR_OPENGL.bat crea sesiones opengl_balanced_XXXX.
- LANZAR_OPENGL_BAJO_FPS.bat crea sesiones opengl_low_XXXX.
- LANZAR_OPENGL_ALTO_DETALLE.bat crea sesiones opengl_high_XXXX.
- Los tres lanzadores activan JUEGO_PRESET_SAMPLE_LOG=1.
- Los tres lanzadores usan py para arrancar el juego y el estado del render.

Flujo recomendado:
1. Ejecutar LIMPIAR_LOG_PRESETS_GRAFICOS.bat.
2. Probar LANZAR_OPENGL_BAJO_FPS.bat durante 1-2 minutos.
3. Probar LANZAR_OPENGL.bat durante 1-2 minutos.
4. Probar LANZAR_OPENGL_ALTO_DETALLE.bat durante 1-2 minutos.
5. Ejecutar ANALIZAR_PRESETS_GRAFICOS.bat para comparar todo.

Nota:
- ANALIZAR_PRESETS_ULTIMA_SESION.bat sirve para revisar solo la corrida mas reciente.
- Para comparar los tres presets, conviene usar ANALIZAR_PRESETS_GRAFICOS.bat.
