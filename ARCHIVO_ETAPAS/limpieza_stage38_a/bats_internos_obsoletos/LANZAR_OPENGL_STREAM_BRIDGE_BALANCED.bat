@echo off
cd /d "%~dp0"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=1
set JUEGO_STREAM_BRIDGE_PRESET=balanced
python main.py
pause
