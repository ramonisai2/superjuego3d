Stage36 H - MANO Y AGARRE BOXEL

Objetivo:
- Mostrar mano/puño en primera persona aunque no haya arma equipada.
- Hacer que las armas boxel parezcan agarradas, no flotando.
- Mantener la misma animacion de ataque.

Cambios:
- Se agrega render_first_person_grip().
- render_first_person_weapon() ya no sale temprano con mano.
- Si no hay arma, se dibuja puño/antebrazo.
- Si hay arma, se dibuja puño, agarre y arma.

Visual:
- Antebrazo con manga.
- Puño con dedos boxel.
- Banda de agarre cuando sostiene palo.

Notas:
- No cambia daño, alcance, usos ni recetas.
- Por ahora usa colores base de piel/manga.
- Mas adelante puede leer skin del jugador para colorear mano y ropa.
