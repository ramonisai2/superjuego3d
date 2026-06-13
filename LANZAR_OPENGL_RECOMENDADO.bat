@echo off
setlocal

set JUEGO_RECOMMENDED_PRESET=balanced
set JUEGO_RECOMMENDED_CONFIDENCE=low
set JUEGO_RECOMMENDED_FILE=%~dp0juego3d_v1_5\logs\recommended_graphics_preset.txt

pushd "%~dp0juego3d_v1_5"
set JUEGO_PRESET_ANALYZE_SESSION=all
py -m motor_juegos.preset_runtime_log_analyzer
popd

if exist "%JUEGO_RECOMMENDED_FILE%" (
    for /f "usebackq tokens=1,2 delims==" %%A in ("%JUEGO_RECOMMENDED_FILE%") do (
        if "%%A"=="preset" set JUEGO_RECOMMENDED_PRESET=%%B
        if "%%A"=="confidence" set JUEGO_RECOMMENDED_CONFIDENCE=%%B
    )
)

if /i not "%JUEGO_RECOMMENDED_PRESET%"=="low" if /i not "%JUEGO_RECOMMENDED_PRESET%"=="balanced" if /i not "%JUEGO_RECOMMENDED_PRESET%"=="high" (
    set JUEGO_RECOMMENDED_PRESET=balanced
    set JUEGO_RECOMMENDED_CONFIDENCE=low
)

cd /d "%~dp0juego3d_v1_5"
set JUEGO_RENDER_BACKEND=opengl
set JUEGO_GRAPHICS_PRESET=%JUEGO_RECOMMENDED_PRESET%
set JUEGO_PRESET_SAMPLE_LOG=1
set JUEGO_PRESET_SAMPLE_SESSION=opengl_recommended_%JUEGO_RECOMMENDED_PRESET%_%RANDOM%
echo Preset recomendado: %JUEGO_RECOMMENDED_PRESET%  confianza: %JUEGO_RECOMMENDED_CONFIDENCE%
if /i not "%JUEGO_RECOMMENDED_CONFIDENCE%"=="ok" (
    echo Advertencia: el preset recomendado requiere atencion. Revisa opcion 9 o el reporte de presets.
)
call "%~dp0SELECCIONAR_PYTHON_JUEGO.bat" || (pause & exit /b 1)
"%JUEGO_PY_CMD%" -m motor_juegos.render_mode_status
"%JUEGO_PY_CMD%" main.py
pause
