@echo off
cd /d "%~dp0"
set JUEGO_RENDER_BACKEND=vulkan_present
python -m motor_juegos.render_mode_status
python main.py
pause
