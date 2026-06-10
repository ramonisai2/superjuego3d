STAGE 28 FIX G - RESPAWN + OPTIMIZACION DE OASIS

Cambios principales:
1) Bug de reaparicion:
   - El jugador ya no reaparece siempre en (0,0).
   - Al cargar partida o iniciar mundo se define un punto seguro de respawn.
   - Si el punto guardado cae en agua o terreno raro, busca una posicion seca cercana.
   - F9 tambien aplica esta correccion al recargar.

2) Vegetacion alrededor de lagos:
   - Se conserva la regla: alrededor de los lagos hay mas vegetacion.
   - Hay flores, arbustos y pasto alto de diferentes tamaños.
   - En desierto, la orilla del lago se comporta como oasis.

3) Carga grafica:
   - Se bajo la densidad de arboles y arbustos en orillas para no saturar.
   - El pasto de oasis sigue existiendo, pero con menos instancias por celda.
   - SUBDIVISIONES bajo de 120 a 96 para equilibrar suavizado y rendimiento.

4) Arboles:
   - Troncos mas gruesos.
   - Menos segmentos en troncos para abaratar geometria.
   - Copas bajadas y con conectores mas grandes para evitar hojas flotantes.

Notas de prueba:
- Probar continuar mundo guardado y morir/recibir daño para revisar respawn.
- Buscar lagos y observar si hay vegetacion abundante alrededor sin exceso de arboles.
- Revisar si el rendimiento mejora respecto al FIX F.
