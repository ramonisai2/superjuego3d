@echo off
set "JUEGO_PY_CMD="

if not defined JUEGO_PYTHON_CHECK set "JUEGO_PYTHON_CHECK=import numpy, pygame, OpenGL"
if exist "%~dp0JUEGO_PYTHON_LOCAL.bat" call "%~dp0JUEGO_PYTHON_LOCAL.bat"

if defined JUEGO_PYTHON call :probar_python "%JUEGO_PYTHON%"
call :probar_python python
call :probar_python py
call :probar_python "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :probar_python "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
call :probar_python "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
call :probar_python "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
call :probar_python "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not defined JUEGO_PY_CMD (
    echo No encontre un Python valido para este lanzador.
    echo Requisito comprobado: %JUEGO_PYTHON_CHECK%
    echo.
    echo Si tienes Python instalado en otra ruta, define JUEGO_PYTHON antes de lanzar.
    echo Ejemplo:
    echo set JUEGO_PYTHON=C:\Ruta\A\python.exe
    exit /b 1
)

echo Python seleccionado: %JUEGO_PY_CMD%
exit /b 0

:probar_python
if defined JUEGO_PY_CMD exit /b 0
set "CANDIDATO=%~1"
if "%CANDIDATO%"=="" exit /b 0
"%CANDIDATO%" -c "%JUEGO_PYTHON_CHECK%" >nul 2>nul
if not errorlevel 1 set "JUEGO_PY_CMD=%CANDIDATO%"
exit /b 0
