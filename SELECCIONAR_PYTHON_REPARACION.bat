@echo off
set "JUEGO_PY_REPAIR_CMD="
set "JUEGO_PY_REPAIR_SOURCE="
set "JUEGO_PY_REPAIR_MISSING=sin diagnostico"
set "JUEGO_PY_REPAIR_SCORE=-1"

if exist "%~dp0JUEGO_PYTHON_LOCAL.bat" (
    call "%~dp0JUEGO_PYTHON_LOCAL.bat"
    if defined JUEGO_PYTHON (
        set "JUEGO_PY_REPAIR_CMD=%JUEGO_PYTHON%"
        set "JUEGO_PY_REPAIR_SOURCE=JUEGO_PYTHON_LOCAL.bat"
        call :read_missing "%JUEGO_PYTHON%"
        exit /b 0
    )
)

if defined JUEGO_PYTHON (
    set "JUEGO_PY_REPAIR_CMD=%JUEGO_PYTHON%"
    set "JUEGO_PY_REPAIR_SOURCE=JUEGO_PYTHON"
    call :read_missing "%JUEGO_PYTHON%"
    exit /b 0
)

call :consider_python "python" python
call :consider_python "py" py
call :consider_python "Python312 usuario" "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :consider_python "Python311 usuario" "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
call :consider_python "Python310 usuario" "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
call :consider_python "Python39 usuario" "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
call :consider_python "Python Codex preview" "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not defined JUEGO_PY_REPAIR_CMD exit /b 1
exit /b 0

:consider_python
set "PY_LABEL=%~1"
set "PY_CANDIDATO=%~2"
set "PY_SCORE="
set "PY_MISSING="
if "%PY_CANDIDATO%"=="" exit /b 0
set "PY_SCORE_FILE=%TEMP%\juego_python_score_%RANDOM%_%RANDOM%.txt"
"%PY_CANDIDATO%" "%~dp0juego3d_v1_5\motor_juegos\python_dependency_score.py" > "%PY_SCORE_FILE%" 2>nul
if errorlevel 1 (
    if exist "%PY_SCORE_FILE%" del "%PY_SCORE_FILE%" >nul 2>nul
    exit /b 0
)
for /f "usebackq tokens=1,* delims=|" %%A in ("%PY_SCORE_FILE%") do (
    set "PY_SCORE=%%A"
    set "PY_MISSING=%%B"
)
if exist "%PY_SCORE_FILE%" del "%PY_SCORE_FILE%" >nul 2>nul
if not defined PY_SCORE exit /b 0
if %PY_SCORE% GTR %JUEGO_PY_REPAIR_SCORE% (
    set "JUEGO_PY_REPAIR_SCORE=%PY_SCORE%"
    set "JUEGO_PY_REPAIR_CMD=%PY_CANDIDATO%"
    set "JUEGO_PY_REPAIR_SOURCE=%PY_LABEL%"
    set "JUEGO_PY_REPAIR_MISSING=%PY_MISSING%"
)
exit /b 0

:read_missing
set "PY_READ_CMD=%~1"
set "JUEGO_PY_REPAIR_MISSING=sin diagnostico"
if "%PY_READ_CMD%"=="" exit /b 0
set "PY_SCORE_FILE=%TEMP%\juego_python_score_%RANDOM%_%RANDOM%.txt"
"%PY_READ_CMD%" "%~dp0juego3d_v1_5\motor_juegos\python_dependency_score.py" > "%PY_SCORE_FILE%" 2>nul
if errorlevel 1 (
    if exist "%PY_SCORE_FILE%" del "%PY_SCORE_FILE%" >nul 2>nul
    exit /b 0
)
for /f "usebackq tokens=1,* delims=|" %%A in ("%PY_SCORE_FILE%") do (
    set "JUEGO_PY_REPAIR_SCORE=%%A"
    set "JUEGO_PY_REPAIR_MISSING=%%B"
)
if exist "%PY_SCORE_FILE%" del "%PY_SCORE_FILE%" >nul 2>nul
exit /b 0
