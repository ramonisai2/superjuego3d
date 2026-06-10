STAGE 28 - SAVE WORLD + MENU + LANZADOR

Novedades:
1) Guardado de mundo en saves/world_save.json
   - Guarda semilla del mundo.
   - Guarda coordenadas X/Y/Z.
   - Guarda vida, hambre, stamina, inventario, yaw/pitch y modo de cámara.

2) Menu inicial
   - C: continuar mundo guardado.
   - N: empezar nueva partida con semilla aleatoria.
   - S: escribir una semilla manual.
   - ESC: salir.

3) Pantalla de carga
   - Muestra la semilla que se esta cargando.
   - Sirve para que el juego no entre de golpe a negro mientras prepara mundo.

4) Lanzador rapido
   - Windows: doble clic en LANZADOR_RAPIDO.bat
   - Alternativa: python lanzador_rapido.py

Controles dentro del juego:
- F5: guardar mundo actual.
- F9: recargar partida guardada si usa la misma semilla.
- V: cambiar primera/tercera persona.
- B: distancia de cámara.
- Q: fijar objetivo.
- TAB: cambiar objetivo.

Nota:
Si entras con Nueva Semilla, F9 no cargara una partida vieja de otra semilla.
Para volver a tu mundo guardado usa la opcion C del menu inicial.
