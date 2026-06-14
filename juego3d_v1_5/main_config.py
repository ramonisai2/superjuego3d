"""Configuracion principal de main.py.

Este modulo existe para que main.py pueda ir bajando de tamano sin cambiar
los nombres que ya usa el loop del juego.
"""

from __future__ import annotations

import os
import random
import time

from motor_juegos.env_config import read_env_bool, read_env_float, read_env_int, read_env_text


ANCHO = 1280
ALTO = 720
SEMILLA_MUNDO = random.randint(1, 1000000)
GRAPHICS_PRESET = read_env_text("JUEGO_GRAPHICS_PRESET", "balanced", lower=True) or "balanced"
GRAPHICS_PRESETS = {
    "low": {
        "subdivisiones": 40,
        "radio_vision": 2,
        "radio_detalle": 1,
        "subdivisiones_lod": 8,
        "lods_por_tanda": 1,
        "chunk_render_extra": 1.10,
        "chunk_render_min_extra": 1.10,
        "detail_render_extra": 0.90,
        "detail_near_keep": 1.05,
        "detail_back_margin": 0.02,
        "entity_render_distance": 88.0,
        "entity_label_distance": 34.0,
        "entity_full_detail": 22.0,
        "entity_mid_detail": 48.0,
        "remnant_render_distance": 34.0,
    },
    "balanced": {
        "subdivisiones": 48,
        "radio_vision": 2,
        "radio_detalle": 1,
        "subdivisiones_lod": 10,
        "lods_por_tanda": 2,
        "chunk_render_extra": 1.35,
        "chunk_render_min_extra": 1.25,
        "detail_render_extra": 1.05,
        "detail_near_keep": 1.25,
        "detail_back_margin": 0.08,
        "entity_render_distance": 125.0,
        "entity_label_distance": 48.0,
        "entity_full_detail": 34.0,
        "entity_mid_detail": 72.0,
        "remnant_render_distance": 58.0,
    },
    "high": {
        "subdivisiones": 56,
        "radio_vision": 3,
        "radio_detalle": 1,
        "subdivisiones_lod": 12,
        "lods_por_tanda": 2,
        "chunk_render_extra": 1.65,
        "chunk_render_min_extra": 1.35,
        "detail_render_extra": 1.25,
        "detail_near_keep": 1.55,
        "detail_back_margin": 0.14,
        "entity_render_distance": 155.0,
        "entity_label_distance": 58.0,
        "entity_full_detail": 44.0,
        "entity_mid_detail": 96.0,
        "remnant_render_distance": 72.0,
    },
}
if GRAPHICS_PRESET not in GRAPHICS_PRESETS:
    GRAPHICS_PRESET = "balanced"
os.environ["JUEGO_GRAPHICS_PRESET"] = GRAPHICS_PRESET
GRAPHICS_SETTINGS = GRAPHICS_PRESETS.get(GRAPHICS_PRESET, GRAPHICS_PRESETS["balanced"])

CHUNK_SIZE = 64
SUBDIVISIONES = read_env_int("JUEGO_SUBDIVISIONES", GRAPHICS_SETTINGS["subdivisiones"])
RADIO_VISION = read_env_int("JUEGO_RADIO_VISION", GRAPHICS_SETTINGS["radio_vision"])
RADIO_DETALLE = read_env_int("JUEGO_RADIO_DETALLE", GRAPHICS_SETTINGS["radio_detalle"])
SUBDIVISIONES_LOD = read_env_int("JUEGO_SUBDIVISIONES_LOD", GRAPHICS_SETTINGS["subdivisiones_lod"])
MAX_COLA_PETICIONES = 3
CHUNKS_COMPILAR_POR_FRAME = 1
LODS_CREAR_POR_TANDA = read_env_int("JUEGO_LOD_CREAR_POR_TANDA", GRAPHICS_SETTINGS["lods_por_tanda"])
ENABLE_STREAM_BRIDGE_SAFE = read_env_bool("JUEGO_STREAM_BRIDGE_SAFE", False)
DEBUG_RENDER_ALL_CHUNKS = read_env_bool("JUEGO_DEBUG_RENDER_ALL_CHUNKS", False)
DEBUG_RENDER_ALL_ENTITIES = read_env_bool("JUEGO_DEBUG_RENDER_ALL_ENTITIES", False)

ADAPTIVE_QUALITY_ENABLED = read_env_bool("JUEGO_ADAPTIVE_QUALITY", True)
ADAPTIVE_FPS_LOW = read_env_float("JUEGO_ADAPTIVE_FPS_LOW", 28.0)
ADAPTIVE_FPS_HIGH = read_env_float("JUEGO_ADAPTIVE_FPS_HIGH", 48.0)
ADAPTIVE_CHUNK_RENDER_ENABLED = read_env_bool("JUEGO_ADAPTIVE_CHUNKS", True)
ADAPTIVE_STREAMING_ENABLED = read_env_bool("JUEGO_ADAPTIVE_STREAMING", True)
ADAPTIVE_RESCUE_ENABLED = read_env_bool("JUEGO_FRAME_RESCUE", True)
ADAPTIVE_RESCUE_FPS = read_env_float("JUEGO_FRAME_RESCUE_FPS", 34.0)
ADAPTIVE_EMERGENCY_FPS = read_env_float("JUEGO_FRAME_EMERGENCY_FPS", 24.0)
PRESET_SAMPLE_LOG_ENABLED = read_env_bool("JUEGO_PRESET_SAMPLE_LOG", True)
PRESET_SAMPLE_LOG_INTERVAL = read_env_float("JUEGO_PRESET_SAMPLE_LOG_INTERVAL", 3.0)
PRESET_SAMPLE_SESSION = read_env_text("JUEGO_PRESET_SAMPLE_SESSION", "") or time.strftime("%Y%m%d_%H%M%S")

CHUNK_RENDER_EXTRA = read_env_float("JUEGO_CHUNK_RENDER_EXTRA", GRAPHICS_SETTINGS.get("chunk_render_extra", 1.8))
CHUNK_RENDER_MIN_EXTRA = read_env_float("JUEGO_CHUNK_RENDER_MIN_EXTRA", GRAPHICS_SETTINGS.get("chunk_render_min_extra", CHUNK_RENDER_EXTRA))
DETAIL_CHUNK_RENDER_EXTRA = read_env_float("JUEGO_DETAIL_CHUNK_RENDER_EXTRA", GRAPHICS_SETTINGS.get("detail_render_extra", 1.8))
DETAIL_CHUNK_NEAR_KEEP = read_env_float("JUEGO_DETAIL_CHUNK_NEAR_KEEP", GRAPHICS_SETTINGS.get("detail_near_keep", 2.05))
DETAIL_CHUNK_BACK_MARGIN = read_env_float("JUEGO_DETAIL_CHUNK_BACK_MARGIN", GRAPHICS_SETTINGS.get("detail_back_margin", 0.28))
ENTITY_RENDER_DISTANCE = read_env_float("JUEGO_ENTITY_RENDER_DISTANCE", GRAPHICS_SETTINGS["entity_render_distance"])
ENTITY_LABEL_DISTANCE = read_env_float("JUEGO_ENTITY_LABEL_DISTANCE", GRAPHICS_SETTINGS["entity_label_distance"])
ENTITY_FULL_DETAIL_DISTANCE = read_env_float("JUEGO_ENTITY_FULL_DETAIL_DISTANCE", GRAPHICS_SETTINGS["entity_full_detail"])
ENTITY_MID_DETAIL_DISTANCE = read_env_float("JUEGO_ENTITY_MID_DETAIL_DISTANCE", GRAPHICS_SETTINGS["entity_mid_detail"])
REMNANT_RENDER_DISTANCE = read_env_float("JUEGO_REMNANT_RENDER_DISTANCE", GRAPHICS_SETTINGS["remnant_render_distance"])

WATER_QUERY_GRID = 0.75
TOTAL_HEIGHT_QUERY_GRID = 0.25
RESOURCE_CELL_SIZE = 4.0
ROCK_COLLISION_CELL_SIZE = 4.0
WORLD_CONTEXT_INTERVAL = 0.18
WORLD_CONTEXT_MOVE_STEP = 1.25
NPC_FULL_AI_DISTANCE = 36.0
NPC_FAR_AI_INTERVAL = 0.35
ENEMY_FULL_AI_DISTANCE = 42.0
ENEMY_FAR_AI_INTERVAL = 0.25
SPAWN_CHUNK_X = 0
SPAWN_CHUNK_Z = 0
SPAWN_CENTER_X = SPAWN_CHUNK_X * CHUNK_SIZE + CHUNK_SIZE * 0.5
SPAWN_CENTER_Z = SPAWN_CHUNK_Z * CHUNK_SIZE + CHUNK_SIZE * 0.5
