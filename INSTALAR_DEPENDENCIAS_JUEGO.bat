@echo off
setlocal

echo ===============================================
echo  JUEGO 1.6 - INSTALAR DEPENDENCIAS
echo ===============================================
echo.
echo Esto instalara los paquetes listados en:
echo %~dp0requirements_juego.txt
echo.
echo Paquetes:
type "%~dp0requirements_juego.txt"
echo.

call "%~dp0SELECCIONAR_PYTHON_REPARACION.bat"
if errorlevel 1 (
    echo No encontre ningun Python ejecutable para instalar dependencias.
    echo Si tienes Python en otra ruta, usa:
    echo set JUEGO_PYTHON=C:\Ruta\A\python.exe
    pause
    exit /b 1
)

set "PY_INSTALL_CMD=%JUEGO_PY_REPAIR_CMD%"

echo Python destino:
"%PY_INSTALL_CMD%" -c "import sys; print(sys.executable)" 2>nul
if errorlevel 1 (
    echo No se pudo ejecutar el Python destino.
    echo Si tienes Python en otra ruta, usa:
    echo set JUEGO_PYTHON=C:\Ruta\A\python.exe
    echo.
    echo O ejecuta manualmente:
    echo "C:\Ruta\A\python.exe" -m pip install -r "%~dp0requirements_juego.txt"
    pause
    exit /b 1
)
echo.
echo Origen de Python:
echo %JUEGO_PY_REPAIR_SOURCE%
echo.
echo Paquetes faltantes en ese Python:
echo %JUEGO_PY_REPAIR_MISSING%
echo.
echo Comando que se ejecutara:
echo "%PY_INSTALL_CMD%" -m pip install -r "%~dp0requirements_juego.txt"
echo.
set /p CONFIRMAR=Escribe SI para instalar ahora: 
if /i not "%CONFIRMAR%"=="SI" (
    echo Instalacion cancelada.
    pause
    exit /b 0
)

echo.
echo Instalando dependencias...
"%PY_INSTALL_CMD%" -m pip install -r "%~dp0requirements_juego.txt"
if errorlevel 1 (
    echo.
    echo La instalacion fallo. Revisa conexion, permisos o la version de Python.
    pause
    exit /b 1
)

echo.
echo Instalacion terminada.
echo Verificando Python destino reparado...
"%PY_INSTALL_CMD%" -c "import sys; print(sys.executable); import numpy, pygame, OpenGL; print('Python listo para jugar')" 2>nul
if errorlevel 1 (
    echo.
    echo La instalacion termino, pero este Python aun no pudo importar numpy, pygame y PyOpenGL.
    echo Ejecuta la opcion 3 para ver el diagnostico detallado.
    pause
    exit /b 1
)
echo.
echo Python destino listo para abrir el juego.
echo.
set /p GUARDAR=Escribe GUARDAR para recordar este Python en los lanzadores: 
if /i "%GUARDAR%"=="GUARDAR" (
    >"%~dp0JUEGO_PYTHON_LOCAL.bat" echo @echo off
    >>"%~dp0JUEGO_PYTHON_LOCAL.bat" echo set "JUEGO_PYTHON=%PY_INSTALL_CMD%"
    echo Ruta guardada en JUEGO_PYTHON_LOCAL.bat.
) else (
    echo Ruta no guardada. Podras guardarla despues con la opcion 7.
)
echo.
echo Ejecutando verificacion...
call "%~dp0VERIFICAR_ENTORNO_JUEGO.bat"
exit /b 0
