@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "LOG_DIR=%ROOT%juego3d_v1_5\logs"
set "REPORT=%LOG_DIR%\estado_rapido_juego.txt"
set "PRESET_FILE=%LOG_DIR%\recommended_graphics_preset.txt"
set "VEG_REPORT=%ROOT%juego3d_v1_5\previews\vegetation_biomes_report.txt"
set "UPDATE_FILE=%LOG_DIR%\current_update_status.txt"
set "FALTAN=0"
set "JUEGO_OK=0"
set "PREVIEW_OK=0"
set "UPDATE_STAGE=unknown"
set "UPDATE_SUBTITLE=unknown"
set "UPDATE_DESCRIPTION=unknown"
set "PRESET_RECOMMENDED=balanced"
set "PRESET_CONFIDENCE=unknown"
set "PRESET_SAMPLES=0"
set "PRESET_MISSING=unknown"
set "VEG_STATUS=sin_reporte"
set "VEG_COVERAGE=unknown"
set "VEG_TREES=unknown"
set "VEG_UNDERSTORY=unknown"
set "VEG_STABILITY=unknown"
set "VEG_COVERAGE_MIN=unknown"
set "VEG_COVERAGE_AVG=unknown"
set "VEG_COVERAGE_MAX=unknown"
set "VEG_REPORT_STAGE=unknown"
set "VEG_REPORT_FRESH=unknown"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

> "%REPORT%" echo JUEGO 1.6 - ESTADO RAPIDO
>> "%REPORT%" echo Fecha: %DATE% %TIME%
>> "%REPORT%" echo.
>> "%REPORT%" echo ESTRUCTURA PRINCIPAL
>> "%REPORT%" echo --------------------

if exist "%ROOT%INICIO_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  INICIO_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  INICIO_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%LEEME_PRIMERO.txt" (>> "%REPORT%" echo OK     archivo  LEEME_PRIMERO.txt) else (>> "%REPORT%" echo FALTA  archivo  LEEME_PRIMERO.txt & set /a FALTAN+=1)
if exist "%ROOT%requirements_juego.txt" (>> "%REPORT%" echo OK     archivo  requirements_juego.txt) else (>> "%REPORT%" echo FALTA  archivo  requirements_juego.txt & set /a FALTAN+=1)
if exist "%ROOT%LANZAR_OPENGL.bat" (>> "%REPORT%" echo OK     archivo  LANZAR_OPENGL.bat) else (>> "%REPORT%" echo FALTA  archivo  LANZAR_OPENGL.bat & set /a FALTAN+=1)
if exist "%ROOT%LANZAR_OPENGL_RECOMENDADO.bat" (>> "%REPORT%" echo OK     archivo  LANZAR_OPENGL_RECOMENDADO.bat) else (>> "%REPORT%" echo FALTA  archivo  LANZAR_OPENGL_RECOMENDADO.bat & set /a FALTAN+=1)
if exist "%ROOT%PROBAR_PRESETS_OPENGL.bat" (>> "%REPORT%" echo OK     archivo  PROBAR_PRESETS_OPENGL.bat) else (>> "%REPORT%" echo FALTA  archivo  PROBAR_PRESETS_OPENGL.bat & set /a FALTAN+=1)
if exist "%ROOT%PROBAR_IMPORTADOR_OBJ.bat" (>> "%REPORT%" echo OK     archivo  PROBAR_IMPORTADOR_OBJ.bat) else (>> "%REPORT%" echo FALTA  archivo  PROBAR_IMPORTADOR_OBJ.bat & set /a FALTAN+=1)
if exist "%ROOT%PREVISUALIZAR_VEGETACION_BIOMAS.bat" (>> "%REPORT%" echo OK     archivo  PREVISUALIZAR_VEGETACION_BIOMAS.bat) else (>> "%REPORT%" echo FALTA  archivo  PREVISUALIZAR_VEGETACION_BIOMAS.bat & set /a FALTAN+=1)
if exist "%ROOT%AUDITAR_VALORES_RECICLABLES.bat" (>> "%REPORT%" echo OK     archivo  AUDITAR_VALORES_RECICLABLES.bat) else (>> "%REPORT%" echo FALTA  archivo  AUDITAR_VALORES_RECICLABLES.bat & set /a FALTAN+=1)
if exist "%ROOT%AUDITAR_TAMANO_PY.bat" (>> "%REPORT%" echo OK     archivo  AUDITAR_TAMANO_PY.bat) else (>> "%REPORT%" echo FALTA  archivo  AUDITAR_TAMANO_PY.bat & set /a FALTAN+=1)
if exist "%ROOT%VERIFICAR_ENTORNO_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  VERIFICAR_ENTORNO_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  VERIFICAR_ENTORNO_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%VERIFICAR_ESTRUCTURA_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  VERIFICAR_ESTRUCTURA_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  VERIFICAR_ESTRUCTURA_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  SELECCIONAR_PYTHON_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  SELECCIONAR_PYTHON_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_REPARACION.bat" (>> "%REPORT%" echo OK     archivo  SELECCIONAR_PYTHON_REPARACION.bat) else (>> "%REPORT%" echo FALTA  archivo  SELECCIONAR_PYTHON_REPARACION.bat & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\env_config.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\env_config.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\env_config.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\chunk_math.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\chunk_math.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\chunk_math.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\world_detail.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\world_detail.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\world_detail.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\chunk_mesh_builder.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\chunk_mesh_builder.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\chunk_mesh_builder.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\environment_legacy_draw.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\environment_legacy_draw.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\environment_legacy_draw.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\far_terrain_lod.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\far_terrain_lod.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\far_terrain_lod.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\forest_impostor_lod.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\forest_impostor_lod.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\forest_impostor_lod.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\atmospheric_sky.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\atmospheric_sky.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\atmospheric_sky.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\vegetation_preview.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\vegetation_preview.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\vegetation_preview.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\obj_asset_loader.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\motor_juegos\obj_asset_loader.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\motor_juegos\obj_asset_loader.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_config.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_config.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_config.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_adaptive_quality.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_adaptive_quality.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_adaptive_quality.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_resources.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_resources.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_resources.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_preset_logging.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_preset_logging.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_preset_logging.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_spawn.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_spawn.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_spawn.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_hud_render.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_hud_render.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_hud_render.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_world_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_world_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_world_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_render3d.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_render3d.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_render3d.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_preload.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_preload.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_preload.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_save_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_save_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_save_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_entity_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_entity_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_entity_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_combat_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_combat_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_combat_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_chunk_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_chunk_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_chunk_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main_screens.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main_screens.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main_screens.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\probar_importador_obj.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\probar_importador_obj.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\probar_importador_obj.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\previsualizar_vegetacion_biomas.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\previsualizar_vegetacion_biomas.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\previsualizar_vegetacion_biomas.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\auditar_valores_reciclables.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\auditar_valores_reciclables.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\auditar_valores_reciclables.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\auditar_tamano_py.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\auditar_tamano_py.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\auditar_tamano_py.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\models\obj_probe_crate.obj" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\assets\models\obj_probe_crate.obj) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\assets\models\obj_probe_crate.obj & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\player_skin_texture_atlas.png" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\player_skin_texture_atlas.png) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\player_skin_texture_atlas.png & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\entity_update_budget.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\entity_update_budget.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\entity_update_budget.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_identity.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\npc_identity.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\npc_identity.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_memory.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\npc_memory.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\npc_memory.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\npc_ai_runtime.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\npc_ai_runtime.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\npc_ai_runtime.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\projectiles.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\projectiles.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\projectiles.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\game\z_targeting.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\game\z_targeting.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\game\z_targeting.py & set /a FALTAN+=1)

if exist "%ROOT%juego3d_v1_5\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\ & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\motor_juegos\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\motor_juegos\ & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\assets\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\assets\ & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\models\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\assets\models\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\assets\models\ & set /a FALTAN+=1)
if exist "%ROOT%ARCHIVO_ETAPAS\" (>> "%REPORT%" echo OK     carpeta  ARCHIVO_ETAPAS\) else (>> "%REPORT%" echo FALTA  carpeta  ARCHIVO_ETAPAS\ & set /a FALTAN+=1)

>> "%REPORT%" echo.
>> "%REPORT%" echo PYTHON
>> "%REPORT%" echo ------
if exist "%ROOT%JUEGO_PYTHON_LOCAL.bat" (
    >> "%REPORT%" echo Python local guardado: SI
) else (
    >> "%REPORT%" echo Python local guardado: NO
)

set JUEGO_PY_CMD=
set JUEGO_PYTHON_CHECK=import numpy, pygame, OpenGL
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" >nul 2>nul
if errorlevel 1 (
    >> "%REPORT%" echo Juego: FALTA Python con numpy, pygame y PyOpenGL
) else (
    set "JUEGO_OK=1"
    >> "%REPORT%" echo Juego: OK
    >> "%REPORT%" echo Python juego: %JUEGO_PY_CMD%
)

set JUEGO_PY_CMD=
set JUEGO_PYTHON_CHECK=import numpy; from PIL import Image
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" >nul 2>nul
if errorlevel 1 (
    >> "%REPORT%" echo Previews: FALTA Python con numpy y PIL
) else (
    set "PREVIEW_OK=1"
    >> "%REPORT%" echo Previews: OK
    >> "%REPORT%" echo Python previews: %JUEGO_PY_CMD%
)

>> "%REPORT%" echo.
>> "%REPORT%" echo ACTUALIZACION
>> "%REPORT%" echo ------------
if "%PREVIEW_OK%"=="1" (
    pushd "%ROOT%juego3d_v1_5" >nul
    "%JUEGO_PY_CMD%" -c "from motor_juegos.version_info import full_update_name, UPDATE_SUBTITLE, UPDATE_DESCRIPTION; print('stage=' + full_update_name()); print('subtitle=' + UPDATE_SUBTITLE); print('description=' + UPDATE_DESCRIPTION)" > "%UPDATE_FILE%" 2>nul
    popd >nul
    if exist "%UPDATE_FILE%" (
        for /f "tokens=1,* delims==" %%A in ('type "%UPDATE_FILE%"') do (
            if /i "%%A"=="stage" set "UPDATE_STAGE=%%B"
            if /i "%%A"=="subtitle" set "UPDATE_SUBTITLE=%%B"
            if /i "%%A"=="description" set "UPDATE_DESCRIPTION=%%B"
        )
        type "%UPDATE_FILE%" >> "%REPORT%"
    ) else (
        >> "%REPORT%" echo No se pudo leer motor_juegos\version_info.py
    )
) else (
    >> "%REPORT%" echo No se pudo leer version_info.py porque falta Python para previews.
)

>> "%REPORT%" echo.
>> "%REPORT%" echo PRESET GRAFICO
>> "%REPORT%" echo --------------
set JUEGO_PY_CMD=
set JUEGO_PYTHON_CHECK=import pathlib
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" >nul 2>nul
if errorlevel 1 (
    >> "%REPORT%" echo No se pudo actualizar el analisis de presets.
) else (
    pushd "%ROOT%juego3d_v1_5" >nul
    "%JUEGO_PY_CMD%" -m motor_juegos.preset_runtime_log_analyzer >nul 2>nul
    popd >nul
    if exist "%PRESET_FILE%" (
        type "%PRESET_FILE%" >> "%REPORT%"
        for /f "tokens=1,* delims==" %%A in ('type "%PRESET_FILE%"') do (
            if /i "%%A"=="preset" set "PRESET_RECOMMENDED=%%B"
            if /i "%%A"=="confidence" set "PRESET_CONFIDENCE=%%B"
            if /i "%%A"=="samples" set "PRESET_SAMPLES=%%B"
            if /i "%%A"=="missing_presets" set "PRESET_MISSING=%%B"
        )
    ) else (
        >> "%REPORT%" echo Aun no hay archivo de preset recomendado.
    )
)

>> "%REPORT%" echo.
>> "%REPORT%" echo VEGETACION
>> "%REPORT%" echo ----------
if exist "%VEG_REPORT%" (
    for /f "tokens=1,* delims==" %%A in ('type "%VEG_REPORT%"') do (
        if /i "%%A"=="update_stage" set "VEG_REPORT_STAGE=%%B"
        if /i "%%A"=="cobertura_total" set "VEG_COVERAGE=%%B"
        if /i "%%A"=="arboles" set "VEG_TREES=%%B"
        if /i "%%A"=="sotobosque" set "VEG_UNDERSTORY=%%B"
        if /i "%%A"=="lectura" set "VEG_STATUS=%%B"
        if /i "%%A"=="stability" set "VEG_STABILITY=%%B"
        if /i "%%A"=="coverage_min" set "VEG_COVERAGE_MIN=%%B"
        if /i "%%A"=="coverage_avg" set "VEG_COVERAGE_AVG=%%B"
        if /i "%%A"=="coverage_max" set "VEG_COVERAGE_MAX=%%B"
    )
    if "!VEG_REPORT_STAGE!"=="!UPDATE_STAGE!" (set "VEG_REPORT_FRESH=SI") else (set "VEG_REPORT_FRESH=NO")
    >> "%REPORT%" echo Reporte: OK
    >> "%REPORT%" echo reporte_etapa=!VEG_REPORT_STAGE!
    >> "%REPORT%" echo reporte_actualizado=!VEG_REPORT_FRESH!
    >> "%REPORT%" echo cobertura_total=!VEG_COVERAGE!
    >> "%REPORT%" echo arboles=!VEG_TREES!
    >> "%REPORT%" echo sotobosque=!VEG_UNDERSTORY!
    >> "%REPORT%" echo lectura=!VEG_STATUS!
    >> "%REPORT%" echo multiseed=!VEG_STABILITY!
    >> "%REPORT%" echo cobertura_multiseed=!VEG_COVERAGE_MIN! - !VEG_COVERAGE_MAX! promedio !VEG_COVERAGE_AVG!
) else (
    >> "%REPORT%" echo Reporte: FALTA preview de vegetacion
    >> "%REPORT%" echo Ejecuta INICIO_JUEGO.bat opcion 10 para generar vegetation_biomes_report.txt.
)

>> "%REPORT%" echo.
>> "%REPORT%" echo RESUMEN
>> "%REPORT%" echo -------
if "%FALTAN%"=="0" (
    >> "%REPORT%" echo Estructura: OK
) else (
    >> "%REPORT%" echo Estructura: Faltan %FALTAN% piezas.
)
>> "%REPORT%" echo Preset sugerido: %PRESET_RECOMMENDED%
>> "%REPORT%" echo Vegetacion: %VEG_STATUS% %VEG_COVERAGE% multiseed %VEG_STABILITY% reporte %VEG_REPORT_FRESH%
>> "%REPORT%" echo Actualizacion: %UPDATE_STAGE%
>> "%REPORT%" echo.
>> "%REPORT%" echo SIGUIENTE PASO
>> "%REPORT%" echo --------------
if not "%JUEGO_OK%"=="1" (
    >> "%REPORT%" echo Prioridad 1: configurar un Python que tenga numpy, pygame y PyOpenGL.
    >> "%REPORT%" echo Desde INICIO_JUEGO.bat usa la opcion 6 para instalar dependencias o la opcion 7 para guardar una ruta de Python.
    >> "%REPORT%" echo La opcion 6 elegira el Python que ya tenga mas paquetes listos.
    >> "%REPORT%" echo Para ver exactamente que paquete falta en cada Python, usa la opcion 3.
    >> "%REPORT%" echo Si ya guardaste una ruta local, la opcion 6 la usara automaticamente.
    >> "%REPORT%" echo.
    >> "%REPORT%" echo Comando manual sugerido:
    >> "%REPORT%" echo py -m pip install -r "%ROOT%requirements_juego.txt"
    call "%ROOT%SELECCIONAR_PYTHON_REPARACION.bat" >nul 2>nul
    if not errorlevel 1 (
        >> "%REPORT%" echo.
        >> "%REPORT%" echo Comando elegido por opcion 6:
        >> "%REPORT%" echo "!JUEGO_PY_REPAIR_CMD!" -m pip install -r "%ROOT%requirements_juego.txt"
        >> "%REPORT%" echo Python destino: !JUEGO_PY_REPAIR_SOURCE!
        >> "%REPORT%" echo Faltan: !JUEGO_PY_REPAIR_MISSING!
    )
    >> "%REPORT%" echo.
    >> "%REPORT%" echo Si usas la opcion 6, el instalador verificara el Python destino al terminar.
    >> "%REPORT%" echo Si queda listo, podra guardar esa ruta para futuros lanzadores.
    >> "%REPORT%" echo Despues ejecuta otra vez la opcion 13 para confirmar.
) else if not "%PREVIEW_OK%"=="1" (
    >> "%REPORT%" echo Prioridad 1: revisar Python para previews de terreno.
    >> "%REPORT%" echo El juego puede abrir, pero las herramientas de vista previa no estan completas.
    >> "%REPORT%" echo La opcion 6 elegira el Python que ya tenga mas paquetes listos.
    >> "%REPORT%" echo Para ver exactamente que paquete falta en cada Python, usa la opcion 3.
    >> "%REPORT%" echo Si ya guardaste una ruta local, la opcion 6 la usara automaticamente.
    >> "%REPORT%" echo.
    >> "%REPORT%" echo Comando manual sugerido:
    >> "%REPORT%" echo py -m pip install -r "%ROOT%requirements_juego.txt"
    call "%ROOT%SELECCIONAR_PYTHON_REPARACION.bat" >nul 2>nul
    if not errorlevel 1 (
        >> "%REPORT%" echo.
        >> "%REPORT%" echo Comando elegido por opcion 6:
        >> "%REPORT%" echo "!JUEGO_PY_REPAIR_CMD!" -m pip install -r "%ROOT%requirements_juego.txt"
        >> "%REPORT%" echo Python destino: !JUEGO_PY_REPAIR_SOURCE!
        >> "%REPORT%" echo Faltan: !JUEGO_PY_REPAIR_MISSING!
    )
    >> "%REPORT%" echo.
    >> "%REPORT%" echo Si usas la opcion 6, el instalador verificara el Python destino al terminar.
    >> "%REPORT%" echo Si queda listo, podra guardar esa ruta para futuros lanzadores.
    >> "%REPORT%" echo Despues ejecuta otra vez la opcion 13 para confirmar.
) else if not "%PRESET_CONFIDENCE%"=="ok" (
    >> "%REPORT%" echo Prioridad 1: completar comparacion de presets.
    >> "%REPORT%" echo Preset actual sugerido: %PRESET_RECOMMENDED% con confianza baja.
    >> "%REPORT%" echo Faltan muestras de: %PRESET_MISSING%.
    >> "%REPORT%" echo Desde INICIO_JUEGO.bat usa la opcion 4 y prueba cada preset caminando 1 o 2 minutos.
) else (
    >> "%REPORT%" echo Todo lo principal esta listo para una sesion de juego.
    >> "%REPORT%" echo Usa OpenGL estable o OpenGL recomendado con preset %PRESET_RECOMMENDED%.
)
>> "%REPORT%" echo.
>> "%REPORT%" echo Reporte guardado en:
>> "%REPORT%" echo %REPORT%

cls
type "%REPORT%"
echo.
pause
exit /b %FALTAN%
