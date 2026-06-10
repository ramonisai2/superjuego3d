@echo off
cd /d "%~dp0juego3d_v1_5"
if not exist logs mkdir logs
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=1
set JUEGO_STREAM_BRIDGE_PRESET=safe
set JUEGO_PERF_LOG=1
echo Camina 1-2 minutos. Guardando log en juego3d_v1_5\logs\perf_movimiento_opengl_bridge_safe.log
python main.py > logs\perf_movimiento_opengl_bridge_safe.log 2>&1
pause
