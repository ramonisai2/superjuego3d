JUEGO 1.6 - Stage40 D
DARK FOREST IMPOSTORS

Objetivo
- Dar masa visual a bosques lejanos sin llenar el mundo de arboles reales.
- Evitar el horizonte vacio y reforzar el "bosque oscuro que no deja ver atras".
- Mantener una regla honesta: se colocan por seed, humedad, altura, temperatura y bioma.

Cambios
- Nuevo modulo: juego3d_v1_5\motor_juegos\forest_impostor_lod.py
- main_render3d.py dibuja estos impostores despues del relieve lejano y antes de chunks normales.
- render_stats expone forest_impostor_enabled, forest_impostor_tiles_visible y forest_impostor_trees_drawn.

Reglas
- No hay colision, recursos ni IA.
- Los chunks cercanos siguen siendo los que mandan cuando el jugador se acerca.
- No se dibujan en desiertos/calor seco salvo que el bioma real lo justifique.

Variables utiles
- JUEGO_FOREST_IMPOSTORS_ENABLED=0 apaga esta capa.
- JUEGO_FOREST_IMPOSTOR_DENSITY controla densidad.
- JUEGO_FOREST_IMPOSTOR_RADIUS controla distancia de anillos visibles.
- JUEGO_FOREST_IMPOSTOR_SAMPLES controla muestras por tile.
- JUEGO_FOREST_IMPOSTOR_BUILD_PER_FRAME controla compilacion por frame.

Verificacion
- py_compile de forest_impostor_lod.py, main_render3d.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Abrir OpenGL estable.
- Buscar zonas humedas/boscosas.
- Mirar a distancia media/lejana y caminar hacia la masa de bosque.
- Si se ve demasiado muro, bajar JUEGO_FOREST_IMPOSTOR_DENSITY.
