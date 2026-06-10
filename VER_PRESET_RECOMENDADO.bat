@echo off
setlocal

pushd "%~dp0juego3d_v1_5"
set JUEGO_PRESET_ANALYZE_SESSION=all
py -m motor_juegos.preset_runtime_log_analyzer
popd

echo.
echo ===============================================
echo  PRESET RECOMENDADO ACTUAL
echo ===============================================

if exist "%~dp0juego3d_v1_5\logs\recommended_graphics_preset.txt" (
    type "%~dp0juego3d_v1_5\logs\recommended_graphics_preset.txt"
) else (
    echo Aun no hay archivo de recomendacion.
)

echo.
echo Reporte completo:
echo %~dp0juego3d_v1_5\logs\preset_runtime_report.txt
pause
