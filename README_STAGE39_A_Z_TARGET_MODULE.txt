JUEGO 1.6 - Stage39 A - Z TARGET MODULE

Objetivo
- Continuar reduciendo main.py por responsabilidad.
- Sacar la logica de lock-on/Z-targeting a un modulo propio.
- Mantener el comportamiento visible actual: el sistema queda reservado, no reactivado automaticamente.

Cambios
- Nuevo archivo:
  juego3d_v1_5\game\z_targeting.py

- Movido desde main.py:
  find_z_target
  z_target_candidates
  ZTargetState

- Limpieza en main.py:
  Se removieron funciones de Z-targeting que estaban definidas pero no llamadas.
  Se removieron banderas globales de boton que ya no se usaban.

Nota
- El HUD todavia conserva z_target/z_target_type como variables runtime.
- Si se reactiva el lock-on, conviene hacerlo usando ZTargetState desde game\z_targeting.py.
