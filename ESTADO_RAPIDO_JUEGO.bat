@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "LOG_DIR=%ROOT%juego3d_v1_5\logs"
set "REPORT=%LOG_DIR%\estado_rapido_juego.txt"
set "PRESET_FILE=%LOG_DIR%\recommended_graphics_preset.txt"
set "FALTAN=0"
set "JUEGO_OK=0"
set "PREVIEW_OK=0"
set "PRESET_RECOMMENDED=balanced"
set "PRESET_CONFIDENCE=unknown"
set "PRESET_SAMPLES=0"
set "PRESET_MISSING=unknown"

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
if exist "%ROOT%VERIFICAR_ENTORNO_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  VERIFICAR_ENTORNO_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  VERIFICAR_ENTORNO_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%VERIFICAR_ESTRUCTURA_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  VERIFICAR_ESTRUCTURA_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  VERIFICAR_ESTRUCTURA_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat" (>> "%REPORT%" echo OK     archivo  SELECCIONAR_PYTHON_JUEGO.bat) else (>> "%REPORT%" echo FALTA  archivo  SELECCIONAR_PYTHON_JUEGO.bat & set /a FALTAN+=1)
if exist "%ROOT%SELECCIONAR_PYTHON_REPARACION.bat" (>> "%REPORT%" echo OK     archivo  SELECCIONAR_PYTHON_REPARACION.bat) else (>> "%REPORT%" echo FALTA  archivo  SELECCIONAR_PYTHON_REPARACION.bat & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\main.py" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\main.py) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\main.py & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\player_skin_texture_atlas.png" (>> "%REPORT%" echo OK     archivo  juego3d_v1_5\player_skin_texture_atlas.png) else (>> "%REPORT%" echo FALTA  archivo  juego3d_v1_5\player_skin_texture_atlas.png & set /a FALTAN+=1)

if exist "%ROOT%juego3d_v1_5\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\ & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\motor_juegos\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\motor_juegos\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\motor_juegos\ & set /a FALTAN+=1)
if exist "%ROOT%juego3d_v1_5\assets\" (>> "%REPORT%" echo OK     carpeta  juego3d_v1_5\assets\) else (>> "%REPORT%" echo FALTA  carpeta  juego3d_v1_5\assets\ & set /a FALTAN+=1)
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
>> "%REPORT%" echo RESUMEN
>> "%REPORT%" echo -------
if "%FALTAN%"=="0" (
    >> "%REPORT%" echo Estructura: OK
) else (
    >> "%REPORT%" echo Estructura: Faltan %FALTAN% piezas.
)
>> "%REPORT%" echo Preset sugerido: %PRESET_RECOMMENDED%
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
    >> "%REPORT%" echo Despues ejecuta otra vez la opcion 12 para confirmar.
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
    >> "%REPORT%" echo Despues ejecuta otra vez la opcion 12 para confirmar.
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
