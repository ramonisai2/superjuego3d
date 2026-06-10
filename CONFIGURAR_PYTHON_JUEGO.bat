@echo off
setlocal

echo ===============================================
echo  JUEGO 1.6 - CONFIGURAR PYTHON
echo ===============================================
echo.
echo Este asistente guarda una ruta local para los lanzadores.
echo Archivo que se creara:
echo %~dp0JUEGO_PYTHON_LOCAL.bat
echo.
echo Ejemplo de ruta:
echo C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\python.exe
echo.
set /p PYTHON_RUTA=Ruta completa de python.exe: 

if "%PYTHON_RUTA%"=="" (
    echo No se escribio ninguna ruta.
    pause
    exit /b 1
)

"%PYTHON_RUTA%" -c "import sys; print(sys.executable); import numpy, pygame, OpenGL; print('numpy pygame PyOpenGL ok')" 2>nul
if errorlevel 1 (
    echo.
    echo Ese Python no pudo importar numpy, pygame y PyOpenGL.
    echo Instala dependencias o elige otra ruta.
    pause
    exit /b 1
)

>"%~dp0JUEGO_PYTHON_LOCAL.bat" echo @echo off
>>"%~dp0JUEGO_PYTHON_LOCAL.bat" echo set "JUEGO_PYTHON=%PYTHON_RUTA%"

echo.
echo Ruta guardada.
echo Ahora ejecuta VERIFICAR_ENTORNO_JUEGO.bat.
pause
