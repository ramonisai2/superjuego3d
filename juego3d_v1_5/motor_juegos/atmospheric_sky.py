"""Cielo atmosferico barato: ciclo dia/noche, nubes, sol, luna y estrellas."""

try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    # Permite compilar/auditar sin PyOpenGL instalado.
    pass
import math
import time
from dataclasses import dataclass

import numpy as np

from .env_config import read_env_bool, read_env_float, read_env_int


_START_TIME = time.perf_counter()
_sky_stats = {
    "clouds_enabled": 0,
    "clouds_drawn": 0,
    "biome_hint": "none",
    "biome_tint_strength": 0.0,
    "rescue_level": 0,
}
_sky_rescue = {
    "level": 0,
    "cloud_scale": 1.0,
}
_biome_sky_context = {
    "hint": "none",
    "tint": (0.70, 0.86, 1.00),
    "strength": 0.0,
}
_last_biome_sample = {
    "time": -9999.0,
    "px": 0.0,
    "pz": 0.0,
    "lx": 0.0,
    "lz": 0.0,
}


@dataclass(frozen=True)
class SkyProfile:
    hour: float
    daylight: float
    night: float
    dawn: float
    horizon: tuple
    zenith: tuple
    fog: tuple
    star_alpha: float
    sun_alpha: float
    moon_alpha: float


def current_sky_profile():
    if not read_env_bool("JUEGO_DAY_NIGHT_ENABLED", True):
        return _profile_from_day_fraction(0.29)

    day_seconds = read_env_float("JUEGO_DAY_LENGTH_SECONDS", 900.0, 120.0, 7200.0)
    start_hour = read_env_float("JUEGO_DAY_START_HOUR", 9.0, 0.0, 24.0)
    elapsed = max(0.0, time.perf_counter() - _START_TIME)
    day_fraction = ((start_hour / 24.0) + (elapsed / day_seconds)) % 1.0
    return _profile_from_day_fraction(day_fraction)


def sky_runtime_stats():
    return dict(_sky_stats)


def set_sky_rescue_level(level=0, cloud_scale=1.0):
    _sky_rescue["level"] = int(max(0, min(3, int(level or 0))))
    _sky_rescue["cloud_scale"] = float(max(0.10, min(1.0, cloud_scale)))
    _sky_stats["rescue_level"] = _sky_rescue["level"]


def update_distant_biome_sky(env_module, px, pz, lx, lz, seed):
    if not read_env_bool("JUEGO_BIOME_SKY_TINT_ENABLED", True):
        _set_biome_context("none", (0.70, 0.86, 1.00), 0.0)
        return
    try:
        now = time.perf_counter()
        interval = read_env_float("JUEGO_BIOME_SKY_SAMPLE_INTERVAL", 0.75, 0.10, 5.0)
        move_step = read_env_float("JUEGO_BIOME_SKY_MOVE_STEP", 24.0, 4.0, 128.0)
        look_step = read_env_float("JUEGO_BIOME_SKY_LOOK_STEP", 0.34, 0.05, 2.0)
        moved = math.hypot(float(px) - _last_biome_sample["px"], float(pz) - _last_biome_sample["pz"]) >= move_step
        looked = math.hypot(float(lx) - _last_biome_sample["lx"], float(lz) - _last_biome_sample["lz"]) >= look_step
        if now - _last_biome_sample["time"] < interval and not moved and not looked:
            return
        _last_biome_sample.update({
            "time": now,
            "px": float(px),
            "pz": float(pz),
            "lx": float(lx),
            "lz": float(lz),
        })
        length = max(0.001, math.sqrt(float(lx) * float(lx) + float(lz) * float(lz)))
        dist = read_env_float("JUEGO_BIOME_SKY_SAMPLE_DISTANCE", 260.0, 96.0, 640.0)
        sx = float(px) + (float(lx) / length) * dist
        sz = float(pz) + (float(lz) / length) * dist
        gx = np.array([[sx]], dtype=float)
        gz = np.array([[sz]], dtype=float)
        terrain_props, _fields = env_module.calculate_runtime_terrain_properties_with_fields(gx, gz, seed)
        h_map, m_map, _c_map, temp_map, rare_map = terrain_props
        hint, tint, strength = _biome_tint_from_fields(
            float(h_map[0, 0]),
            float(m_map[0, 0]),
            float(temp_map[0, 0]),
            float(rare_map[0, 0]),
        )
        strength *= read_env_float("JUEGO_BIOME_SKY_TINT_STRENGTH", 1.0, 0.0, 2.0)
        _set_biome_context(hint, tint, min(0.32, strength))
    except Exception:
        _set_biome_context("none", (0.70, 0.86, 1.00), 0.0)


def _set_biome_context(hint, tint, strength):
    _biome_sky_context["hint"] = str(hint)
    _biome_sky_context["tint"] = tuple(float(c) for c in tint)
    _biome_sky_context["strength"] = float(max(0.0, min(0.32, strength)))
    _sky_stats["biome_hint"] = _biome_sky_context["hint"]
    _sky_stats["biome_tint_strength"] = round(_biome_sky_context["strength"], 3)


def _biome_tint_from_fields(height, moisture, temp, rare):
    desert = _smoothstep(0.66, 0.82, temp) * (1.0 - _smoothstep(0.22, 0.36, moisture))
    swamp = _smoothstep(0.68, 0.84, moisture) * (1.0 - _smoothstep(9.0, 14.0, height)) * _smoothstep(0.24, 0.46, temp)
    cold_high = _smoothstep(13.0, 20.0, height) * (1.0 - _smoothstep(0.22, 0.42, temp))
    dark_forest = _smoothstep(0.68, 0.82, moisture) * (1.0 - _smoothstep(0.52, 0.68, temp)) * _smoothstep(0.12, 0.42, -rare)
    candidates = (
        ("desierto", (0.96, 0.78, 0.48), desert * 0.24),
        ("pantano", (0.42, 0.58, 0.46), swamp * 0.24),
        ("montana_fria", (0.66, 0.78, 0.94), cold_high * 0.16),
        ("bosque_oscuro", (0.34, 0.48, 0.36), dark_forest * 0.18),
    )
    return max(candidates, key=lambda item: item[2])


def draw_atmospheric_skybox(size=300.0):
    profile = current_sky_profile()
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    try:
        cull_was_enabled = bool(glIsEnabled(GL_CULL_FACE))
        glDisable(GL_CULL_FACE)
    except Exception:
        cull_was_enabled = False

    half = size * 0.5
    y_low = -20.0
    y_high = size * 0.45
    segments = read_env_int("JUEGO_SKYBOX_SEGMENTS", 24, 8, 64)

    glBegin(GL_QUADS)
    for i in range(segments):
        a0 = (i / float(segments)) * math.pi * 2.0
        a1 = ((i + 1) / float(segments)) * math.pi * 2.0
        x0, z0 = math.cos(a0) * half, math.sin(a0) * half
        x1, z1 = math.cos(a1) * half, math.sin(a1) * half
        glColor3f(*profile.horizon); glVertex3f(x0, y_low, z0); glVertex3f(x1, y_low, z1)
        glColor3f(*profile.zenith); glVertex3f(x1, y_high, z1); glVertex3f(x0, y_high, z0)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glColor3f(*profile.zenith)
    glVertex3f(0.0, y_high + 40.0, 0.0)
    for i in range(segments + 1):
        a = (i / float(segments)) * math.pi * 2.0
        glVertex3f(math.cos(a) * half, y_high, math.sin(a) * half)
    glEnd()

    _draw_cloud_layers(size, profile)
    _draw_stars(size, profile.star_alpha)
    _draw_sun_moon(size, profile)

    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    if cull_was_enabled:
        glEnable(GL_CULL_FACE)


def _profile_from_day_fraction(day_fraction):
    hour = float(day_fraction) * 24.0
    # 0 en medianoche, 1 en mediodia.
    sun_height = math.sin((day_fraction - 0.25) * math.pi * 2.0)
    daylight = _smoothstep(-0.10, 0.18, sun_height)
    night = 1.0 - _smoothstep(-0.24, 0.08, sun_height)
    dawn = max(0.0, 1.0 - abs(sun_height) / 0.34) * (1.0 - night * 0.35)

    day_horizon = (0.70, 0.86, 1.00)
    day_zenith = (0.20, 0.36, 0.70)
    night_horizon = (0.055, 0.075, 0.13)
    night_zenith = (0.010, 0.018, 0.050)
    dawn_horizon = (0.95, 0.52, 0.26)
    dawn_zenith = (0.22, 0.16, 0.34)

    horizon = _mix(night_horizon, day_horizon, daylight)
    zenith = _mix(night_zenith, day_zenith, daylight)
    horizon = _mix(horizon, dawn_horizon, dawn * 0.72)
    zenith = _mix(zenith, dawn_zenith, dawn * 0.45)

    fog = _mix((0.08, 0.10, 0.14), (0.75, 0.88, 1.00), daylight)
    fog = _mix(fog, (0.90, 0.58, 0.34), dawn * 0.55)
    tint_strength = float(_biome_sky_context.get("strength", 0.0)) * (0.45 + daylight * 0.55)
    if tint_strength > 0.001:
        tint = _biome_sky_context.get("tint", day_horizon)
        horizon = _mix(horizon, tint, tint_strength)
        fog = _mix(fog, tint, tint_strength * 0.70)

    return SkyProfile(
        hour=hour,
        daylight=daylight,
        night=night,
        dawn=dawn,
        horizon=horizon,
        zenith=zenith,
        fog=fog,
        star_alpha=max(0.0, min(1.0, night * 0.90)),
        sun_alpha=max(0.0, min(1.0, daylight)),
        moon_alpha=max(0.0, min(1.0, night * 0.85)),
    )


def _draw_sun_moon(size, profile):
    if profile.sun_alpha > 0.03:
        angle = ((profile.hour / 24.0) - 0.25) * math.pi * 2.0
        _draw_disc(
            math.cos(angle) * size * 0.42,
            math.sin(angle) * size * 0.34 + size * 0.12,
            math.sin(angle * 0.35) * size * 0.20,
            size * 0.040,
            (1.0, 0.86, 0.42, profile.sun_alpha),
            segments=18,
        )
    if profile.moon_alpha > 0.03:
        angle = ((profile.hour / 24.0) + 0.25) * math.pi * 2.0
        _draw_disc(
            math.cos(angle) * size * 0.42,
            math.sin(angle) * size * 0.34 + size * 0.12,
            math.sin(angle * 0.35 + 2.0) * size * 0.20,
            size * 0.030,
            (0.72, 0.80, 0.92, profile.moon_alpha),
            segments=16,
        )


def _draw_cloud_layers(size, profile):
    if not read_env_bool("JUEGO_CLOUDS_ENABLED", True):
        _sky_stats.update({"clouds_enabled": 0, "clouds_drawn": 0})
        return

    density = read_env_float("JUEGO_CLOUD_DENSITY", 0.95, 0.0, 1.75)
    base_count = read_env_int("JUEGO_CLOUD_COUNT", 24, 0, 48)
    cloud_scale = float(_sky_rescue.get("cloud_scale", 1.0) or 1.0)
    density *= cloud_scale
    count = max(0, min(64, int(round(base_count * density))))
    if count <= 0:
        _sky_stats.update({"clouds_enabled": 1, "clouds_drawn": 0})
        return

    elapsed = max(0.0, time.perf_counter() - _START_TIME)
    wind_speed = read_env_float("JUEGO_CLOUD_WIND_SPEED", 0.020, -0.20, 0.20)
    wind_angle = read_env_float("JUEGO_CLOUD_WIND_ANGLE", -0.35, -6.28, 6.28)
    wx = math.cos(wind_angle)
    wz = math.sin(wind_angle)
    sx = -wz
    sz = wx
    night_soften = 1.0 - profile.night * 0.55
    alpha_base = (0.17 + profile.daylight * 0.23 + profile.dawn * 0.08) * density * night_soften
    alpha_base = max(0.03, min(0.48, alpha_base))
    cloud_day = (0.92, 0.95, 0.96)
    cloud_dawn = (0.96, 0.70, 0.52)
    cloud_night = (0.18, 0.22, 0.32)
    color = _mix(cloud_night, cloud_day, profile.daylight)
    color = _mix(color, cloud_dawn, profile.dawn * 0.35)

    drawn = 0
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    for layer in range(2):
        layer_count = count // 2 if layer == 0 else count - (count // 2)
        y = size * (0.36 + layer * 0.13)
        span = size * (1.55 + layer * 0.18)
        cross_span = size * (1.00 + layer * 0.16)
        drift = elapsed * wind_speed * size * (0.30 + layer * 0.16)
        for i in range(layer_count):
            idx = i + layer * 53
            h = _hash01(idx * 41.7 + 3.1)
            h2 = _hash01(idx * 17.3 + 9.4)
            h3 = _hash01(idx * 67.9 + 1.7)
            along = ((h * span + drift) % span) - span * 0.5
            cross = (h2 - 0.5) * cross_span
            cx = wx * along + sx * cross
            cz = wz * along + sz * cross
            width = size * (0.070 + h3 * 0.060) * (1.15 if layer == 1 else 1.0)
            depth = size * (0.030 + h2 * 0.026)
            local_alpha = alpha_base * (0.72 + h * 0.38) * (0.78 if layer == 1 else 1.0)
            _cloud_sheet_cluster(cx, y, cz, width, depth, color, local_alpha, wx, wz, sx, sz)
            drawn += 1
    glEnd()
    glDisable(GL_BLEND)
    _sky_stats.update({"clouds_enabled": 1, "clouds_drawn": int(drawn)})


def _cloud_quad_cluster(cx, cy, cz, width, height, color, alpha):
    # Tres tarjetas horizontales dan lectura de nube sin malla ni textura.
    length = max(0.001, math.sqrt(cx * cx + cz * cz))
    rx = cz / length
    rz = -cx / length
    pieces = (
        (-0.38, 0.00, 0.74, 0.78, 0.56),
        (0.00, 0.02, 1.00, 1.00, 0.82),
        (0.42, -0.01, 0.68, 0.70, 0.48),
    )
    for ox, oy, sx, sy, a_mul in pieces:
        w = width * sx
        h = height * sy
        x = cx + rx * ox * width
        z = cz + rz * ox * width
        y = cy + oy * height
        glColor4f(color[0], color[1], color[2], alpha * a_mul)
        glVertex3f(x - rx * w, y - h, z - rz * w)
        glVertex3f(x + rx * w, y - h, z + rz * w)
        glVertex3f(x + rx * w, y + h, z + rz * w)
        glVertex3f(x - rx * w, y + h, z - rz * w)


def _cloud_sheet_cluster(cx, cy, cz, width, depth, color, alpha, wx, wz, sx, sz):
    # Láminas horizontales altas: entran desde el horizonte sin orbitar la cámara.
    pieces = (
        (-0.38, -0.08, 0.74, 0.70, 0.52),
        (0.00, 0.02, 1.00, 0.88, 0.82),
        (0.42, 0.10, 0.68, 0.62, 0.46),
    )
    for ox, oz, sw, sd, a_mul in pieces:
        x = cx + sx * ox * width + wx * oz * depth
        z = cz + sz * ox * width + wz * oz * depth
        y = cy + (a_mul - 0.60) * depth * 0.05
        w = width * sw
        d = depth * sd
        glColor4f(color[0], color[1], color[2], alpha * a_mul)
        glVertex3f(x - sx * w - wx * d, y, z - sz * w - wz * d)
        glVertex3f(x + sx * w - wx * d, y, z + sz * w - wz * d)
        glVertex3f(x + sx * w + wx * d, y, z + sz * w + wz * d)
        glVertex3f(x - sx * w + wx * d, y, z - sz * w + wz * d)


def _draw_disc(cx, cy, cz, radius, color, segments=16):
    length = max(0.001, math.sqrt(cx * cx + cy * cy + cz * cz))
    dx, dy, dz = cx / length, cy / length, cz / length
    rx, ry, rz = dz, 0.0, -dx
    rlen = max(0.001, math.sqrt(rx * rx + ry * ry + rz * rz))
    rx, ry, rz = rx / rlen, ry / rlen, rz / rlen
    ux = dy * rz - dz * ry
    uy = dz * rx - dx * rz
    uz = dx * ry - dy * rx

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_TRIANGLE_FAN)
    glColor4f(*color)
    glVertex3f(cx, cy, cz)
    for i in range(segments + 1):
        a = (i / float(segments)) * math.pi * 2.0
        ca = math.cos(a) * radius
        sa = math.sin(a) * radius
        glVertex3f(cx + rx * ca + ux * sa, cy + ry * ca + uy * sa, cz + rz * ca + uz * sa)
    glEnd()
    glDisable(GL_BLEND)


def _draw_stars(size, alpha):
    if alpha <= 0.02:
        return
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    for i in range(44):
        h = math.sin(i * 91.17) * 43758.5453
        rx = (h - math.floor(h)) * 2.0 - 1.0
        h2 = math.sin(i * 47.31 + 9.7) * 27113.13
        rz = (h2 - math.floor(h2)) * 2.0 - 1.0
        h3 = math.sin(i * 13.61 + 3.2) * 6113.91
        ry = 0.22 + (h3 - math.floor(h3)) * 0.38
        x = rx * size * 0.46
        y = size * ry
        z = rz * size * 0.46
        s = size * 0.0028
        glColor4f(0.84, 0.90, 1.0, alpha * (0.45 + (i % 3) * 0.18))
        glVertex3f(x - s, y, z)
        glVertex3f(x + s, y, z)
        glVertex3f(x + s, y + s, z)
        glVertex3f(x - s, y + s, z)
    glEnd()
    glDisable(GL_BLEND)


def _smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / max(0.0001, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(3))


def _hash01(value):
    return math.sin(float(value) * 12.9898) * 43758.5453 % 1.0
