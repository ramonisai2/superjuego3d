@echo off
setlocal

set "ROOT=%~dp0"
set "FALTAN=0"

echo ===============================================
echo  JUEGO 1.6 - VERIFICAR ESTRUCTURA
echo ===============================================
echo.

if exist "%ROOT%INICIO_JUEGO.bat" (echo OK     archivo  INICIO_JUEGO.bat) else (echo FALTA  archivo  INICIO_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%LEEME_PRIMERO.txt" (echo OK     archivo  LEEME_PRIMERO.txt) else (echo FALTA  archivo  LEEME_PRIMERO.txt & set /a FALTAN+=1)
if exist "%ROOT%requirements_juego.txt" (echo OK     archivo  requirements_juego.txt) else (echo FALTA  archivo  requirements_juego.txt & set /a FALTAN+=1)
if exist "%ROOT%LANZAR_OPENGL.bat" (echo OK     archivo  LANZAR_OPENGL.bat) else (echo FALTA  archivo  LANZAR_OPENGL.bat & set /a FALTAN+=1)
if exist "%ROOT%LANZAR_OPENGL_RECOMENDADO.bat" (echo OK     archivo  LANZAR_OPENGL_RECOMENDADO.bat) else (echo FALTA  archivo  LANZAR_OPENGL_RECOMENDADO.bat & set /a FALTAN+=1)
if exist "%ROOT%PROBAR_PRESETS_OPENGL.bat" (echo OK     archivo  PROBAR_PRESETS_OPENGL.bat) else (echo FALTA  archivo  PROBAR_PRESETS_OPENGL.bat & set /a FALTAN+=1)
if exist "%ROOT%PROBAR_IMPORTADOR_OBJ.bat" (echo OK     archivo  PROBAR_IMPORTADOR_OBJ.bat) else (echo FALTA  archivo  PROBAR_IMPORTADOR_OBJ.bat & set /a FALTAN+=1)
if exist "%ROOT%PREVISUALIZAR_VEGETACION_BIOMAS.bat" (echo OK     archivo  PREVISUALIZAR_VEGETACION_BIOMAS.bat) else (echo FALTA  archivo  PREVISUALIZAR_VEGETACION_BIOMAS.bat & set /a FALTAN+=1)
if exist "%ROOT%AUDITAR_VALORES_RECICLABLES.bat" (echo OK     archivo  AUDITAR_VALORES_RECICLABLES.bat) else (echo FALTA  archivo  AUDITAR_VALORES_RECICLABLES.bat & set /a FALTAN+=1)
if exist "%ROOT%AUDITAR_TAMANO_PY.bat" (echo OK     archivo  AUDITAR_TAMANO_PY.bat) else (echo FALTA  archivo  AUDITAR_TAMANO_PY.bat & set /a FALTAN+=1)
if exist "%ROOT%VERIFICAR_ENTORNO_JUEGO.bat" (echo OK     archivo  VERIFICAR_ENTORNO_JUEGO.bat) else (echo FALTA  archivo  VERIFICAR_ENTORNO_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" (echo OK     archivo  SELECCIONAR_PYTHON_JUEGO.bat) else (echo FALTA  archivo  SELECCIONAR_PYTHON_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_REPARACION.bat" (echo OK     archivo  SELECCIONAR_PYTHON_REPARACION.bat) else (echo FALTA  archivo  SELECCIONAR_PYTHON_REPARACION.bat & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\python_dependency_score.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\python_dependency_score.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\python_dependency_score.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\preset_runtime_log_analyzer.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\preset_runtime_log_analyzer.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\preset_runtime_log_analyzer.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\env_config.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\env_config.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\env_config.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\chunk_math.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\chunk_math.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\chunk_math.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\world_detail.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\world_detail.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\world_detail.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\chunk_mesh_builder.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\chunk_mesh_builder.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\chunk_mesh_builder.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\environment_legacy_draw.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\environment_legacy_draw.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\environment_legacy_draw.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\far_terrain_lod.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\far_terrain_lod.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\far_terrain_lod.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\forest_impostor_lod.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\forest_impostor_lod.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\forest_impostor_lod.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\atmospheric_sky.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\atmospheric_sky.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\atmospheric_sky.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\vegetation_preview.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\vegetation_preview.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\vegetation_preview.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\obj_asset_loader.py" (echo OK     archivo  juego3d_v1_5\motor_juegos\obj_asset_loader.py) else (echo FALTA  archivo  juego3d_v1_5\motor_juegos\obj_asset_loader.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main.py" (echo OK     archivo  juego3d_v1_5\main.py) else (echo FALTA  archivo  juego3d_v1_5\main.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_config.py" (echo OK     archivo  juego3d_v1_5\main_config.py) else (echo FALTA  archivo  juego3d_v1_5\main_config.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_adaptive_quality.py" (echo OK     archivo  juego3d_v1_5\main_adaptive_quality.py) else (echo FALTA  archivo  juego3d_v1_5\main_adaptive_quality.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_resources.py" (echo OK     archivo  juego3d_v1_5\main_resources.py) else (echo FALTA  archivo  juego3d_v1_5\main_resources.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_preset_logging.py" (echo OK     archivo  juego3d_v1_5\main_preset_logging.py) else (echo FALTA  archivo  juego3d_v1_5\main_preset_logging.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_spawn.py" (echo OK     archivo  juego3d_v1_5\main_spawn.py) else (echo FALTA  archivo  juego3d_v1_5\main_spawn.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_hud_render.py" (echo OK     archivo  juego3d_v1_5\main_hud_render.py) else (echo FALTA  archivo  juego3d_v1_5\main_hud_render.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_world_runtime.py" (echo OK     archivo  juego3d_v1_5\main_world_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\main_world_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_render3d.py" (echo OK     archivo  juego3d_v1_5\main_render3d.py) else (echo FALTA  archivo  juego3d_v1_5\main_render3d.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_preload.py" (echo OK     archivo  juego3d_v1_5\main_preload.py) else (echo FALTA  archivo  juego3d_v1_5\main_preload.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_save_runtime.py" (echo OK     archivo  juego3d_v1_5\main_save_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\main_save_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_entity_runtime.py" (echo OK     archivo  juego3d_v1_5\main_entity_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\main_entity_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_combat_runtime.py" (echo OK     archivo  juego3d_v1_5\main_combat_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\main_combat_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_chunk_runtime.py" (echo OK     archivo  juego3d_v1_5\main_chunk_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\main_chunk_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_screens.py" (echo OK     archivo  juego3d_v1_5\main_screens.py) else (echo FALTA  archivo  juego3d_v1_5\main_screens.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\probar_importador_obj.py" (echo OK     archivo  juego3d_v1_5\probar_importador_obj.py) else (echo FALTA  archivo  juego3d_v1_5\probar_importador_obj.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\previsualizar_vegetacion_biomas.py" (echo OK     archivo  juego3d_v1_5\previsualizar_vegetacion_biomas.py) else (echo FALTA  archivo  juego3d_v1_5\previsualizar_vegetacion_biomas.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\auditar_valores_reciclables.py" (echo OK     archivo  juego3d_v1_5\auditar_valores_reciclables.py) else (echo FALTA  archivo  juego3d_v1_5\auditar_valores_reciclables.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\auditar_tamano_py.py" (echo OK     archivo  juego3d_v1_5\auditar_tamano_py.py) else (echo FALTA  archivo  juego3d_v1_5\auditar_tamano_py.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\models\obj_probe_crate.obj" (echo OK     archivo  juego3d_v1_5\assets\models\obj_probe_crate.obj) else (echo FALTA  archivo  juego3d_v1_5\assets\models\obj_probe_crate.obj & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\player_skin_texture_atlas.png" (echo OK     archivo  juego3d_v1_5\player_skin_texture_atlas.png) else (echo FALTA  archivo  juego3d_v1_5\player_skin_texture_atlas.png & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\entity_update_budget.py" (echo OK     archivo  juego3d_v1_5\game\entity_update_budget.py) else (echo FALTA  archivo  juego3d_v1_5\game\entity_update_budget.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_identity.py" (echo OK     archivo  juego3d_v1_5\game\npc_identity.py) else (echo FALTA  archivo  juego3d_v1_5\game\npc_identity.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_memory.py" (echo OK     archivo  juego3d_v1_5\game\npc_memory.py) else (echo FALTA  archivo  juego3d_v1_5\game\npc_memory.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_ai_runtime.py" (echo OK     archivo  juego3d_v1_5\game\npc_ai_runtime.py) else (echo FALTA  archivo  juego3d_v1_5\game\npc_ai_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\projectiles.py" (echo OK     archivo  juego3d_v1_5\game\projectiles.py) else (echo FALTA  archivo  juego3d_v1_5\game\projectiles.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\z_targeting.py" (echo OK     archivo  juego3d_v1_5\game\z_targeting.py) else (echo FALTA  archivo  juego3d_v1_5\game\z_targeting.py & set /a FALTAN+=1)

if exist "%ROOT%juego3d_v1_5\" (echo OK     carpeta  juego3d_v1_5) else (echo FALTA  carpeta  juego3d_v1_5 & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\" (echo OK     carpeta  juego3d_v1_5\motor_juegos) else (echo FALTA  carpeta  juego3d_v1_5\motor_juegos & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\" (echo OK     carpeta  juego3d_v1_5\assets) else (echo FALTA  carpeta  juego3d_v1_5\assets & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\models\" (echo OK     carpeta  juego3d_v1_5\assets\models) else (echo FALTA  carpeta  juego3d_v1_5\assets\models & set /a FALTAN+=1)
if exist "%ROOT%ARCHIVO_ETAPAS\" (echo OK     carpeta  ARCHIVO_ETAPAS) else (echo FALTA  carpeta  ARCHIVO_ETAPAS & set /a FALTAN+=1)

echo.
echo ===============================================
echo  RESULTADO
echo ===============================================
if "%FALTAN%"=="0" (
    echo Estructura OK. Las piezas principales estan presentes.
) else (
    echo Faltan %FALTAN% piezas. Revisa las lineas marcadas como FALTA.
)
echo.
pause
exit /b %FALTAN%
