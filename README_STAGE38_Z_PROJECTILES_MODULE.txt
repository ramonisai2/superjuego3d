JUEGO 1.6 - Stage38 Z - PROJECTILES MODULE

Objetivo
- Continuar reduciendo main.py por responsabilidad.
- Sacar la fisica y render de proyectiles de piedra a un modulo de gameplay.
- Mantener main.py como coordinador, no como contenedor de todas las clases.

Cambios
- Nuevo archivo:
  juego3d_v1_5\game\projectiles.py

- Movido desde main.py:
  StoneProjectile
  spawn_stone_projectile
  update_stone_projectiles
  entity_alive

- main.py conserva:
  stone_projectiles como lista runtime
  llamadas para crear, actualizar y renderizar proyectiles

Resultado
- main.py baja un poco mas.
- El siguiente corte recomendado sigue siendo main_world_queries.py o z_targeting.py.
