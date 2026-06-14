JUEGO 1.6 - Stage40 F
BIOME UNDERGROWTH

Objetivo
- Reducir la sensacion de suelo vacio.
- Agregar vegetacion baja por bioma sin saturar el rendimiento.
- Complementar los nuevos arboles con detalle cercano barato.

Tipos nuevos
- junco: orillas, pantanos bajos y humedad alta.
- helecho: bosque humedo templado.
- hierba_alta: praderas y zonas verdes medias.
- flor_azul: bosque fresco claro / pradera humeda.
- maleza_oscura: bosque oscuro humedo.

Cambios
- environment.py decide el sotobosque por humedad, altura, temperatura y rareza.
- chunk_mesh_builder.py dibuja las plantas como planos/boxels baratos.
- environment_legacy_draw.py agrega respaldo visual.

Verificacion
- py_compile de environment.py, chunk_mesh_builder.py, environment_legacy_draw.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Revisar orillas para juncos.
- Revisar bosques humedos para helechos y maleza oscura.
- Revisar zonas templadas para flor azul e hierba alta.
- Si el mundo se ve cargado, bajar detalle/deco desde presets de mundo.
