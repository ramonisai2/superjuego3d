Stage40 X - FRAME RESCUE BUDGET

Objetivo
- Convertir la idea de "reusar el frame anterior" en un sistema seguro.
- Mantener jugador, camara, enemigos cercanos y HUD vivos aunque el FPS caiga.
- Quitar carga a lo lejano antes de congelar o degradar la experiencia jugable.

Cambios
- main_adaptive_quality.py ahora calcula rescue_level:
  - 0 OK
  - 1 SUAVE
  - 2 FUERTE
  - 3 CRITICO
- El rescate reduce radio, cantidad visible y construccion nueva de far_terrain_lod.py.
- El rescate reduce radio, cantidad visible y construccion nueva de forest_impostor_lod.py.
- En rescate fuerte/critico se puede pausar temporalmente la creacion de LOD lejanos.
- atmospheric_sky.py reduce la cantidad de nubes segun el nivel de rescate.
- main_render3d.py reporta frame_rescue_level/frame_rescue_label al HUD y logs.
- main_hud_render.py muestra el rescate en el panel F1.
- main_preset_logging.py guarda rescue/rescueLevel en las muestras de rendimiento.

Variables utiles
- JUEGO_FRAME_RESCUE: activa/desactiva el sistema. Default 1.
- JUEGO_FRAME_RESCUE_FPS: bajo este FPS promedio entra rescate fuerte. Default 30.
- JUEGO_FRAME_EMERGENCY_FPS: bajo este FPS promedio entra rescate critico. Default 22.
- JUEGO_ADAPTIVE_FPS_LOW: umbral general de ahorro adaptativo. Default 28.
- JUEGO_ADAPTIVE_FPS_HIGH: umbral de recuperacion. Default 48.

Lectura
- No redibuja literalmente el frame anterior completo.
- Si se hiciera literal, aumentaria input lag y se sentiria congelado al moverse.
- Esta etapa aplica la version segura: congela/reduce lo lejano y conserva lo jugable.
- Si el HUD marca mucho CRITICO, el siguiente paso es revisar chunks visibles, vertices y uploads.
