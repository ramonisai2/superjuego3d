"""Relieve lejano real con apoyo barato de monticulos y cordilleras suaves.

Los parches lejanos usan la generacion real como base y una capa procedural
suave para que el horizonte tenga silueta sin calcular chunks completos.
"""

try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    pass
import math
import numpy as np
from . import biomes
from .env_config import read_env_bool, read_env_float, read_env_int


_far_tile_cache = {}
_far_tile_order = []
_last_candidate_lock = {"key": None, "candidates": None}
_stats = {
    "enabled": 0,
    "tiles_visible": 0,
    "tiles_built": 0,
    "tiles_cached": 0,
    "tile_size": 0,
    "subdivisions": 0,
    "max_visible": 0,
    "radius": 0,
    "height_scale": 0.0,
    "mound_amp": 0.0,
    "ridge_amp": 0.0,
    "terrain_blend": 0.0,
}


def far_terrain_stats():
    return dict(_stats)


def draw_far_terrain_lod(env_module, px, py, pz, seed, rescue=None):
    if not read_env_bool("JUEGO_FAR_TERRAIN_ENABLED", True):
        _stats.update({"enabled": 0, "tiles_visible": 0, "tiles_built": 0, "tiles_cached": len(_far_tile_cache)})
        return
    rescue = rescue or {}

    tile_size = read_env_float("JUEGO_FAR_TERRAIN_TILE_SIZE", 384.0, 160.0, 768.0)
    subdivisions = read_env_int("JUEGO_FAR_TERRAIN_SUBDIVISIONS", 5, 2, 12)
    base_radius = read_env_int("JUEGO_FAR_TERRAIN_RADIUS", 5, 3, 7)
    inner_base = read_env_int("JUEGO_FAR_TERRAIN_INNER_RADIUS", 2, 0, base_radius - 1)
    radius = max(inner_base + 1, int(round(base_radius * float(rescue.get("far_radius_scale", 1.0)))))
    inner_radius = max(0, min(inner_base, radius - 1))
    horizon_sink = read_env_float("JUEGO_FAR_TERRAIN_HORIZON_SINK", 0.62, 0.0, 5.0)
    height_scale = read_env_float("JUEGO_FAR_TERRAIN_HEIGHT_SCALE", 1.75, 0.50, 4.0)
    height_base = read_env_float("JUEGO_FAR_TERRAIN_HEIGHT_BASE", 7.5, -10.0, 40.0)
    vertical_lift = read_env_float("JUEGO_FAR_TERRAIN_VERTICAL_LIFT", 1.05, -10.0, 20.0)
    haze = read_env_float("JUEGO_FAR_TERRAIN_HAZE", 0.10, 0.0, 0.65)
    softness = read_env_float("JUEGO_FAR_TERRAIN_SOFTNESS", float(rescue.get("far_softness", 0.18)), 0.0, 0.75)
    build_budget = read_env_int("JUEGO_FAR_TERRAIN_BUILD_PER_FRAME", 1, 0, 4)
    build_budget = int(max(0, round(build_budget * float(rescue.get("far_build_scale", 1.0)))))
    max_cache = read_env_int("JUEGO_FAR_TERRAIN_CACHE_LIMIT", 80, 16, 160)
    max_visible = read_env_int("JUEGO_FAR_TERRAIN_MAX_VISIBLE", 64, 8, 96)
    max_visible = max(8, int(round(max_visible * float(rescue.get("far_max_visible_scale", 1.0)))))

    mound_amplitude = read_env_float("JUEGO_FAR_TERRAIN_MOUND_AMP", 6.0, 2.0, 18.0)
    mound_frequency = read_env_float("JUEGO_FAR_TERRAIN_MOUND_FREQ", 3.0, 1.0, 8.0)
    ridge_amplitude = read_env_float("JUEGO_FAR_TERRAIN_RIDGE_AMP", 10.0, 4.0, 25.0)
    ridge_frequency = read_env_float("JUEGO_FAR_TERRAIN_RIDGE_FREQ", 0.8, 0.3, 2.0)
    terrain_blend = read_env_float("JUEGO_FAR_TERRAIN_BLEND", 0.68, 0.0, 1.0)

    center_tx = int(math.floor(float(px) / tile_size))
    center_tz = int(math.floor(float(pz) / tile_size))
    candidates = []
    lock_key = (int(seed), int(center_tx), int(center_tz), int(round(tile_size)), int(subdivisions))
    if _last_candidate_lock.get("key") == lock_key and _last_candidate_lock.get("candidates"):
        candidates = list(_last_candidate_lock["candidates"])
    else:
        for tx in range(center_tx - radius, center_tx + radius + 1):
            for tz in range(center_tz - radius, center_tz + radius + 1):
                dx = tx - center_tx
                dz = tz - center_tz
                ring = max(abs(dx), abs(dz))
                if ring <= inner_radius or ring > radius:
                    continue
                dist2 = dx * dx + dz * dz
                candidates.append((dist2, tx, tz))
        candidates.sort()
        if len(candidates) > max_visible:
            candidates = candidates[:max_visible]
        _last_candidate_lock["key"] = lock_key
        _last_candidate_lock["candidates"] = tuple(candidates)

    built = 0
    visible = 0
    for _, tx, tz in candidates:
        ring = max(abs(tx - center_tx), abs(tz - center_tz))
        sink = _ring_horizon_sink(ring, inner_radius, horizon_sink)
        key = (
            int(seed), int(tx), int(tz), int(subdivisions),
            round(float(tile_size), 3), round(float(sink), 3),
            round(float(height_scale), 3), round(float(height_base), 3),
            round(float(vertical_lift), 3), round(float(haze), 3),
            round(float(mound_amplitude), 3),
            round(float(mound_frequency), 3),
            round(float(ridge_amplitude), 3),
            round(float(ridge_frequency), 3),
            round(float(terrain_blend), 3),
        )
        tile = _far_tile_cache.get(key)
        if tile is None and built < build_budget:
            tile = _build_far_tile(
                env_module, tx, tz, tile_size, subdivisions, seed, sink,
                height_scale, height_base, vertical_lift, haze, softness, ring, inner_radius,
                mound_amplitude, mound_frequency, ridge_amplitude, ridge_frequency, terrain_blend,
            )
            _far_tile_cache[key] = tile
            _far_tile_order.append(key)
            built += 1
        if tile is not None:
            glCallList(tile)
            visible += 1

    _trim_cache(max_cache)
    _stats.update({
        "enabled": 1,
        "tiles_visible": int(visible),
        "tiles_built": int(built),
        "tiles_cached": len(_far_tile_cache),
        "tile_size": int(round(tile_size)),
        "subdivisions": int(subdivisions),
        "max_visible": int(max_visible),
        "radius": int(radius),
        "height_scale": round(float(height_scale), 2),
        "rescue_level": int(rescue.get("level", 0) or 0),
        "softness": round(float(softness), 2),
        "mound_amp": round(mound_amplitude, 2),
        "ridge_amp": round(ridge_amplitude, 2),
        "terrain_blend": round(float(terrain_blend), 2),
    })


def _build_far_tile(
    env_module, tx, tz, tile_size, subdivisions, seed, horizon_sink,
    height_scale, height_base, vertical_lift, haze, softness, ring, inner_radius,
    mound_amp, mound_freq, ridge_amp, ridge_freq, terrain_blend,
):
    x0 = float(tx) * float(tile_size)
    z0 = float(tz) * float(tile_size)
    step = float(tile_size) / int(subdivisions)

    xs = x0 + np.arange(subdivisions + 1, dtype=float) * step
    zs = z0 + np.arange(subdivisions + 1, dtype=float) * step
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    terrain_props, _ = env_module.calculate_runtime_terrain_properties_with_fields(gx, gz, seed)
    h_map, m_map, c_map, temp_map, rareza_map = terrain_props

    mound_wave = (math.tau * float(mound_freq)) / max(float(tile_size), 1.0)
    ridge_wave = (math.tau * float(ridge_freq)) / max(float(tile_size), 1.0)
    mound_heights = (
        np.sin(gx * mound_wave * 0.9 + gz * mound_wave * 0.55)
        * np.cos(gz * mound_wave * 0.8 - gx * mound_wave * 0.35)
        + 0.45 * np.sin(gx * mound_wave * 1.55 + gz * mound_wave * 1.2 + 1.7)
    ) * (float(mound_amp) / 1.45)
    ridge_heights = (
        np.sin(gx * ridge_wave * 0.65 + gz * ridge_wave * 0.28)
        + 0.35 * np.sin(gx * ridge_wave * 1.05 - gz * ridge_wave * 0.82 + 1.8)
    ) * (float(ridge_amp) / 1.35)
    combined_heights = mound_heights + ridge_heights

    list_id = glGenLists(1)
    glNewList(list_id, GL_COMPILE)
    glBegin(GL_QUADS)
    for i in range(subdivisions):
        for j in range(subdivisions):
            raw_h00 = h_map[i, j]
            raw_h10 = h_map[i + 1, j]
            raw_h11 = h_map[i + 1, j + 1]
            raw_h01 = h_map[i, j + 1]

            h00_base = _far_height(raw_h00, height_base, height_scale, vertical_lift, horizon_sink)
            h10_base = _far_height(raw_h10, height_base, height_scale, vertical_lift, horizon_sink)
            h11_base = _far_height(raw_h11, height_base, height_scale, vertical_lift, horizon_sink)
            h01_base = _far_height(raw_h01, height_base, height_scale, vertical_lift, horizon_sink)

            hill00 = combined_heights[i, j]
            hill10 = combined_heights[i + 1, j]
            hill11 = combined_heights[i + 1, j + 1]
            hill01 = combined_heights[i, j + 1]

            h00 = h00_base * terrain_blend + hill00 * (1.0 - terrain_blend)
            h10 = h10_base * terrain_blend + hill10 * (1.0 - terrain_blend)
            h11 = h11_base * terrain_blend + hill11 * (1.0 - terrain_blend)
            h01 = h01_base * terrain_blend + hill01 * (1.0 - terrain_blend)

            avg_h = (h00 + h10 + h11 + h01) * 0.25
            avg_m = float((m_map[i, j] + m_map[i + 1, j] + m_map[i + 1, j + 1] + m_map[i, j + 1]) * 0.25)
            avg_temp = float((temp_map[i, j] + temp_map[i + 1, j] + temp_map[i + 1, j + 1] + temp_map[i, j + 1]) * 0.25)
            avg_rareza = float((rareza_map[i, j] + rareza_map[i + 1, j] + rareza_map[i + 1, j + 1] + rareza_map[i, j + 1]) * 0.25)
            es_cueva = bool(c_map[i, j])
            color, *_ = biomes.get_biome_color_and_features(avg_h, avg_m, es_cueva, avg_temp, avg_rareza)

            distance_softness = max(0.0, float(ring) - float(inner_radius)) * float(softness)
            shade = _slope_shade(h00, h10, h11, h01, distance_softness)
            height_tint = max(0.0, min(1.0, (avg_h - 7.0) / 14.0))
            final_haze = min(0.7, haze + 0.1 * distance_softness)
            col = _far_color(color, shade, height_tint, final_haze, distance_softness)
            glColor3f(col[0], col[1], col[2])

            glVertex3f(float(gx[i, j]), h00, float(gz[i, j]))
            glVertex3f(float(gx[i + 1, j]), h10, float(gz[i + 1, j]))
            glVertex3f(float(gx[i + 1, j + 1]), h11, float(gz[i + 1, j + 1]))
            glVertex3f(float(gx[i, j + 1]), h01, float(gz[i, j + 1]))
    glEnd()
    glEndList()
    return list_id


def _slope_shade(h00, h10, h11, h01, softness=0.0):
    dx = ((h10 + h11) - (h00 + h01)) * 0.5
    dz = ((h01 + h11) - (h00 + h10)) * 0.5
    contrast = max(0.35, 1.0 - float(softness) * 0.55)
    return max(0.76, min(1.10, 1.0 + ((-dx * 0.035 + dz * 0.025) * contrast)))


def _ring_horizon_sink(ring, inner_radius, horizon_sink):
    far_t = max(0.0, float(ring) - float(inner_radius))
    return float(horizon_sink) * (far_t ** 1.10)


def _far_height(raw_height, height_base, height_scale, vertical_lift, horizon_sink):
    raw = float(raw_height)
    return float(height_base) + (raw - float(height_base)) * float(height_scale) + float(vertical_lift) - float(horizon_sink)


def _far_color(color, shade, height_tint, haze, softness=0.0):
    horizon = (0.62, 0.76, 0.84)
    cold = (0.82, 0.84, 0.86)
    haze = max(0.0, min(0.82, float(haze)))
    contrast = max(0.40, 1.0 - float(softness) * 0.42)
    r = float(color[0]) * shade
    g = float(color[1]) * shade
    b = float(color[2]) * shade
    r = horizon[0] + (r - horizon[0]) * contrast
    g = horizon[1] + (g - horizon[1]) * contrast
    b = horizon[2] + (b - horizon[2]) * contrast
    r = r * (1.0 - height_tint * 0.20) + cold[0] * height_tint * 0.20
    g = g * (1.0 - height_tint * 0.20) + cold[1] * height_tint * 0.20
    b = b * (1.0 - height_tint * 0.20) + cold[2] * height_tint * 0.20
    return (
        max(0.0, min(1.0, r * (1.0 - haze) + horizon[0] * haze)),
        max(0.0, min(1.0, g * (1.0 - haze) + horizon[1] * haze)),
        max(0.0, min(1.0, b * (1.0 - haze) + horizon[2] * haze)),
    )


def _trim_cache(max_cache):
    while len(_far_tile_order) > int(max_cache):
        old = _far_tile_order.pop(0)
        list_id = _far_tile_cache.pop(old, None)
        if list_id:
            try:
                glDeleteLists(list_id, 1)
            except Exception:
                pass
