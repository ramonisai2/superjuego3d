@echo off
setlocal

echo ===============================================
echo  JUEGO 1.6 - VERIFICAR ENTORNO
echo ===============================================
echo.
if exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    echo Python local guardado: SI
) else (
    echo Python local guardado: NO
)
echo.

echo [1/2] Python para abrir el juego
set JUEGO_PY_CMD=
set JUEGO_PYTHON_CHECK=import numpy, pygame, OpenGL
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat"
if errorlevel 1 (
    set JUEGO_OK=0
) else (
    set JUEGO_OK=1
    set "PY_JUEGO=%JUEGO_PY_CMD%"
)

echo.
echo [2/2] Python para previews de terreno
set JUEGO_PY_CMD=
set JUEGO_PYTHON_CHECK=import numpy; from PIL import Image
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat"
if errorlevel 1 (
    set PREVIEW_OK=0
) else (
    set PREVIEW_OK=1
    set "PY_PREVIEW=%JUEGO_PY_CMD%"
)

echo.
echo ===============================================
echo  RESULTADO
echo ===============================================
if "%JUEGO_OK%"=="1" (
    echo Juego: OK
    echo Python juego: %PY_JUEGO%
) else (
    echo Juego: FALTA Python con numpy, pygame y PyOpenGL
)

if "%PREVIEW_OK%"=="1" (
    echo Previews: OK
    echo Python previews: %PY_PREVIEW%
) else (
    echo Previews: FALTA Python con numpy y PIL
)

echo.
if not "%JUEGO_OK%"=="1" (
    echo Para forzar una ruta de Python:
    echo set JUEGO_PYTHON=C:\Ruta\A\python.exe
    echo.
    echo Para guardar una ruta fija local:
    echo CONFIGURAR_PYTHON_JUEGO.bat
    echo.
    echo Para revisar o borrar la ruta guardada:
    echo ADMINISTRAR_PYTHON_JUEGO.bat
    echo.
    echo Para ver el comando de instalacion de dependencias:
    echo MOSTRAR_COMANDO_DEPENDENCIAS.bat
    echo.
    echo Para instalar con confirmacion:
    echo INSTALAR_DEPENDENCIAS_JUEGO.bat
    echo.
    echo ===============================================
    echo  DIAGNOSTICO DETALLADO
    echo ===============================================
    echo.
    call :diagnostico_python
)
pause
exit /b 0

:diagnostico_python
if exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    call "%~dp0JUEGO_PYTHON_LOCAL.bat"
    if defined JUEGO_PYTHON call :probar_paquetes "guardado" "%JUEGO_PYTHON%"
)
if defined JUEGO_PYTHON call :probar_paquetes "variable JUEGO_PYTHON" "%JUEGO_PYTHON%"
call :probar_paquetes "python" python
call :probar_paquetes "py" py
call :probar_paquetes "Python312 usuario" "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :probar_paquetes "Python311 usuario" "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
call :probar_paquetes "Python310 usuario" "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
call :probar_paquetes "Python39 usuario" "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
call :probar_paquetes "Python Codex preview" "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
exit /b 0

:probar_paquetes
set "PY_LABEL=%~1"
set "PY_CANDIDATO=%~2"
if "%PY_CANDIDATO%"=="" exit /b 0
echo [%PY_LABEL%]
"%PY_CANDIDATO%" -c "import sys, importlib.util as u; mods=[('numpy','numpy'),('pygame','pygame'),('PyOpenGL','OpenGL'),('Pillow','PIL')]; missing=[name for name,mod in mods if u.find_spec(mod) is None]; print(sys.executable); print('OK todos los paquetes' if not missing else 'FALTAN: ' + ', '.join(missing))" 2>nul
if errorlevel 1 echo No ejecuta o no existe.
echo.
exit /b 0
