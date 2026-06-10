@echo off
cd /d "%~dp0juego3d_v1_5"
set JUEGO_PYTHON_CHECK=import numpy; from PIL import Image
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat" || (pause & exit /b 1)
"%JUEGO_PY_CMD%" previsualizar_metodos_terreno.py
pause
