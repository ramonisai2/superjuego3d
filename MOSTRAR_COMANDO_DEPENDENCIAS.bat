@echo off
setlocal

echo ===============================================
echo  JUEGO 1.6 - DEPENDENCIAS PYTHON
echo ===============================================
echo.
echo Archivo:
echo %~dp0requirements_juego.txt
echo.
echo Comando manual basico:
echo py -m pip install -r "%~dp0requirements_juego.txt"
echo.
echo Recomendado:
echo Ejecuta INSTALAR_DEPENDENCIAS_JUEGO.bat para que elija el Python que ya tenga mas paquetes listos.
echo.
echo Si usas una ruta fija de Python, primero define:
echo set JUEGO_PYTHON=C:\Ruta\A\python.exe
echo.
echo Luego ejecuta:
echo INSTALAR_DEPENDENCIAS_JUEGO.bat
echo.
echo Si ya guardaste una ruta con CONFIGURAR_PYTHON_JUEGO.bat,
echo el instalador opcional usara esa ruta automaticamente.
echo.
echo Para guardar una ruta fija local:
echo CONFIGURAR_PYTHON_JUEGO.bat
echo.
echo O manualmente:
echo "C:\Ruta\A\python.exe" -m pip install -r "%~dp0requirements_juego.txt"
echo.
echo Despues de instalar, ejecuta:
echo VERIFICAR_ENTORNO_JUEGO.bat
echo.
echo El instalador opcional tambien verifica el mismo Python destino despues de instalar.
echo Si queda listo, puede guardar esa ruta para futuros lanzadores.
echo.
echo Instalador opcional con confirmacion:
echo INSTALAR_DEPENDENCIAS_JUEGO.bat
echo.
pause
