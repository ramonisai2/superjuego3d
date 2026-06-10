import numpy as np


def _hash01(v):
    return np.mod(np.sin(v) * 43758.5453, 1.0)

def _smoothstep_np(edge0, edge1, x):
    t = np.clip((x - edge0) / max(0.0001, (edge1 - edge0)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


_BIOME_GRID = {
    (0, 0): ([0.88, 0.80, 0.60], False, 0.005, "pequeña", "arbol_seco", 0.006, [0.85, 0.75, 0.55]),
    (0, 1): ([0.82, 0.76, 0.68], False, 0.005, "normal", None, 0.0, None),
    (0, 2): ([0.22, 0.28, 0.18], True,  0.005, "normal", "arbol_pantano", 0.007, None),
    (1, 0): ([0.55, 0.52, 0.30], True,  0.01,  "normal", "arbol_seco", 0.006, None),
    (1, 1): ([0.22, 0.55, 0.22], True,  0.008, "normal", "arbol_bosque", 0.008, None),
    (1, 2): ([0.12, 0.42, 0.12], True,  0.01,  "normal", "arbol_bosque", 0.010, None),
    (2, 0): ([0.40, 0.40, 0.40], False, 0.04,  "gigante", "cristal", 0.005, [0.38, 0.38, 0.40]),
    (2, 1): ([0.30, 0.35, 0.38], True,  0.02,  "normal", "cristal", 0.003, None),
    (2, 2): ([0.95, 0.95, 0.98], False, 0.01,  "grande", None, 0.0, None),
}


def _macro_layer_field(x_array, z_array, seed):
    """
    FIX P: capas como bandas de altura controladas, no como mapas gigantes.

    La analogia de las tortillas:
    - baja/caliente: valles, lagos y pantanos puntuales.
    - media/templada: piso principal del mundo, debe dominar.
    - alta/fria: mesetas y montañas puntuales.

    Devuelve fuerzas suaves; la capa media es el estado normal.
    """
    s = seed * 0.01
    macro = (
        np.sin(x_array * 0.0021 + s * 0.7) * 0.40 +
        np.cos(z_array * 0.0019 - s * 0.8) * 0.34 +
        np.sin((x_array + z_array) * 0.0014 + s * 0.4) * 0.22
    )
    macro = (macro + 0.96) / 1.92
    macro = np.clip(macro, 0.0, 1.0)

    # Fuerzas limitadas: no convierten medio mundo en capa 1 o capa 3.
    low = (1.0 - _smoothstep_np(0.18, 0.32, macro)) * 0.42
    high = _smoothstep_np(0.72, 0.88, macro) * 0.46
    return low, high, macro


def _altitude_temperature_band(x_array, z_array, seed):
    """Banda climatica barata: caliente abajo, templada en medio, fria arriba."""
    s = seed * 0.01
    band = (
        np.sin(x_array * 0.00145 + s * 0.3) * 0.45 +
        np.cos(z_array * 0.00130 - s * 0.4) * 0.35
    )
    return np.clip((band + 0.80) / 1.60, 0.0, 1.0)

def _lake_basin_field(x_array, z_array, seed):
    """
    Generador de cuencas de lago mas visibles.
    Basado en celdas grandes con formas organicas y subcuencas suaves,
    para que el terreno forme depresiones reales y no solo charcas planas.
    """
    cell_size = 210.0
    base_cx = np.floor(x_array / cell_size)
    base_cz = np.floor(z_array / cell_size)
    best = np.zeros_like(x_array, dtype=float)

    for ox in (-1.0, 0.0, 1.0):
        for oz in (-1.0, 0.0, 1.0):
            cx = base_cx + ox
            cz = base_cz + oz
            h = cx * 127.1 + cz * 311.7 + seed * 0.013
            enabled = _hash01(h + 19.19) > 0.28
            rx = _hash01(h + 3.17)
            rz = _hash01(h + 8.73)
            rr = _hash01(h + 41.91)
            elong = _hash01(h + 77.7)
            angle = _hash01(h + 12.31) * np.pi * 2.0

            center_x = (cx + 0.16 + rx * 0.68) * cell_size
            center_z = (cz + 0.16 + rz * 0.68) * cell_size
            radius_x = 42.0 + rr * 58.0
            radius_z = radius_x * (0.60 + elong * 0.68)

            dx = x_array - center_x
            dz = z_array - center_z
            ca = np.cos(angle)
            sa = np.sin(angle)
            lx = dx * ca + dz * sa
            lz = -dx * sa + dz * ca

            wobble = (
                1.0
                + 0.10 * np.sin(x_array * 0.030 + seed * 0.011)
                + 0.08 * np.cos(z_array * 0.028 - seed * 0.009)
                + 0.05 * np.sin((x_array + z_array) * 0.018 + seed * 0.02)
            )
            d = np.sqrt((lx / (radius_x * wobble)) ** 2 + (lz / (radius_z * wobble)) ** 2)
            strength = np.clip(1.0 - d, 0.0, 1.0)
            strength = strength * strength * (3.0 - 2.0 * strength)

            # Subcuenca central ligera para dar sensacion de hoya mas marcada.
            inner = np.clip(1.0 - d * 1.55, 0.0, 1.0)
            inner = inner * inner * (3.0 - 2.0 * inner)
            profile = np.maximum(strength * 0.78, inner)

            best = np.maximum(best, np.where(enabled, profile, 0.0))

    return best



def _high_lake_basin_field(x_array, z_array, seed):
    """
    Lagos altos/lagunas de capa 3.
    Son mas pequenos y menos comunes que los lagos bajos, para que existan en
    zonas altas sin convertir la capa 4 en oceanos congelados.
    """
    cell_size = 190.0
    base_cx = np.floor(x_array / cell_size)
    base_cz = np.floor(z_array / cell_size)
    best = np.zeros_like(x_array, dtype=float)

    for ox in (-1.0, 0.0, 1.0):
        for oz in (-1.0, 0.0, 1.0):
            cx = base_cx + ox
            cz = base_cz + oz
            h = cx * 271.9 + cz * 157.3 + seed * 0.019
            enabled = _hash01(h + 88.8) > 0.44
            rx = _hash01(h + 4.21)
            rz = _hash01(h + 11.42)
            rr = _hash01(h + 63.13)
            elong = _hash01(h + 37.31)
            angle = _hash01(h + 22.91) * np.pi * 2.0

            center_x = (cx + 0.18 + rx * 0.64) * cell_size
            center_z = (cz + 0.18 + rz * 0.64) * cell_size
            radius_x = 34.0 + rr * 46.0
            radius_z = radius_x * (0.62 + elong * 0.54)

            dx = x_array - center_x
            dz = z_array - center_z
            ca = np.cos(angle)
            sa = np.sin(angle)
            lx = dx * ca + dz * sa
            lz = -dx * sa + dz * ca

            wobble = (
                1.0
                + 0.08 * np.sin(x_array * 0.034 + seed * 0.015)
                + 0.06 * np.cos(z_array * 0.031 - seed * 0.012)
            )
            d = np.sqrt((lx / (radius_x * wobble)) ** 2 + (lz / (radius_z * wobble)) ** 2)
            strength = np.clip(1.0 - d, 0.0, 1.0)
            strength = strength * strength * (3.0 - 2.0 * strength)
            inner = np.clip(1.0 - d * 1.42, 0.0, 1.0)
            inner = inner * inner * (3.0 - 2.0 * inner)
            profile = np.maximum(strength * 0.72, inner)
            best = np.maximum(best, np.where(enabled, profile, 0.0))

    return best


def _mesa_field(x_array, z_array, seed):
    """
    Mesetas procedurales altas: tapan parte del paisaje y tienen paredes fuertes,
    pero cada una incluye una rampa/camino natural menos abrupto.
    Devuelve (fuerza, altura_extra).
    """
    cell_size = 560.0
    base_cx = np.floor(x_array / cell_size)
    base_cz = np.floor(z_array / cell_size)
    best_strength = np.zeros_like(x_array, dtype=float)
    best_lift = np.zeros_like(x_array, dtype=float)

    for ox in (-1.0, 0.0, 1.0):
        for oz in (-1.0, 0.0, 1.0):
            cx = base_cx + ox
            cz = base_cz + oz
            h = cx * 193.3 + cz * 421.7 + seed * 0.017
            enabled = _hash01(h + 55.5) > 0.70
            rx = _hash01(h + 2.11)
            rz = _hash01(h + 9.91)
            rr = _hash01(h + 71.4)
            elong = _hash01(h + 33.8)
            angle = _hash01(h + 18.2) * np.pi * 2.0
            ramp_angle = angle + (_hash01(h + 29.1) - 0.5) * 1.8

            center_x = (cx + 0.16 + rx * 0.68) * cell_size
            center_z = (cz + 0.16 + rz * 0.68) * cell_size
            radius_x = 68.0 + rr * 72.0
            radius_z = radius_x * (0.58 + elong * 0.70)
            height = 5.5 + _hash01(h + 44.4) * 7.5

            dx = x_array - center_x
            dz = z_array - center_z
            ca = np.cos(angle)
            sa = np.sin(angle)
            lx = dx * ca + dz * sa
            lz = -dx * sa + dz * ca
            d = np.sqrt((lx / radius_x) ** 2 + (lz / radius_z) ** 2)

            # Perfil principal: cima bastante plana, borde más vertical.
            plateau = 1.0 - np.clip((d - 0.52) / 0.34, 0.0, 1.0)
            plateau = plateau * plateau * (3.0 - 2.0 * plateau)

            # Falda exterior pequeña para que no parezca bloque pegado.
            skirt = np.clip((1.13 - d) / 0.28, 0.0, 1.0)
            skirt = skirt * skirt * 0.22
            profile = np.maximum(plateau, skirt)

            # Rampa natural: una cuña radial que suaviza el ascenso.
            theta = np.arctan2(dz, dx)
            angle_diff = np.arctan2(np.sin(theta - ramp_angle), np.cos(theta - ramp_angle))
            ramp_width = 0.09 + _hash01(h + 90.0) * 0.05
            ramp_mask = (np.abs(angle_diff) < ramp_width) & (d < 1.16)
            ramp_profile = np.clip((1.12 - d) / 0.82, 0.0, 1.0)
            ramp_profile = ramp_profile * ramp_profile * (3.0 - 2.0 * ramp_profile)
            profile = np.where(ramp_mask, np.maximum(profile * 0.12, ramp_profile * 0.72), profile)

            profile = np.where(enabled, profile, 0.0)
            lift = profile * height
            best_strength = np.maximum(best_strength, profile)
            best_lift = np.maximum(best_lift, lift)

    return best_strength, best_lift
def calculate_terrain_properties_with_fields(x_array, z_array, seed):
    s = seed * 0.01

    # FIX D experimental: relieve de 4 capas.
    # 1 baja/caliente, 2 media/templada, 3 alta/fresca, 4 cumbre/fria.
    lake_basin = _lake_basin_field(x_array, z_array, seed)
    high_lake_basin = _high_lake_basin_field(x_array, z_array, seed)
    layer_low_macro, layer_high_macro, macro = _macro_layer_field(x_array, z_array, seed)
    temp_band = _altitude_temperature_band(x_array, z_array, seed)
    mesa_strength, mesa_lift = _mesa_field(x_array, z_array, seed)

    # Detalle local y ondulacion media: ahora hay mas accidente sin subir todo el mapa.
    roll_a = np.sin(x_array * 0.018 - s) * np.cos(z_array * 0.016 + s) * 0.72
    roll_b = np.sin(x_array * 0.042 + z_array * 0.017 + s * 0.3) * 0.36
    roll_c = np.sin(x_array * 0.070 - z_array * 0.051 + s * 0.9) * 0.16
    detalle = roll_a + roll_b + roll_c

    # Campo de crestas/cumbres: es raro y estrecho, para meter una cuarta altura.
    ridge = (
        np.sin(x_array * 0.0066 + s * 0.55) * 0.50 +
        np.cos(z_array * 0.0061 - s * 0.50) * 0.42 +
        np.sin((x_array - z_array) * 0.0048 + s * 0.33) * 0.28
    )
    ridge = (ridge + 1.20) / 2.40
    ridge = np.clip(ridge, 0.0, 1.0)

    layer1 = 4.4 + detalle * 0.25     # valles, lagos, pantanos, zona caliente
    layer2 = 8.2 + detalle * 0.95     # mundo principal
    layer3 = 12.4 + detalle * 0.82 + layer_high_macro * 1.8  # colinas altas/mesetas
    layer4 = 16.2 + detalle * 0.62 + ridge * 4.2             # cumbres frias, escasas

    lake_floor_strength = _smoothstep_np(0.36, 0.82, lake_basin)
    low_strength = np.maximum(layer_low_macro * 0.26, lake_floor_strength * 0.74)

    mesa_top = np.clip((mesa_strength - 0.52) / 0.38, 0.0, 1.0)
    mesa_top = mesa_top * mesa_top * (3.0 - 2.0 * mesa_top)
    high_strength = np.maximum(layer_high_macro * 0.55, mesa_top * 0.76)
    high_strength = np.maximum(high_strength, _smoothstep_np(0.44, 0.74, ridge) * 0.34)

    # Capa 4: solo cuando coinciden cresta + altura macro/meseta. Debe verse especial, no común.
    peak_strength = _smoothstep_np(0.50, 0.78, ridge) * (0.18 + high_strength * 1.05 + mesa_top * 0.70)
    peak_strength = np.clip(peak_strength, 0.0, 0.78)
    peak_strength = peak_strength * (1.0 - lake_floor_strength * 0.95)

    elevation_final = layer2 * (1.0 - low_strength) + layer1 * low_strength
    elevation_final = elevation_final * (1.0 - high_strength) + layer3 * high_strength
    elevation_final = elevation_final * (1.0 - peak_strength) + layer4 * peak_strength

    # Mesetas especificas: suaviza cima y levanta un poco; con 4 capas se reduce el lift para no crear paredes imposibles.
    mesa_base = _neighbor_mean(elevation_final, radius=4)
    elevation_final = elevation_final * (1.0 - mesa_top * 0.38) + mesa_base * (mesa_top * 0.38) + mesa_lift * 0.48

    # Riachuelos de meseta: si una meseta es humeda/verde, sus bordes tallan
    # pequenas rutas de escorrentia como pasaria en laderas naturales.
    mesa_edge = _smoothstep_np(0.16, 0.42, mesa_strength) * (1.0 - _smoothstep_np(0.70, 0.92, mesa_strength))
    mesa_runoff_wave = (
        np.sin(x_array * 0.027 + z_array * 0.011 + s * 3.7)
        + 0.42 * np.sin(x_array * 0.053 - z_array * 0.041 + s * 1.9)
    )
    mesa_runoff_line = np.clip((0.092 - np.abs(mesa_runoff_wave)) / 0.092, 0.0, 1.0)
    mesa_green_gate = _smoothstep_np(0.38, 0.62, temp_band) * _smoothstep_np(0.28, 0.58, macro)
    mesa_runoff_carve = mesa_edge * mesa_runoff_line * mesa_green_gate * (1.0 - lake_floor_strength) * 0.58
    elevation_final = np.clip(elevation_final - mesa_runoff_carve, 0.20, 95.0)

    # Tallado de lago claro, respetando la capa baja.
    basin_curve = np.clip(lake_basin, 0.0, 1.0)
    basin_curve = basin_curve * basin_curve * (3.0 - 2.0 * basin_curve)
    inner_curve = np.clip((lake_basin - 0.42) / 0.58, 0.0, 1.0)
    inner_curve = inner_curve * inner_curve * (3.0 - 2.0 * inner_curve)
    basin_carve = basin_curve * 0.34 + inner_curve * 1.18
    elevation_final = np.clip(elevation_final - basin_carve, 0.20, 95.0)

    # PRE-E: lagunas de capa 3. Se tallan solo en alturas medias-altas,
    # nunca en cumbres extremas. Esto permite agua en capa 3 sin llenar capa 4.
    high_lake_gate = np.clip((elevation_final - 10.2) / 2.4, 0.0, 1.0) * (1.0 - np.clip((elevation_final - 15.2) / 1.8, 0.0, 1.0))
    high_lake_curve = np.clip((high_lake_basin - 0.22) / 0.78, 0.0, 1.0)
    high_lake_curve = high_lake_curve * high_lake_curve * (3.0 - 2.0 * high_lake_curve)
    high_lake_carve = high_lake_curve * high_lake_gate * 1.65
    elevation_final = np.clip(elevation_final - high_lake_carve, 0.20, 95.0)

    # Cuevas preliminares: mas probables bajo capa 3/4, sin romper lagos.
    capa_cueva_x = np.sin(x_array * 0.15 + s)
    capa_cueva_z = np.cos(z_array * 0.15 - s)
    mascara_cueva = (capa_cueva_x > 0.86) & (capa_cueva_z > 0.86)
    es_zona_montana = (elevation_final > 11.0) & (elevation_final < 30.0) & (lake_basin < 0.12)
    condicion_cueva = mascara_cueva & es_zona_montana
    elevation_final = np.where(condicion_cueva, elevation_final - 4.0, elevation_final)
    elevation_final = np.clip(elevation_final, 0.20, 95.0)

    capa_clima_base = np.cos((x_array + 300) * 0.005 + s) * np.sin((z_array + 300) * 0.005 + s)
    capa_clima_det = np.sin(x_array * 0.02 - s) * np.cos(z_array * 0.02 + s) * 0.2
    moisture = np.clip((capa_clima_base + capa_clima_det + 1.2) / 2.4, 0.0, 1.0)
    moisture = np.clip(moisture + lake_floor_strength * 0.16 - high_strength * 0.06 - peak_strength * 0.08, 0.0, 1.0)

    rareza = np.sin(x_array * 0.03 + s) * np.cos(z_array * 0.03 - s)

    # Temperatura por 4 capas: valles calientes, media templada, altas frias, cumbres muy frias.
    temperatura = 0.86 - (elevation_final / 38.0) + (1.0 - temp_band) * 0.18 + (rareza * 0.16) - peak_strength * 0.18
    temperatura = np.clip(temperatura, 0.0, 1.0)

    props = (elevation_final, moisture, condicion_cueva, temperatura, rareza)
    fields = {
        "lake_basin": lake_basin,
        "high_lake_basin": high_lake_basin,
        "mesa_strength": mesa_strength,
    }
    return props, fields


def calculate_terrain_properties(x_array, z_array, seed):
    props, _ = calculate_terrain_properties_with_fields(x_array, z_array, seed)
    return props


def _lerp_color(c1, c2, t):
    return [c1[i] + (c2[i] - c1[i]) * t for i in range(3)]


def _lerp_property(p1, p2, t):
    return p1 + (p2 - p1) * t


def _smoothstep(edge0, edge1, x):
    if edge1 == edge0:
        return 0.0
    t = (float(x) - edge0) / (edge1 - edge0)
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return t * t * (3.0 - 2.0 * t)



def _neighbor_mean(arr, radius=1):
    """Promedio local sin wrap-around; ayuda a detectar cuencas reales."""
    if arr.ndim != 2:
        return arr.astype(float)
    pad = np.pad(arr.astype(float), radius, mode="edge")
    total = np.zeros_like(arr, dtype=float)
    count = 0
    h, w = arr.shape
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            if dx == 0 and dz == 0:
                continue
            total += pad[radius + dx:radius + dx + h, radius + dz:radius + dz + w]
            count += 1
    return total / max(1, count)


def _neighbor_bool_max(mask, radius=1):
    if mask.ndim != 2:
        return mask
    pad = np.pad(mask.astype(bool), radius, mode="edge")
    out = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            out |= pad[radius + dx:radius + dx + h, radius + dz:radius + dz + w]
    return out


def calculate_water_properties(x_array, z_array, elevation, moisture, temperatura, rareza, seed, terrain_fields=None):
    """
    PRE-E: agua por capas.
    - Lagos bajos: capa 1 y depresiones.
    - Lagunas altas: capa 3, mas pequenas y frias.
    - Capa 4 queda casi seca/sagrada/fria, sin lagos comunes.
    """
    s = seed * 0.01
    terrain_fields = terrain_fields or {}
    lake_basin = terrain_fields.get("lake_basin")
    if lake_basin is None:
        lake_basin = _lake_basin_field(x_array, z_array, seed)
    high_lake_basin = terrain_fields.get("high_lake_basin")
    if high_lake_basin is None:
        high_lake_basin = _high_lake_basin_field(x_array, z_array, seed)
    mesa_strength = terrain_fields.get("mesa_strength")
    if mesa_strength is None:
        mesa_strength, _ = _mesa_field(x_array, z_array, seed)

    # Lagos bajos: nivel local bajo, un poco mas permisivo que antes.
    terrace_low = np.floor((np.sin(x_array * 0.0015 + s) + np.cos(z_array * 0.0013 - s)) * 0.85) * 0.25
    low_water_level = 5.25 + terrace_low
    low_depth = np.clip(low_water_level - elevation, 0.0, 8.0)

    # Lagunas altas de capa 3: nivel frio/local. No usar en capa 4.
    terrace_high = np.floor((np.sin(x_array * 0.0022 + s * 1.7) + np.cos(z_array * 0.0020 - s * 1.3)) * 0.80) * 0.22
    high_water_level = 13.25 + terrace_high
    high_depth = np.clip(high_water_level - elevation, 0.0, 5.0)
    high_layer_gate = (elevation > 9.4) & (elevation < 15.15) & (temperatura > 0.12)

    pond_core_low = (lake_basin > 0.54) & (low_depth > 0.36) & (elevation < 5.72)

    # Riachuelos/entradas bajas, raros pero un poco mas visibles.
    arm_wave = np.sin(x_array * 0.014 + z_array * 0.008 + s * 2.2)
    trickle_low = (
        (lake_basin > 0.34) & (lake_basin <= 0.58) &
        (np.abs(arm_wave) < 0.006) &
        (low_depth > 0.12) & (low_depth < 0.78) & (elevation < 5.92)
    )

    # Lagos altos: mas chicos; necesitan cuenca fuerte y estar en capa 3.
    pond_core_high = high_layer_gate & (high_lake_basin > 0.46) & (high_depth > 0.12)
    high_trickle_wave = np.sin(x_array * 0.019 - z_array * 0.012 + s * 3.1)
    trickle_high = high_layer_gate & (high_lake_basin > 0.34) & (high_lake_basin <= 0.58) & (np.abs(high_trickle_wave) < 0.0065) & (high_depth > 0.10) & (high_depth < 0.55)

    # Escorrentia desde mesetas verdes: aparece en bordes de meseta con humedad
    # suficiente y corre siguiendo bandas estrechas, no como lagos planos.
    mesa_edge = _smoothstep_np(0.16, 0.42, mesa_strength) * (1.0 - _smoothstep_np(0.70, 0.92, mesa_strength))
    mesa_runoff_wave = (
        np.sin(x_array * 0.027 + z_array * 0.011 + s * 3.7)
        + 0.42 * np.sin(x_array * 0.053 - z_array * 0.041 + s * 1.9)
    )
    mesa_runoff_line = np.abs(mesa_runoff_wave) < (0.034 + moisture * 0.018)
    mesa_green = (moisture > 0.38) & (temperatura > 0.16) & (temperatura < 0.80)
    mesa_runoff_gate = high_layer_gate | ((elevation > 8.6) & (elevation < 16.2) & (mesa_edge > 0.24))
    mesa_runoff = (
        mesa_runoff_gate
        & mesa_green
        & (mesa_edge > 0.10)
        & mesa_runoff_line
        & (high_lake_basin > 0.02)
    )

    water_mask_low = pond_core_low | trickle_low
    water_mask_high = pond_core_high | trickle_high | mesa_runoff
    water_mask = water_mask_low | water_mask_high

    # Nivel por punto: si es lago alto, usa su terraza alta; si no, baja.
    water_level = np.where(water_mask_high, high_water_level, low_water_level)
    depth = np.where(water_mask_high, high_depth, low_depth)
    water_level = np.where(mesa_runoff, elevation + 0.22, water_level)
    depth = np.where(mesa_runoff, 0.28, depth)

    # Orillas: anillo bajo + anillo alto. No invaden capa 4.
    shore_low = (~water_mask) & (lake_basin > 0.22) & (lake_basin < 0.66) & (elevation >= low_water_level - 0.62) & (elevation < low_water_level + 1.70)
    shore_high = (~water_mask) & high_layer_gate & (high_lake_basin > 0.24) & (high_lake_basin < 0.78) & (elevation >= high_water_level - 0.50) & (elevation < high_water_level + 1.25)
    shore_runoff = (~water_mask) & mesa_runoff_gate & (mesa_edge > 0.06) & (moisture > 0.32) & (np.abs(mesa_runoff_wave) < 0.120)
    shore_mask = shore_low | shore_high | shore_runoff

    return water_mask, shore_mask, water_level, depth


def get_water_color(depth, moisture, temperatura):
    """Color simple para lagos: mas turbio en pantano, mas frio en altura."""
    t = float(max(0.0, min(1.0, depth / 2.4)))
    if moisture > 0.72 and temperatura > 0.35:
        base = [0.13, 0.36, 0.32]   # agua pantanosa verdosa
    elif temperatura < 0.28:
        base = [0.28, 0.50, 0.66]   # lago frio de altura
    else:
        base = [0.16, 0.41, 0.58]   # lago normal
    return [max(0.0, min(1.0, c + t * 0.07)) for c in base]

def get_biome_color_and_features(avg_h, avg_m, es_interior_cueva, temperatura, rareza):
    if es_interior_cueva:
        return [0.25, 0.25, 0.27], False, 0.02, "normal", "cristal", 0.06, [0.30, 0.30, 0.32]

    # Determinar índices de altura
    if avg_h < 3.5:
        h_idx = 0
        h_t = avg_h / 3.5
    elif avg_h < 13.0:
        h_idx = 1
        h_t = (avg_h - 3.5) / (13.0 - 3.5)
    else:
        h_idx = 2
        h_t = min(1.0, (avg_h - 13.0) / 10.0)

    # Índices de humedad
    if avg_m < 0.35:
        m_idx = 0
        m_t = avg_m / 0.35
    elif avg_m < 0.65:
        m_idx = 1
        m_t = (avg_m - 0.35) / 0.3
    else:
        m_idx = 2
        m_t = min(1.0, (avg_m - 0.65) / 0.35)

    def get(i, j):
        i = max(0, min(2, i))
        j = max(0, min(2, j))
        return _BIOME_GRID[(i, j)]

    p00 = get(h_idx, m_idx)
    p10 = get(h_idx + 1, m_idx)
    p01 = get(h_idx, m_idx + 1)
    p11 = get(h_idx + 1, m_idx + 1)

    # Interpolación en altura
    c_m0 = _lerp_color(p00[0], p10[0], h_t)
    grass_m0 = _lerp_property(float(p00[1]), float(p10[1]), h_t) > 0.5
    rock_chance_m0 = _lerp_property(p00[2], p10[2], h_t)
    rock_type_m0 = p00[3] if h_t < 0.5 else p10[3]
    deco_type_m0 = p00[4] if h_t < 0.5 else p10[4]
    deco_chance_m0 = _lerp_property(p00[5], p10[5], h_t)
    rc_m0 = (_lerp_color(p00[6] or [0.5, 0.5, 0.5], p10[6] or [0.5, 0.5, 0.5], h_t)
             if p00[6] is not None and p10[6] is not None else None)

    c_m1 = _lerp_color(p01[0], p11[0], h_t)
    grass_m1 = _lerp_property(float(p01[1]), float(p11[1]), h_t) > 0.5
    rock_chance_m1 = _lerp_property(p01[2], p11[2], h_t)
    rock_type_m1 = p01[3] if h_t < 0.5 else p11[3]
    deco_type_m1 = p01[4] if h_t < 0.5 else p11[4]
    deco_chance_m1 = _lerp_property(p01[5], p11[5], h_t)
    rc_m1 = (_lerp_color(p01[6] or [0.5, 0.5, 0.5], p11[6] or [0.5, 0.5, 0.5], h_t)
             if p01[6] is not None and p11[6] is not None else None)

    # Interpolación en humedad
    color = _lerp_color(c_m0, c_m1, m_t)
    has_grass = _lerp_property(float(grass_m0), float(grass_m1), m_t) > 0.5
    rock_chance = _lerp_property(rock_chance_m0, rock_chance_m1, m_t)
    rock_type = rock_type_m0 if m_t < 0.5 else rock_type_m1
    deco_type = deco_type_m0 if m_t < 0.5 else deco_type_m1
    deco_chance = _lerp_property(deco_chance_m0, deco_chance_m1, m_t)
    rock_color = (_lerp_color(rc_m0, rc_m1, m_t) if rc_m0 is not None and rc_m1 is not None else None)

    # Sobrecapas suaves para biomas singulares, evitando parches duros.
    # 1) Volcánico muy raro.
    volc = _smoothstep(0.90, 0.98, temperatura) * _smoothstep(0.72, 0.95, rareza) * (1.0 - _smoothstep(18.0, 24.0, avg_h))
    if volc > 0.01:
        color = _lerp_color(color, [0.50, 0.20, 0.10], volc)
        rock_chance = _lerp_property(rock_chance, 0.02, volc)
        rock_type = rock_type if volc < 0.55 else "gigante"
        deco_type = deco_type if volc < 0.55 else "cristal"
        deco_chance = _lerp_property(deco_chance, 0.002, volc)
        rock_color = _lerp_color(rock_color or [0.45, 0.40, 0.35], [0.60, 0.22, 0.10], volc)
        has_grass = has_grass and volc < 0.35

    # 2) Glaciar suave en altura fría.
    glac = _smoothstep(0.00, 0.25, 0.25 - temperatura) * _smoothstep(12.0, 18.0, avg_h)
    if glac > 0.01:
        color = _lerp_color(color, [0.90, 0.95, 1.00], glac)
        rock_chance = _lerp_property(rock_chance, 0.02, glac)
        rock_color = _lerp_color(rock_color or [0.60, 0.65, 0.72], [0.70, 0.80, 1.00], glac)
        if glac > 0.55:
            rock_type = "normal"
            deco_type = "cristal"
            deco_chance = max(deco_chance, 0.005)
            has_grass = False

    # 3) Zonas calientes/desérticas pequeñas, con borde suave.
    # Secas y calientes. Más raras que antes.
    hot_patch = _smoothstep(0.74, 0.87, temperatura) * (1.0 - _smoothstep(0.16, 0.28, avg_m)) * _smoothstep(0.25, 0.60, -rareza)
    if hot_patch > 0.01:
        color = _lerp_color(color, [0.86, 0.72, 0.42], hot_patch * 0.85)
        rock_color = _lerp_color(rock_color or [0.55, 0.50, 0.42], [0.92, 0.74, 0.44], hot_patch)
        rock_chance = _lerp_property(rock_chance, 0.004, hot_patch)
        if hot_patch > 0.42:
            deco_type = "cactus"
            deco_chance = max(deco_chance, 0.004)
            has_grass = False
            if rock_type == "gigante":
                rock_type = "grande"

    # 4) Terracota cálida: sólo pequeñas manchas templadas/semiáridas,
    # mucho más suaves y menos frecuentes que antes.
    terracota = (
        _smoothstep(0.69, 0.77, temperatura) *
        _smoothstep(0.24, 0.30, avg_m) *
        (1.0 - _smoothstep(0.34, 0.40, avg_m)) *
        _smoothstep(0.88, 0.97, rareza)
    )
    if terracota > 0.01:
        # Mezcla más sutil para que se vea como transición caliente, no como parche duro.
        color = _lerp_color(color, [0.80, 0.46, 0.26], terracota * 0.42)
        rock_color = _lerp_color(rock_color or [0.58, 0.46, 0.36], [0.78, 0.44, 0.24], terracota * 0.55)
        rock_chance = _lerp_property(rock_chance, 0.003, terracota * 0.55)
        if terracota > 0.62:
            deco_type = "cactus"
            deco_chance = max(deco_chance, 0.002)
            has_grass = False

    # 5) Bosque oscuro raro, también suave.
    bosque_osc = _smoothstep(0.72, 0.84, avg_m) * _smoothstep(5.0, 10.0, avg_h) * (1.0 - _smoothstep(14.0, 18.0, avg_h)) * _smoothstep(0.38, 0.60, -rareza) * (1.0 - _smoothstep(0.55, 0.68, temperatura))
    if bosque_osc > 0.01:
        color = _lerp_color(color, [0.10, 0.20, 0.10], bosque_osc * 0.70)
        rock_chance = _lerp_property(rock_chance, 0.01, bosque_osc)
        if bosque_osc > 0.45:
            deco_type = "arbol_pantano"
            deco_chance = max(deco_chance, 0.0045)
            rock_color = _lerp_color(rock_color or [0.26, 0.28, 0.24], [0.20, 0.20, 0.20], bosque_osc)

    return color, has_grass, rock_chance, rock_type, deco_type, deco_chance, rock_color
