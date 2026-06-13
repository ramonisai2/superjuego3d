"""Informacion visible de version/actualizacion."""

GAME_VERSION = "JUEGO 1.6"
STAGE_NAME = "Stage39 T"
UPDATE_CODENAME = "MAIN CHUNK RUNTIME MODULE"
UPDATE_SUBTITLE = "Separar streaming chunks"

def full_update_name():
    return f"{STAGE_NAME} - {UPDATE_CODENAME}"

UPDATE_DESCRIPTION = "Streaming, LOD, worker y compilacion de chunks viven en main_chunk_runtime.py"
