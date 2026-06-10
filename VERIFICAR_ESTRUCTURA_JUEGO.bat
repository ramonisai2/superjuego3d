@echo off
setlocal

set "FALTAN=0"

echo ===============================================
echo  JUEGO 1.6 - VERIFICAR ESTRUCTURA
echo ===============================================
echo.

call :check_file "INICIO_JUEGO.bat"
call :check_file "LEEME_PRIMERO.txt"
call :check_file "requirements_juego.txt"
call :check_file "LANZAR_OPENGL.bat"
call :check_file "LANZAR_OPENGL_RECOMENDADO.bat"
call :check_file "PROBAR_PRESETS_OPENGL.bat"
call :check_file "VERIFICAR_ENTORNO_JUEGO.bat"
call :check_file "SELECCIONAR_PYTHON_JUEGO.bat"
call :check_file "juego3d_v1_5\main.py"
call :check_file "juego3d_v1_5\player_skin_texture_atlas.png"

call :check_dir "juego3d_v1_5"
call :check_dir "juego3d_v1_5\motor_juegos"
call :check_dir "juego3d_v1_5\assets"
call :check_dir "ARCHIVO_ETAPAS"

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

:check_file
if exist "%~dp0%~1" (
    echo OK     archivo  %~1
) else (
    echo FALTA  archivo  %~1
    set /a FALTAN+=1
)
exit /b 0

:check_dir
if exist "%~dp0%~1\" (
    echo OK     carpeta  %~1
) else (
    echo FALTA  carpeta  %~1
    set /a FALTAN+=1
)
exit /b 0
