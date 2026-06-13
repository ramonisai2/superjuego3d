@echo off
setlocal

set "ROOT=%~dp0"
set "JUEGO_PY_CMD="
set "JUEGO_PYTHON_CHECK=import pathlib"
call "%ROOT%SELECCIONAR_PYTHON_JUEGO.bat"
if errorlevel 1 (
    echo No se encontro Python para ejecutar la auditoria.
    pause
    exit /b 1
)

pushd "%ROOT%juego3d_v1_5" >nul
"%JUEGO_PY_CMD%" auditar_tamano_py.py
set "ERR=%ERRORLEVEL%"
popd >nul

echo.
if "%ERR%"=="0" (
    echo Reporte generado en juego3d_v1_5\logs\tamano_py_report.txt
) else (
    echo La auditoria fallo con codigo %ERR%.
)
pause
exit /b %ERR%
