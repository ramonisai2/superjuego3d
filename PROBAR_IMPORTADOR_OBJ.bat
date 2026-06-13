@echo off
setlocal

set "ROOT=%~dp0"
set "JUEGO_PY_CMD="
set "JUEGO_PYTHON_CHECK=import pathlib"
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat"
if errorlevel 1 (
    echo No se encontro Python para probar el importador OBJ.
    echo Esta prueba solo necesita Python basico.
    pause
    exit /b 1
)

pushd "%ROOT%juego3d_v1_5"
"%JUEGO_PY_CMD%" probar_importador_obj.py
set "ERR=%ERRORLEVEL%"
popd

if "%ERR%"=="0" (
    echo.
    echo Importador OBJ verificado.
) else (
    echo.
    echo La prueba del importador OBJ fallo.
)
echo.
pause
exit /b %ERR%
