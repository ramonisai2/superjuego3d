@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=0
set JUEGO_PERF_LOG=1
echo Camina 1-2 minutos. Guardando log en logs\perf_movimiento_opengl_legacy.log
python main.py > logs\perf_movimiento_opengl_legacy.log 2>&1
pause
