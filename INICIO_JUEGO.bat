@echo off
setlocal

:menu
cls
echo ===============================================
echo  JUEGO 1.6 - INICIO
echo ===============================================
echo.
echo  1. Jugar OpenGL estable
echo  2. Jugar OpenGL recomendado
echo  3. Verificar entorno Python
echo  4. Menu de presets OpenGL
echo  5. Ver dependencias
echo  6. Instalar dependencias
echo  7. Configurar Python del juego
echo  8. Administrar Python guardado
echo  9. Previsualizar terreno
echo 10. Log de movimiento OpenGL
echo 11. Verificar estructura del proyecto
echo 12. Estado rapido del proyecto
echo  0. Salir
echo.
set /p OPCION=Elige una opcion: 

if "%OPCION%"=="1" goto jugar_opengl
if "%OPCION%"=="2" goto jugar_recomendado
if "%OPCION%"=="3" goto verificar
if "%OPCION%"=="4" goto presets
if "%OPCION%"=="5" goto dependencias
if "%OPCION%"=="6" goto instalar
if "%OPCION%"=="7" goto configurar_python
if "%OPCION%"=="8" goto administrar_python
if "%OPCION%"=="9" goto preview
if "%OPCION%"=="10" goto perf_log
if "%OPCION%"=="11" goto verificar_estructura
if "%OPCION%"=="12" goto estado_rapido
if "%OPCION%"=="0" exit /b 0
goto menu

:jugar_opengl
call "%~dp0LANZAR_OPENGL.bat"
goto menu

:jugar_recomendado
call "%~dp0LANZAR_OPENGL_RECOMENDADO.bat"
goto menu

:verificar
call "%~dp0VERIFICAR_ENTORNO_JUEGO.bat"
goto menu

:presets
call "%~dp0PROBAR_PRESETS_OPENGL.bat"
goto menu

:dependencias
call "%~dp0MOSTRAR_COMANDO_DEPENDENCIAS.bat"
goto menu

:instalar
call "%~dp0INSTALAR_DEPENDENCIAS_JUEGO.bat"
goto menu

:configurar_python
call "%~dp0CONFIGURAR_PYTHON_JUEGO.bat"
goto menu

:administrar_python
call "%~dp0ADMINISTRAR_PYTHON_JUEGO.bat"
goto menu

:preview
call "%~dp0PREVISUALIZAR_TERRENO.bat"
goto menu

:perf_log
call "%~dp0LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat"
goto menu

:verificar_estructura
call "%~dp0VERIFICAR_ESTRUCTURA_JUEGO.bat"
goto menu

:estado_rapido
call "%~dp0ESTADO_RAPIDO_JUEGO.bat"
goto menu
