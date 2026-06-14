JUEGO 1.6 - Stage39 U
ENVIRONMENT LEGACY DRAW MODULE

Objetivo
- Separar el dibujo OpenGL legacy de rocas y decoraciones fuera de environment.py.
- Mantener environment.py enfocado en generacion/consulta de terreno.
- Dejar el renderer legacy mas facil de reemplazar cuando OpenGL/Vulkan avance.

Cambios
- Nuevo modulo: juego3d_v1_5\motor_juegos\environment_legacy_draw.py
- environment.py importa draw_optimized_rock() y draw_decorations().
- Se elimino el bloque interno viejo de rocas/decoraciones dentro de environment.py.

Resultado
- environment.py bajo de 962 a 714 lineas.
- Ningun archivo Python supera la meta de 1000 lineas.

Verificacion
- py_compile de environment.py y environment_legacy_draw.py.
- auditar_tamano_py.py.
- Verificador estructural actualizado para revisar el modulo nuevo.
