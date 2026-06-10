
STAGE 16 - IDENTIDAD VISUAL + TERCERA PERSONA

Cambios integrados:
- Corrección del texto 2D invertido en renderer2d.py.
- NPCs boxel/voxel modulares con cabeza, torso, brazos, piernas, ojos, nariz, insignia frontal y mochila trasera.
- Los NPCs ahora tienen yaw/dirección visible y miran hacia donde caminan.
- Separación conceptual de collider, visual bounds y selection outline.
- Al seleccionar un NPC desde cerca se muestra contorno verde visual; con Admin Hub abierto también se ve hitbox roja.
- Tercera persona: tecla V alterna cámara; tecla B cambia distancia.
- En tercera persona se renderiza el jugador como avatar boxel azul.
- Árboles y arbustos por bioma integrados en environment.py.
- Nuevos árboles: bosque, pantano y seco/desierto.

Controles nuevos:
- V: alternar primera/tercera persona.
- B: cambiar distancia de cámara en tercera persona.
- F1: Admin Hub.

Nota:
Este stage sigue usando geometría simple inmediata/OpenGL clásico. La siguiente mejora recomendada
es crear un Texture Atlas real para boxels y un sistema de modelos con partes reutilizables.
