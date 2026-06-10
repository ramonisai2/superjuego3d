@echo off
cd /d "%~dp0"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=1
python main.py
pause
