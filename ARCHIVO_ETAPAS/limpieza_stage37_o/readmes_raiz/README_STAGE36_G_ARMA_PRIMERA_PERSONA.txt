Stage36 G - ARMA EN PRIMERA PERSONA

Objetivo:
- Mostrar las armas boxel tambien en primera persona.
- Reutilizar los mismos modelos de Palo, Palo con fibras y Palo con piedra.
- Mantener el golpe animado con attack_swing.

Cambios:
- Se agrega render_first_person_weapon().
- main.py dibuja el arma tras ejecutar el render del mundo.
- El arma solo aparece si la camara esta en primera persona y hay arma equipada.

Visual:
- Se posiciona cerca de la camara, abajo a la derecha.
- Se adelanta e inclina durante el ataque.
- Usa draw_boxel() y BOXEL_UNIT mediante render_crafted_weapon().

Notas:
- No cambia recetas, daño, alcance ni durabilidad.
- La profundidad se desactiva solo durante este dibujo para evitar parpadeos cerca de terreno.
