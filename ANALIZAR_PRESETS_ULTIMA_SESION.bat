@echo off
cd /d "%~dp0juego3d_v1_5"
set JUEGO_PRESET_ANALYZE_SESSION=latest
py -m motor_juegos.preset_runtime_log_analyzer
pause
