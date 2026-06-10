Stage36 I - RECETA ACTIVA HUD

Objetivo:
- Mostrar en el HUD que se puede craftear con C.
- Enseñar la siguiente mejora de palo sin abrir menu.
- Mostrar materiales disponibles contra materiales requeridos.

Cambios:
- Se agrega CRAFT_RECIPES.
- Player.next_craft_recipe() devuelve la receta activa.
- Player.craft_best_weapon() ahora usa la misma tabla de recetas.
- El HUD muestra una linea de receta activa.

Ejemplos:
- C Palo M:0/1
- C Palo con fibras F:1/2
- C Palo con piedra P:0/1

Notas:
- No cambia recetas, daño, alcance ni durabilidad.
- El texto aparece en verde si alcanza y amarillo si falta material.
- Sigue siendo crafteo ingame sin menu grande.
