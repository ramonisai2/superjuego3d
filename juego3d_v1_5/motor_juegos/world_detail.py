"""Tuning de detalle visual del mundo procedural."""

from .env_config import read_env_float, read_env_int, read_env_text
# Modo agresivo de rendimiento: reduce instancias pequeñas y geometría pesada.
PERF_AGGRESSIVE = True
GRASS_DENSITY = 0.35
DECO_DENSITY = 0.35
ROCK_DENSITY = 0.55
OASIS_TREE_DENSITY = 0.25
WATER_SURFACE_MAX_ABOVE_GROUND = 0.018

WORLD_DETAIL_PROFILES = {
    "low": {"grass": 0.20, "deco": 0.22, "rock": 0.42, "oasis_tree": 0.15, "grass_planes": 1, "deco_planes": 1, "leaf_planes": 2, "tree_layers": 1, "rock_detail": 1},
    "balanced": {"grass": GRASS_DENSITY, "deco": DECO_DENSITY, "rock": ROCK_DENSITY, "oasis_tree": OASIS_TREE_DENSITY, "grass_planes": 2, "deco_planes": 2, "leaf_planes": 3, "tree_layers": 2, "rock_detail": 2},
    "high": {"grass": 0.48, "deco": 0.48, "rock": 0.70, "oasis_tree": 0.38, "grass_planes": 2, "deco_planes": 2, "leaf_planes": 3, "tree_layers": 2, "rock_detail": 2},
}


def _world_detail_density():
    preset = read_env_text("JUEGO_WORLD_DETAIL_PRESET", "", lower=True)
    if not preset:
        preset = read_env_text("JUEGO_GRAPHICS_PRESET", "balanced", lower=True) or "balanced"
    profile = dict(WORLD_DETAIL_PROFILES.get(preset, WORLD_DETAIL_PROFILES["balanced"]))
    profile["grass"] = read_env_float("JUEGO_GRASS_DENSITY", profile["grass"], 0.0, 1.25)
    profile["deco"] = read_env_float("JUEGO_DECO_DENSITY", profile["deco"], 0.0, 1.25)
    profile["rock"] = read_env_float("JUEGO_ROCK_DENSITY", profile["rock"], 0.0, 1.25)
    profile["oasis_tree"] = read_env_float("JUEGO_OASIS_TREE_DENSITY", profile["oasis_tree"], 0.0, 1.25)
    profile["grass_planes"] = read_env_int("JUEGO_GRASS_PLANES", profile["grass_planes"], 1, 2)
    profile["deco_planes"] = read_env_int("JUEGO_DECO_PLANES", profile["deco_planes"], 1, 2)
    profile["leaf_planes"] = read_env_int("JUEGO_LEAF_PLANES", profile["leaf_planes"], 1, 3)
    profile["tree_layers"] = read_env_int("JUEGO_TREE_LAYERS", profile["tree_layers"], 1, 2)
    profile["rock_detail"] = read_env_int("JUEGO_ROCK_DETAIL", profile["rock_detail"], 1, 2)
    profile["preset"] = preset if preset in WORLD_DETAIL_PROFILES else "balanced"
    return profile


def get_world_detail_density_status():
    return dict(_world_detail_density())
