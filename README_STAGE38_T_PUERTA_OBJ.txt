JUEGO 1.6 - Stage38 T - PUERTA OBJ

Objetivo:
- Preparar el motor para importar modelos .obj externos.
- Mantenerlo como infraestructura futura, sin cambiar aun el arte visible del juego.
- Dejar una prueba sin ventana que funcione aunque falten pygame/PyOpenGL.

Cambios:
- Nuevo modulo:
  - juego3d_v1_5\motor_juegos\obj_asset_loader.py
- Puede:
  - leer vertices v, uv vt, normales vn.
  - leer grupos/objetos o/g.
  - leer materiales usemtl.
  - triangulizar caras f de 3 o mas vertices.
  - soportar indices positivos y negativos de OBJ.
  - normalizar escala y apoyar el modelo en el suelo.
  - cachear assets con ObjAssetRegistry.
  - convertir ObjMeshData a EntityMeshBufferData.
- Nuevo modelo de prueba:
  - juego3d_v1_5\assets\models\obj_probe_crate.obj
- Nueva prueba:
  - juego3d_v1_5\probar_importador_obj.py
  - PROBAR_IMPORTADOR_OBJ.bat
- INICIO_JUEGO.bat agrega opcion 13 para probar el importador OBJ.

Estado:
- Esto no reemplaza todavia boxels, skins, NPCs ni chunks.
- No renderiza .obj en el mundo por defecto.
- Deja lista la puerta para una etapa futura:
  - objetos decorativos importados.
  - herramientas/armas prototipo.
  - meshes externos para pruebas Vulkan.

Regla:
- No cambia OpenGL estable.
- No cambia Vulkan.
- No hace ZIP.
