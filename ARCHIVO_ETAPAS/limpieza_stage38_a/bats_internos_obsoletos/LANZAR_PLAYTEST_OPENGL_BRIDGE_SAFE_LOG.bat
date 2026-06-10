@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=1
set JUEGO_STREAM_BRIDGE_PRESET=safe
echo Guardando log en logs\playtest_opengl_bridge_safe.log
python main.py > logs\playtest_opengl_bridge_safe.log 2>&1
pause
