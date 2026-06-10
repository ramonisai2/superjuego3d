@echo off
cd /d "%~dp0"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_TERRAIN_MODE=fast_noise
python main.py
pause
