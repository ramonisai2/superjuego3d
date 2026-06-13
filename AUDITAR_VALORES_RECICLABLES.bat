@echo off
setlocal

set "ROOT=%~dp0"
set "JUEGO_PY_CMD="
set "JUEGO_PYTHON_CHECK=import ast, pathlib"
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat"
if errorlevel 1 (
    echo No se encontro Python basico para auditar valores.
    pause
    exit /b 1
)

pushd "%ROOT%juego3d_v1_5"
"%JUEGO_PY_CMD%" auditar_valores_reciclables.py
set "ERR=%ERRORLEVEL%"
popd

echo.
if "%ERR%"=="0" (
    echo Reporte guardado en juego3d_v1_5\logs\valores_reciclables_report.txt
) else (
    echo La auditoria de valores fallo.
)
echo.
pause
exit /b %ERR%
