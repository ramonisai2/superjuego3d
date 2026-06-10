@echo off
cd /d "%~dp0juego3d_v1_5"
if not exist logs mkdir logs
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=0
echo Guardando log en juego3d_v1_5\logs\playtest_opengl_legacy.log
python main.py > logs\playtest_opengl_legacy.log 2>&1
pause
