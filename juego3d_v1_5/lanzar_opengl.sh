#!/usr/bin/env bash
cd "$(dirname "$0")"
export JUEGO_RENDER_BACKEND=opengl
python3 main.py
