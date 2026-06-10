@echo off
cd /d "%~dp0juego3d_v1_5"
if not exist logs mkdir logs
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_STREAM_BRIDGE_SAFE=0
set JUEGO_PERF_LOG=1
echo Camina 1-2 minutos. Guardando log en juego3d_v1_5\logs\perf_movimiento_opengl_legacy.log
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat" || (pause & exit /b 1)
"%JUEGO_PY_CMD%" main.py > logs\perf_movimiento_opengl_legacy.log 2>&1
pause
