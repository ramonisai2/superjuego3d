#!/usr/bin/env bash
cd "$(dirname "$0")"
export JUEGO_RENDER_BACKEND=vulkan_present
python3 main.py
