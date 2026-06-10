JUEGO 1.6 - Stage35 J - IDENTIDAD DE OFICIO

Objetivo
- Pasar de NPCs con ropa/equipo visual a NPCs con oficio consultable.
- Preparar una base estable para necesidades, memoria por ID e IA compacta futura.
- No cambiar el nombre ni atributos especiales ya generados por algoritmo.

Cambios
- Cada profesion humana ahora tiene:
  tool_label, workplace, material, action y temper.
- Cada NPC guarda:
  tool_label, workplace, work_material, work_action, temper e identity_key.
- needs_snapshot() expone identidad, oficio, herramienta y estado actual.
- interactuar() muestra oficio, tarea y necesidad actual antes de dialogos genericos.

Notas
- No hay modelo de lenguaje todavia.
- No se agrego inventario ni combate por herramienta.
- No se genero ZIP.
