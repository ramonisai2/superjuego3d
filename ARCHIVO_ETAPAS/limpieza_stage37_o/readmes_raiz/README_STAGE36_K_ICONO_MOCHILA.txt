Stage36 K - ICONO DE MOCHILA

Objetivo:
- Mostrar el estado de recoleccion con un icono compacto.
- Evitar depender solo del texto.
- Comunicar tres estados simples.

Estados:
- Vacio/neutro: mochila sin linea.
- Recolectando: linea verde parpadeante.
- Llena: linea naranja.

Cambios:
- Se agrega draw_bag_status_icon().
- draw_ui() muestra el icono junto al contador de mochila.
- El icono lee pickup_notices e inventory_free().

Notas:
- No cambia capacidad, recursos ni crafteo.
- La linea verde parpadea con avisos de piedra, madera o fibra.
- La linea naranja aparece si no hay espacio o si el ultimo aviso fue mochila llena.
