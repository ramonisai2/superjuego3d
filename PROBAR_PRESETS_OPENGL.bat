@echo off
setlocal

:menu
cls
echo ===============================================
echo  JUEGO 1.6 - PRUEBA DE PRESETS OPENGL
echo ===============================================
echo.
echo  1. Limpiar log de presets
echo  2. Probar LOW / Bajo FPS
echo  3. Probar BALANCED / Recomendado
echo  4. Probar HIGH / Alto detalle
echo  5. Analizar todo el historial
echo  6. Analizar ultima sesion
echo  7. Ver ultimo reporte
echo  8. Probar preset recomendado
echo  9. Ver preset recomendado
echo 10. Verificar entorno Python
echo 11. Ver comando de dependencias
echo 12. Instalar dependencias
echo 13. Configurar Python del juego
echo 14. Administrar Python guardado
echo  0. Salir
echo.
set /p OPCION=Elige una opcion: 

if "%OPCION%"=="1" goto limpiar
if "%OPCION%"=="2" goto probar_low
if "%OPCION%"=="3" goto probar_balanced
if "%OPCION%"=="4" goto probar_high
if "%OPCION%"=="5" goto analizar_todo
if "%OPCION%"=="6" goto analizar_ultima
if "%OPCION%"=="7" goto ver_reporte
if "%OPCION%"=="8" goto probar_recomendado
if "%OPCION%"=="9" goto ver_recomendado
if "%OPCION%"=="10" goto verificar_entorno
if "%OPCION%"=="11" goto ver_dependencias
if "%OPCION%"=="12" goto instalar_dependencias
if "%OPCION%"=="13" goto configurar_python
if "%OPCION%"=="14" goto administrar_python
if "%OPCION%"=="0" goto salir
goto menu

:limpiar
if exist "%~dp0juego3d_v1_5\logs\preset_runtime_samples.log" (
    del "%~dp0juego3d_v1_5\logs\preset_runtime_samples.log"
    echo Log de presets limpiado.
) else (
    echo No habia log de presets para limpiar.
)
pause
goto menu

:probar_low
call :probar_preset low opengl_low
goto menu

:probar_balanced
call :probar_preset balanced opengl_balanced
goto menu

:probar_high
call :probar_preset high opengl_high
goto menu

:analizar_todo
pushd "%~dp0juego3d_v1_5"
set JUEGO_PRESET_ANALYZE_SESSION=all
py -m motor_juegos.preset_runtime_log_analyzer
popd
pause
goto menu

:analizar_ultima
pushd "%~dp0juego3d_v1_5"
set JUEGO_PRESET_ANALYZE_SESSION=latest
py -m motor_juegos.preset_runtime_log_analyzer
popd
pause
goto menu

:ver_reporte
if exist "%~dp0juego3d_v1_5\logs\preset_runtime_report.txt" (
    type "%~dp0juego3d_v1_5\logs\preset_runtime_report.txt"
) else (
    echo Aun no hay reporte. Usa primero la opcion 5 o 6.
)
pause
goto menu

:probar_recomendado
call "%~dp0LANZAR_OPENGL_RECOMENDADO.bat"
goto menu

:ver_recomendado
call "%~dp0VER_PRESET_RECOMENDADO.bat"
goto menu

:verificar_entorno
call "%~dp0VERIFICAR_ENTORNO_JUEGO.bat"
goto menu

:ver_dependencias
call "%~dp0MOSTRAR_COMANDO_DEPENDENCIAS.bat"
goto menu

:instalar_dependencias
call "%~dp0INSTALAR_DEPENDENCIAS_JUEGO.bat"
goto menu

:configurar_python
call "%~dp0CONFIGURAR_PYTHON_JUEGO.bat"
goto menu

:administrar_python
call "%~dp0ADMINISTRAR_PYTHON_JUEGO.bat"
goto menu

:probar_preset
pushd "%~dp0juego3d_v1_5"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_GRAPHICS_PRESET=%~1
set JUEGO_PRESET_SAMPLE_LOG=1
set JUEGO_PRESET_SAMPLE_SESSION=%~2_%RANDOM%
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat" || (popd & pause & exit /b 1)
"%JUEGO_PY_CMD%" -m motor_juegos.render_mode_status
"%JUEGO_PY_CMD%" main.py
popd
pause
exit /b

:salir
exit /b
