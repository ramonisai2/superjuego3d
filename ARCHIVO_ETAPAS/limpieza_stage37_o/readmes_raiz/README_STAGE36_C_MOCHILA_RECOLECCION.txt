Stage36 C - MOCHILA Y RECOLECCION

Objetivo:
- Dar al jugador una mochila basica.
- Recoger recursos simples por cercania al mundo.
- Preparar la base para crafteo sin abrir menus pesados todavia.

Recursos:
- Piedra: cerca o encima de rocas.
- Madera: cerca de arboles.
- Fibra: dentro de hierba alta.

Cambios:
- Player ahora usa inventario por cantidades.
- Player tiene bag_name, bag_capacity y mensajes de recoleccion.
- Los guardados viejos con inventario tipo lista se normalizan.
- main.py registra rocas, arboles y pasto por chunk.
- try_gather_basic_resource() recoge con pausa por nodo.
- El HUD muestra mochila, capacidad y cantidades P/M/F.

Diseno futuro:
- Primero bolsillos.
- Luego saco.
- Luego alforja.
- Luego mochila expandible.
- Mas adelante mochila magica.

Notas:
- No hay crafteo todavia.
- Los recursos no abren un menu.
- La recoleccion esta limitada por capacidad y cooldown por nodo.
