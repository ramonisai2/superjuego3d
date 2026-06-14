"""Masa de bosque lejana basada en el terreno real.

No crea una pared falsa: usa el seed y los campos de terreno para colocar
impostores oscuros donde la humedad/bioma indican bosque o pantano.
"""

try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    # Permite compilar/auditar sin PyOpenGL instalado.
    pass
import math

import numpy as np

from . import biomes
from .env_config import read_env_bool, read_env_float, read_env_int


_forest_cache = {}
_forest_order = []
_last_candidate_lock = {
    "key": None,
    "candidates": None,
}
_stats = {
    "enabled": 0,
    "tiles_visible": 0,
    "tiles_built": 0,
    "trees_drawn": 0,
    "tiles_cached": 0,
}


def forest_impostor_stats():
    return dict(_stats)


def draw_forest_impostor_lod(env_module, px, py, pz, seed, rescue=None):
    if not read_env_bool("JUEGO_FOREST_IMPOSTORS_ENABLED", True):
        _stats.update({"enabled": 0, "tiles_visible": 0, "tiles_built": 0, "trees_drawn": 0, "tiles_cached": len(_forest_cache)})
        return
    rescue = rescue or {}

    tile_size = read_env_float("JUEGO_FOREST_IMPOSTOR_TILE_SIZE", 160.0, 64.0, 384.0)
    samples = read_env_int("JUEGO_FOREST_IMPOSTOR_SAMPLES", 5, 3, 9)
    base_radius = read_env_int("JUEGO_FOREST_IMPOSTOR_RADIUS", 4, 2, 7)
    inner_base = read_env_int("JUEGO_FOREST_IMPOSTOR_INNER_RADIUS", 2, 0, base_radius - 1)
    radius = max(inner_base + 1, int(round(base_radius * float(rescue.get("forest_radius_scale", 1.0)))))
    inner_radius = max(0, min(inner_base, radius - 1))
    min_distance = read_env_float("JUEGO_FOREST_IMPOSTOR_MIN_DISTANCE", 260.0, 96.0, 640.0)
    build_budget = read_env_int("JUEGO_FOREST_IMPOSTOR_BUILD_PER_FRAME", 2, 0, 8)
    build_budget = int(max(0, round(build_budget * float(rescue.get("forest_build_scale", 1.0)))))
    max_cache = read_env_int("JUEGO_FOREST_IMPOSTOR_CACHE_LIMIT", 96, 24, 256)
    softness = read_env_float("JUEGO_FOREST_IMPOSTOR_SOFTNESS", float(rescue.get("forest_softness", 0.12)), 0.0, 0.80)

    center_tx = int(math.floor(float(px) / tile_size))
    center_tz = int(math.floor(float(pz) / tile_size))
    candidates = []
    lock_key = (int(seed), int(center_tx), int(center_tz), int(round(tile_size)), int(samples))
    if _last_candidate_lock.get("key") == lock_key and _last_candidate_lock.get("candidates"):
        candidates = list(_last_candidate_lock["candidates"])
    else:
        for tx in range(center_tx - radius, center_tx + radius + 1):
            for tz in range(center_tz - radius, center_tz + radius + 1):
                dx = tx - center_tx
                dz = tz - center_tz
                ring = max(abs(dx), abs(dz))
                dist_world = math.hypot((tx + 0.5) * tile_size - float(px), (tz + 0.5) * tile_size - float(pz))
                if ring <= inner_radius or ring > radius or dist_world < min_distance:
                    continue
                candidates.append((dx * dx + dz * dz, tx, tz))
        candidates.sort()
        max_visible = max(4, int(round(len(candidates) * float(rescue.get("forest_max_visible_scale", 1.0)))))
        if len(candidates) > max_visible:
            candidates = candidates[:max_visible]
        _last_candidate_lock["key"] = lock_key
        _last_candidate_lock["candidates"] = tuple(candidates)

    built = 0
    visible = 0
    trees_drawn = 0
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    for _, tx, tz in candidates:
        ring = max(abs(tx - center_tx), abs(tz - center_tz))
        key = (int(seed), int(tx), int(tz), int(samples), round(float(tile_size), 3))
        tile = _forest_cache.get(key)
        if tile is None and built < build_budget:
            tile = _build_forest_tile(env_module, tx, tz, tile_size, samples, seed, softness, ring, inner_radius)
            _forest_cache[key] = tile
            _forest_order.append(key)
            built += 1
        if tile is not None:
            list_id, tree_count = tile
            if list_id:
                glCallList(list_id)
                visible += 1
                trees_drawn += int(tree_count)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    _trim_cache(max_cache)
    _stats.update({
        "enabled": 1,
        "tiles_visible": int(visible),
        "tiles_built": int(built),
        "trees_drawn": int(trees_drawn),
        "tiles_cached": len(_forest_cache),
        "rescue_level": int(rescue.get("level", 0) or 0),
        "softness": round(float(softness), 2),
    })


def _build_forest_tile(env_module, tx, tz, tile_size, samples, seed, softness, ring, inner_radius):
    x0 = float(tx) * float(tile_size)
    z0 = float(tz) * float(tile_size)
    step = float(tile_size) / float(samples)
    xs = x0 + (np.arange(samples, dtype=float) + 0.5) * step
    zs = z0 + (np.arange(samples, dtype=float) + 0.5) * step
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    terrain_props, _terrain_fields = env_module.calculate_runtime_terrain_properties_with_fields(gx, gz, seed)
    h_map, m_map, c_map, temp_map, rareza_map = terrain_props

    trees = []
    density = read_env_float("JUEGO_FOREST_IMPOSTOR_DENSITY", 0.72, 0.0, 2.0)
    for i in range(samples):
        for j in range(samples):
            x = float(gx[i, j])
            z = float(gz[i, j])
            h = float(h_map[i, j])
            moisture = float(m_map[i, j])
            temp = float(temp_map[i, j])
            rareza = float(rareza_map[i, j])
            cave = bool(c_map[i, j])
            _color, has_grass, _rock_chance, _rock_type, deco_type, _deco_chance, _rock_color = biomes.get_biome_color_and_features(
                h, moisture, cave, temp, rareza
            )
            strength = _forest_strength(h, moisture, temp, rareza, has_grass, deco_type)
            if strength <= 0.05:
                continue
            local_hash = _hash01(seed * 0.017 + x * 0.119 + z * 0.173)
            if local_hash > min(0.92, strength * density):
                continue
            ox = (_hash01(x * 0.41 + z * 0.13 + seed) - 0.5) * step * 0.62
            oz = (_hash01(x * 0.17 - z * 0.37 + seed) - 0.5) * step * 0.62
            width = (2.6 + _hash01(x * 0.23 + z * 0.29) * 2.2) * (0.85 + strength * 0.45)
            height = (4.2 + _hash01(x * 0.31 - z * 0.19) * 3.6) * (0.82 + strength * 0.35)
            distance_softness = max(0.0, float(ring) - float(inner_radius)) * float(softness)
            color = _soften_color(_forest_color(moisture, temp, strength, deco_type), distance_softness)
            alpha = (0.34 + strength * 0.22) * max(0.36, 1.0 - distance_softness * 0.24)
            trees.append((x + ox, h + 0.10, z + oz, width, height, color, alpha))

    if not trees:
        return None, 0

    list_id = glGenLists(1)
    glNewList(list_id, GL_COMPILE)
    glBegin(GL_QUADS)
    for x, y, z, width, height, color, alpha in trees:
        _add_tree_impostor_quads(x, y, z, width, height, color, alpha)
    glEnd()
    glEndList()
    return list_id, len(trees)


def _forest_strength(height, moisture, temp, rareza, has_grass, deco_type):
    if deco_type in ("arbol_bosque", "arbol_pantano", "arbol_roble", "arbol_pino", "arbol_abedul", "arbol_sauce", "arbol_cipres"):
        base = 0.58
    elif has_grass and moisture > 0.54:
        base = 0.34
    else:
        base = 0.0
    wet = _smoothstep(0.48, 0.82, moisture)
    altitude_ok = _smoothstep(4.0, 7.0, height) * (1.0 - _smoothstep(16.5, 20.5, height))
    not_hot_desert = 1.0 - (_smoothstep(0.72, 0.90, temp) * (1.0 - _smoothstep(0.36, 0.52, moisture)))
    dark_patch = _smoothstep(0.35, 0.68, -rareza) * _smoothstep(0.62, 0.82, moisture)
    return max(0.0, min(1.0, (base + wet * 0.26 + dark_patch * 0.28) * altitude_ok * not_hot_desert))


def _forest_color(moisture, temp, strength, deco_type):
    if deco_type in ("arbol_pantano", "arbol_sauce"):
        base = (0.045, 0.115, 0.055)
    elif deco_type == "arbol_cipres":
        base = (0.025, 0.095, 0.045)
    elif deco_type == "arbol_pino":
        base = (0.035, 0.125, 0.070)
    elif deco_type == "arbol_abedul":
        base = (0.055, 0.170, 0.070)
    else:
        base = (0.035, 0.155, 0.060)
    cold = max(0.0, min(1.0, 1.0 - temp))
    r = base[0] + moisture * 0.025 + cold * 0.010
    g = base[1] + moisture * 0.050 - strength * 0.025
    b = base[2] + cold * 0.035
    return max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b))


def _soften_color(color, softness):
    haze = (0.60, 0.74, 0.78)
    t = max(0.0, min(0.68, float(softness) * 0.42))
    return (
        color[0] * (1.0 - t) + haze[0] * t,
        color[1] * (1.0 - t) + haze[1] * t,
        color[2] * (1.0 - t) + haze[2] * t,
    )


def _add_tree_impostor_quads(x, y, z, width, height, color, alpha):
    dark = (color[0] * 0.65, color[1] * 0.68, color[2] * 0.72)
    trunk = (0.13, 0.08, 0.045)
    half = width * 0.5
    # Tronco sutil para que la masa no parezca una nube verde.
    trunk_w = width * 0.12
    trunk_h = height * 0.46
    glColor4f(trunk[0], trunk[1], trunk[2], alpha * 0.60)
    glVertex3f(x - trunk_w, y, z)
    glVertex3f(x + trunk_w, y, z)
    glVertex3f(x + trunk_w, y + trunk_h, z)
    glVertex3f(x - trunk_w, y + trunk_h, z)

    y0 = y + height * 0.28
    y1 = y + height
    glColor4f(color[0], color[1], color[2], alpha)
    glVertex3f(x - half, y0, z)
    glVertex3f(x + half, y0, z)
    glVertex3f(x + half * 0.72, y1, z)
    glVertex3f(x - half * 0.72, y1, z)

    zhalf = half * 0.82
    glColor4f(dark[0], dark[1], dark[2], alpha * 0.82)
    glVertex3f(x, y0, z - zhalf)
    glVertex3f(x, y0, z + zhalf)
    glVertex3f(x, y1, z + zhalf * 0.68)
    glVertex3f(x, y1, z - zhalf * 0.68)


def _smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (float(x) - float(edge0)) / max(0.0001, float(edge1) - float(edge0))))
    return t * t * (3.0 - 2.0 * t)


def _hash01(value):
    return math.sin(float(value) * 12.9898) * 43758.5453 % 1.0


def _trim_cache(max_cache):
    while len(_forest_order) > int(max_cache):
        old = _forest_order.pop(0)
        item = _forest_cache.pop(old, None)
        list_id = item[0] if item else None
        if list_id:
            try:
                glDeleteLists(list_id, 1)
            except Exception:
                pass
