STAGE35 E - NARIZ DESDE ATLAS

Objetivo:
- La nariz 3D debe tomar el color de la cara/textura correspondiente.
- Bajar un poco la nariz para que encaje mejor con el rostro.

Cambios:
- Se agrego sample_head_nose_color().
- La nariz 3D lee un promedio pequeno del pixel de nariz en el frente de la cabeza.
- render_head_features acepta nose_color.
- La nariz se bajo ligeramente en Y.

Notas:
- Esto funciona con cabeza base, carpintero viejo y futuras cabezas por raza.
- No se hizo ZIP.
