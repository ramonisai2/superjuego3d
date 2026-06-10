Stage36 F - GOLPE BOXEL

Objetivo:
- Animar el golpe del jugador.
- Mover brazo derecho y arma boxel durante el ataque.
- Mantener la animacion disponible tambien cuando el jugador golpea con la mano.

Cambios:
- Player tiene attack_swing_timer y attack_swing_duration.
- start_attack_swing() dispara la animacion.
- update_attack_animation() consume el tiempo del golpe.
- attack_swing_value() devuelve un pulso suave entre 0 y 1.
- render_player_avatar() acepta attack_swing.
- main.py pasa attack_swing al render del jugador.

Comportamiento:
- El golpe se anima al hacer clic de ataque.
- El cooldown evita reiniciar la animacion en cada frame.
- El arma boxel se adelanta e inclina durante el swing.

Notas:
- Por ahora se ve en tercera persona.
- No cambia recetas, daño ni durabilidad.
- El arma sigue gastando usos solo si acierta.
