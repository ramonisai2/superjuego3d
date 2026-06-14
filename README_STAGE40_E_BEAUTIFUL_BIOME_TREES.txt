JUEGO 1.6 - Stage40 E
BEAUTIFUL BIOME TREES

Objetivo
- Agregar arboles cercanos mas hermosos y con personalidad.
- Mantenerlos baratos: ramas boxel simples + copas impostor.
- Darles biomas favoritos para que no aparezcan como decoracion aleatoria.

Tipos nuevos
- arbol_roble: bosque templado / pradera humeda.
- arbol_pino: montana fria / meseta alta.
- arbol_abedul: bosque fresco claro.
- arbol_sauce: orilla humeda / pantano bajo.
- arbol_cipres: bosque oscuro humedo.

Cambios
- biomes.py contiene TREE_FAVORITE_BIOMES y _choose_tree_type().
- chunk_mesh_builder.py dibuja ramas y copas propias para cada tipo.
- environment.py usa sauce/roble cerca de oasis y orillas.
- forest_impostor_lod.py reconoce los nuevos tipos para masa lejana.
- environment_legacy_draw.py tiene respaldo si algun arbol nuevo cae a legacy.

Verificacion
- py_compile de biomes.py, chunk_mesh_builder.py, environment.py, environment_legacy_draw.py, forest_impostor_lod.py y version_info.py.
- auditar_tamano_py.py.
- VERIFICAR_ESTRUCTURA_JUEGO.bat.
- ESTADO_RAPIDO_JUEGO.bat.

Prueba visual recomendada
- Buscar zonas humedas bajas para sauce.
- Buscar bosque oscuro humedo para cipres.
- Buscar praderas/bosques templados para roble.
- Buscar zonas frias/altas para pino.
- Buscar bosque fresco claro para abedul.
