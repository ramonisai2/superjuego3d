Stage36 J - NOTIFICACIONES DE RECOLECCION

Objetivo:
- Dar confirmacion visual al recoger recursos.
- Evitar saturar el HUD permanente.
- Avisar cuando la mochila esta llena.

Cambios:
- Player tiene pickup_notices.
- add_item() agrega avisos breves.
- update_pickup_notices() consume el tiempo de vida.
- draw_pickup_notices() muestra hasta 3 avisos compactos.

Visual:
- Piedra: gris claro.
- Madera: marron claro.
- Fibra: verde suave.
- Mochila llena: naranja.

Notas:
- No cambia recoleccion, capacidad ni recetas.
- El panel solo aparece cuando hay avisos activos.
