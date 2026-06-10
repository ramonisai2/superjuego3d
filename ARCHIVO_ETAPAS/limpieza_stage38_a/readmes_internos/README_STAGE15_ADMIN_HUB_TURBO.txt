STAGE 15 TURBO - ADMIN HUB REAL

Controles:
- F1 abre/cierra el Admin Hub.
- Con el Hub abierto:
  - Botón Spawn NPC o tecla 1.
  - Botón Spawn Enemigo o tecla 2.
  - Botón Spawn Jefe o tecla 3.
  - Botón Spawn Legendario o tecla 4.
  - Botón Pausar / Activar IA.
  - Botón Limpiar entidades Admin.
  - Botón Limpiar TODAS las entidades.

Cambios importantes:
- Se agregó game/admin_hub.py.
- Se integró AdminHub en main.py.
- El HUD/UI fue migrado a OpenGL 2D mediante motor_juegos/renderer2d.py.
- Esto corrige el problema típico de pygame.blit/pygame.draw que no aparece en ventanas OPENGL.
- Se corrigió game/inventory.py porque tenía indentación inválida.
- Los jefes spawneados por Admin Hub se renderizan más grandes y morados.
- Los NPCs legendarios tienen color especial amarillo/dorado.

Notas:
- Esta fase es una herramienta de desarrollo para probar NPCs, enemigos y futuras entidades.
- Más adelante se puede añadir inspector de entidades, consola de comandos y creación de aldeas.
