@echo off
title JUEGO 1.6 - Lanzador rapido
cd /d "%~dp0"
echo ================================
echo   JUEGO 1.6 - LANZADOR RAPIDO
echo ================================
echo.
echo Iniciando el juego...
echo Si falta alguna dependencia, ejecuta:
echo pip install pygame PyOpenGL numpy
echo.
python main.py
pause
