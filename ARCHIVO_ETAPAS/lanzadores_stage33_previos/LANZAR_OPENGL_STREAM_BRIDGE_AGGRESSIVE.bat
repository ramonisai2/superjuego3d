@echo off
cd /d "%~dp0juego3d_v1_5"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=1
set JUEGO_STREAM_BRIDGE_PRESET=aggressive
python main.py
pause
