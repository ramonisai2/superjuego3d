Stage36 D - CRAFTING DE PALOS

Objetivo:
- Craftear armas simples dentro del juego.
- Usar piedra, madera y fibra recolectadas en Stage36 C.
- Hacer que el combate use alcance, daño y durabilidad del arma equipada.

Tecla:
- C: intenta craftear o mejorar el arma actual.

Recetas:
- Palo:
  - Requiere 1 madera.
  - Daño 1.2.
  - Alcance 6.4.
  - 20 usos.
- Palo con fibras:
  - Requiere tener Palo y 2 fibras.
  - Daño 1.2.
  - Alcance 6.4.
  - 50 usos.
- Palo con piedra:
  - Requiere tener Palo con fibras y 1 piedra.
  - Daño 2.0.
  - Alcance 6.4.
  - 70 usos.

Cambios:
- Player tiene active_weapon.
- Player puede craft_best_weapon().
- Combat usa current_attack_damage() y current_attack_range().
- El arma pierde 1 uso solo al acertar.
- El HUD muestra arma, daño, alcance y usos.
- El guardado conserva active_weapon.

Notas:
- Mano sigue siendo el modo base sin desgaste.
- El crafteo es secuencial por ahora.
- No hay banco de trabajo ni menu de recetas todavia.
