@echo off
cd /d "%~dp0juego3d_v1_5"
if not exist logs mkdir logs
if exist logs\preset_runtime_samples.log del logs\preset_runtime_samples.log
echo Log de presets limpiado.
pause
