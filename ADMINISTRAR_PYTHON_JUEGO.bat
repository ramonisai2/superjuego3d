@echo off
setlocal

:menu
cls
echo ===============================================
echo  JUEGO 1.6 - PYTHON GUARDADO
echo ===============================================
echo.
if exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    echo Estado: hay ruta local guardada.
    call "%~dp0JUEGO_PYTHON_LOCAL.bat"
    echo Ruta: %JUEGO_PYTHON%
) else (
    echo Estado: no hay ruta local guardada.
)
echo.
echo 1. Probar ruta guardada
echo 2. Borrar ruta guardada
echo 0. Salir
echo.
set /p OPCION=Elige una opcion: 

if "%OPCION%"=="1" goto probar
if "%OPCION%"=="2" goto borrar
if "%OPCION%"=="0" exit /b 0
if "%OPCION%"=="" exit /b 0
goto menu

:probar
if not exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    echo No hay ruta guardada.
    pause
    goto menu
)
call "%~dp0JUEGO_PYTHON_LOCAL.bat"
"%JUEGO_PYTHON%" -c "import sys; print(sys.executable); import numpy, pygame, OpenGL; print('numpy pygame PyOpenGL ok')"
if errorlevel 1 (
    echo.
    echo La ruta guardada ya no parece valida para abrir el juego.
) else (
    echo.
    echo Ruta guardada valida.
)
pause
goto menu

:borrar
if not exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    echo No hay ruta guardada para borrar.
    pause
    goto menu
)
set /p CONFIRMAR=Escribe BORRAR para eliminar JUEGO_PYTHON_LOCAL.bat: 
if /i not "%CONFIRMAR%"=="BORRAR" (
    echo Cancelado.
    pause
    goto menu
)
del "%~dp0JUEGO_PYTHON_LOCAL.bat"
echo Ruta guardada borrada.
pause
goto menu
