@echo off
cd /d "%~dp0juego3d_v1_5"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_GRAPHICS_PRESET=low
set JUEGO_PRESET_SAMPLE_LOG=1
set JUEGO_PRESET_SAMPLE_SESSION=opengl_low_%RANDOM%
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat" || (pause & exit /b 1)
"%JUEGO_PY_CMD%" -m motor_juegos.render_mode_status
"%JUEGO_PY_CMD%" main.py
pause
