try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    # Permite usar benchmarks de generacion de terreno sin cargar OpenGL.
    pass
import numpy as np
import math
import os
from . import biomes
from .terrain_noise_experiment import calculate_fast_noise_terrain_properties, calculate_fast_noise_water_properties
from .mesh_data import ChunkMeshData
from .materials import get_material

_height_cache = {}

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


def _read_density_override(name, default, min_value=0.0, max_value=1.25):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return float(default)
    try:
        value = float(raw)
    except ValueError:
        return float(default)
    return max(float(min_value), min(float(max_value), value))


def _read_int_override(name, default, min_value=1, max_value=3):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return int(default)
    try:
        value = int(raw)
    except ValueError:
        return int(default)
    return max(int(min_value), min(int(max_value), value))


def _read_float_override(name, default, min_value=-1.0, max_value=1.0):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return float(default)
    try:
        value = float(raw)
    except ValueError:
        return float(default)
    return max(float(min_value), min(float(max_value), value))


def _water_surface_y(raw_level, ground_y):
    """
    Mantiene la lamina de agua pegada al terreno visual.

    Antes el fondo visual del lago podia bajarse mas que el nivel procedural del
    agua, dejando placas flotando. La superficie ahora no puede quedar mas que
    un margen minimo por encima del suelo local.
    """
    try:
        raw = float(raw_level)
        ground = float(ground_y)
    except (TypeError, ValueError):
        return float(raw_level)
    if not np.isfinite(raw) or not np.isfinite(ground):
        return raw
    max_above = _read_float_override(
        "JUEGO_WATER_SURFACE_MAX_ABOVE_GROUND",
        WATER_SURFACE_MAX_ABOVE_GROUND,
        -0.04,
        0.10,
    )
    return min(raw + 0.004, ground + max_above)


def _world_detail_density():
    preset = os.environ.get("JUEGO_WORLD_DETAIL_PRESET", "").strip().lower()
    if not preset:
        preset = os.environ.get("JUEGO_GRAPHICS_PRESET", "balanced").strip().lower() or "balanced"
    profile = dict(WORLD_DETAIL_PROFILES.get(preset, WORLD_DETAIL_PROFILES["balanced"]))
    profile["grass"] = _read_density_override("JUEGO_GRASS_DENSITY", profile["grass"])
    profile["deco"] = _read_density_override("JUEGO_DECO_DENSITY", profile["deco"])
    profile["rock"] = _read_density_override("JUEGO_ROCK_DENSITY", profile["rock"])
    profile["oasis_tree"] = _read_density_override("JUEGO_OASIS_TREE_DENSITY", profile["oasis_tree"])
    profile["grass_planes"] = _read_int_override("JUEGO_GRASS_PLANES", profile["grass_planes"], 1, 2)
    profile["deco_planes"] = _read_int_override("JUEGO_DECO_PLANES", profile["deco_planes"], 1, 2)
    profile["leaf_planes"] = _read_int_override("JUEGO_LEAF_PLANES", profile["leaf_planes"], 1, 3)
    profile["tree_layers"] = _read_int_override("JUEGO_TREE_LAYERS", profile["tree_layers"], 1, 2)
    profile["rock_detail"] = _read_int_override("JUEGO_ROCK_DETAIL", profile["rock_detail"], 1, 2)
    profile["preset"] = preset if preset in WORLD_DETAIL_PROFILES else "balanced"
    return profile


def get_world_detail_density_status():
    return dict(_world_detail_density())


def _terrain_mode():
    return os.environ.get("JUEGO_TERRAIN_MODE", "current").strip().lower() or "current"


def calculate_runtime_terrain_properties(x_array, z_array, seed):
    if _terrain_mode() in {"fast_noise", "fast_noise_lite", "perlin", "noise"}:
        return calculate_fast_noise_terrain_properties(x_array, z_array, seed)
    return biomes.calculate_terrain_properties(x_array, z_array, seed)


def calculate_runtime_terrain_properties_with_fields(x_array, z_array, seed):
    if _terrain_mode() in {"fast_noise", "fast_noise_lite", "perlin", "noise"}:
        return calculate_fast_noise_terrain_properties(x_array, z_array, seed), {}
    return biomes.calculate_terrain_properties_with_fields(x_array, z_array, seed)


def calculate_runtime_water_properties(x_array, z_array, h_map, m_map, temp_map, rareza_map, seed, terrain_fields=None):
    if _terrain_mode() in {"fast_noise_lite", "noise_lite"}:
        return calculate_fast_noise_water_properties(x_array, z_array, h_map, m_map, temp_map, rareza_map, seed)
    return biomes.calculate_water_properties(x_array, z_array, h_map, m_map, temp_map, rareza_map, seed, terrain_fields=terrain_fields)

def calculate_chunk_data_background(cx, cz, size, subdivisions, seed):
    step = size / subdivisions
    world_start_x, world_start_z = cx * size, cz * size
    detail_density = _world_detail_density()

    # FIX O: calculamos el chunk con un borde extra invisible.
    # Esto evita costuras entre chunks porque el suavizado de agua/lagos ya no
    # depende solo de los datos internos de cada chunk.
    PAD = 6
    lin_x_ext = world_start_x + (np.arange(-PAD, subdivisions + 1 + PAD) * step)
    lin_z_ext = world_start_z + (np.arange(-PAD, subdivisions + 1 + PAD) * step)
    gx_ext, gz_ext = np.meshgrid(lin_x_ext, lin_z_ext, indexing='ij')

    terrain_props, terrain_fields = calculate_runtime_terrain_properties_with_fields(gx_ext, gz_ext, seed)
    h_ext, m_ext, c_ext, temp_ext, rareza_ext = terrain_props
    water_ext, shore_ext, water_level_ext, water_depth_ext = calculate_runtime_water_properties(
        gx_ext, gz_ext, h_ext, m_ext, temp_ext, rareza_ext, seed, terrain_fields=terrain_fields
    )

    sl = slice(PAD, PAD + subdivisions + 1)
    gx, gz = gx_ext[sl, sl], gz_ext[sl, sl]
    h_map, m_map, c_map, temp_map, rareza_map = h_ext[sl, sl], m_ext[sl, sl], c_ext[sl, sl], temp_ext[sl, sl], rareza_ext[sl, sl]
    water_mask, shore_mask = water_ext[sl, sl], shore_ext[sl, sl]
    water_level_map, water_depth_map = water_level_ext[sl, sl], water_depth_ext[sl, sl]

    # Stage 28 FIX F:
    # El fondo del lago se suaviza y profundiza de forma gradual.
    # No queremos un agujero duro, sino una cuenca curva con mejor lectura.
    visual_h_map = h_map.copy()
    smooth_h = biomes._neighbor_mean(visual_h_map, radius=1)
    water_center = np.clip(water_depth_map / 3.8, 0.0, 1.0)
    shore_blend = shore_mask.astype(float) * 0.30
    water_blend = water_mask.astype(float) * (0.42 + water_center * 0.30)
    visual_h_map = visual_h_map * (1.0 - water_blend - shore_blend) + smooth_h * (water_blend + shore_blend)
    visual_h_map = np.where(water_mask, visual_h_map - (0.25 + water_center * 1.15), visual_h_map)
    h_map = visual_h_map

    if (cx, cz) not in _height_cache:
        _height_cache[(cx, cz)] = h_map

    quads_data, grass_data, rock_data, deco_data, water_data = [], [], [], [], []
    np.random.seed(seed + cx * 73 + cz * 37)

    for i in range(subdivisions):
        for j in range(subdivisions):
            x1 = world_start_x + i*step
            x2 = world_start_x + (i+1)*step
            z1 = world_start_z + j*step
            z2 = world_start_z + (j+1)*step

            h00, h10, h11, h01 = h_map[i,j], h_map[i+1,j], h_map[i+1,j+1], h_map[i,j+1]
            avg_h = (h00+h10+h11+h01)/4.0
            avg_m = (m_map[i,j]+m_map[i+1,j]+m_map[i+1,j+1]+m_map[i,j+1])/4.0
            avg_temp = (temp_map[i,j]+temp_map[i+1,j]+temp_map[i+1,j+1]+temp_map[i,j+1])/4.0
            avg_rareza = (rareza_map[i,j]+rareza_map[i+1,j]+rareza_map[i+1,j+1]+rareza_map[i,j+1])/4.0

            es_cueva = bool(c_map[i,j])
            color, has_grass, rock_chance, rock_type, deco_type, deco_chance, rock_color_base = \
                biomes.get_biome_color_and_features(avg_h, avg_m, es_cueva, avg_temp, avg_rareza)
            if PERF_AGGRESSIVE:
                rock_chance *= detail_density["rock"]
                deco_chance *= detail_density["deco"]

            # Stage 28: lagos organicos interiores.
            avg_water = (float(water_mask[i,j]) + float(water_mask[i+1,j]) + float(water_mask[i+1,j+1]) + float(water_mask[i,j+1])) / 4.0
            avg_shore = (float(shore_mask[i,j]) + float(shore_mask[i+1,j]) + float(shore_mask[i+1,j+1]) + float(shore_mask[i,j+1])) / 4.0
            w00, w10, w11, w01 = water_level_map[i,j], water_level_map[i+1,j], water_level_map[i+1,j+1], water_level_map[i,j+1]
            avg_wlevel = (w00 + w10 + w11 + w01) / 4.0
            level_spread = max(w00, w10, w11, w01) - min(w00, w10, w11, w01)
            avg_depth = max(0.0, avg_wlevel - avg_h)

            # Solo dibujamos agua donde la celda esta bastante segura y su terraza no cambia demasiado.
            # Esto corta el bug de una gran placa plana atravesando chunks/alturas.
            es_agua = (avg_water >= 0.22) and (level_spread <= 0.65)
            # Oasis solo como anillo de orilla. No usamos avg_water como fallback porque
            # eso hacía que la vegetación se comiera el lago cuando el agua no dibujaba.
            es_orilla = (not es_agua) and (avg_shore >= 0.10)
            oasis_factor = avg_shore if es_orilla else 0.0
            local_deco_type = deco_type
            local_deco_chance = deco_chance

            if es_agua:
                # Dentro del agua el color del suelo casi se conserva; solo se enfria un poco.
                fondo = [0.18, 0.34, 0.25] if avg_m > 0.45 else [0.28, 0.34, 0.24]
                color = biomes._lerp_color(color, fondo, 0.08)
                has_grass = False
                rock_chance = min(rock_chance, 0.0020)
                local_deco_chance = 0.0
            elif es_orilla:
                # Oasis alrededor del lago: incluso el desierto reverdece aquí.
                oasis_green = [0.22, 0.52, 0.20]
                color = biomes._lerp_color(color, oasis_green, min(0.55, 0.22 + oasis_factor * 0.40))
                has_grass = True
                rock_chance *= 0.45
                # El oasis debe tener vida, pero no una muralla de árboles.
                # Los árboles se agregan aparte con probabilidad muy baja; aquí priorizamos pasto/flores/arbustos.
                local_deco_type = None
                local_deco_chance = 0.0

            ruido = np.random.choice([0.0, 0.012, -0.012])
            quads_data.append(([max(0,min(1,c+ruido)) for c in color],
                               (x1,h00,z1),(x2,h10,z1),(x2,h11,z2),(x1,h01,z2)))

            if es_agua:
                wcol = biomes.get_water_color(avg_depth, avg_m, avg_temp)
                # Ligera variacion para que lagos enormes no parezcan plastico.
                wnoise = np.random.choice([0.0, 0.006, -0.006])
                wcol = [max(0.0, min(1.0, c + wnoise)) for c in wcol]
                # Superficie por terraza local. No es un oceano global: cada lago/chunk puede
                # tener altura distinta. En una misma celda usamos sus 4 esquinas para evitar
                # placas gigantes perfectamente planas cuando cruza una transicion.
                wy = _water_surface_y(avg_wlevel, avg_h)
                # Leve solape para que no se vea una costura negra entre chunks/celdas.
                overlap = step * 0.012
                water_data.append((wcol,
                                   (x1 - overlap, wy, z1 - overlap),
                                   (x2 + overlap, wy, z1 - overlap),
                                   (x2 + overlap, wy, z2 + overlap),
                                   (x1 - overlap, wy, z2 + overlap)))

            # Escombros cueva
            if es_cueva and np.random.rand()<0.2:
                rx = np.random.uniform(x1,x2)
                rz = np.random.uniform(z1,z2)
                sx,sy,sz = np.random.uniform(0.6,1.4), np.random.uniform(3,6), np.random.uniform(0.6,1.4)
                rock_data.append((rx, avg_h, rz, sx, sy, sz, [0.3,0.3,0.32]))

            # Pasto
            grass_trigger = (0.30 if not es_orilla else 0.42) * detail_density["grass"]
            if has_grass and np.random.rand()<grass_trigger:
                grass_count = np.random.randint(1,3) if not es_orilla else np.random.randint(2,4)
                for _ in range(grass_count):
                    gx = np.random.uniform(x1,x2)
                    gz = np.random.uniform(z1,z2)
                    ix = max(0, min(subdivisions-1, int((gx-world_start_x)/size*subdivisions)))
                    iz = max(0, min(subdivisions-1, int((gz-world_start_z)/size*subdivisions)))
                    grass_h = np.random.uniform(0.12,0.22) if not es_orilla else np.random.uniform(0.18,0.38)
                    grass_data.append(([max(0,min(1,c+np.random.uniform(-0.03,0.03))) for c in color],
                                       gx, h_map[ix,iz], gz, grass_h))

            # Rocas
            if not es_cueva and np.random.rand() < rock_chance:
                rx = np.random.uniform(x1,x2)
                rz = np.random.uniform(z1,z2)
                np.random.seed(int(abs(rx*500+rz*500))%1000)

                def interp(x,z):
                    tx = (x-x1)/step
                    tz = (z-z1)/step
                    h0 = h00*(1-tx)+h10*tx
                    h1 = h01*(1-tx)+h11*tx
                    return h0*(1-tz)+h1*tz
                suelo = interp(rx,rz)

                if rock_color_base is not None:
                    base = rock_color_base
                    if rock_type=="gigante":   sx,sy,sz = np.random.uniform(1.25,3.0), np.random.uniform(1.0,2.5), np.random.uniform(1.25,3.0)
                    elif rock_type=="grande":  sx,sy,sz = np.random.uniform(0.6,1.25), np.random.uniform(0.4,1.0), np.random.uniform(0.6,1.25)
                    else:                      sx,sy,sz = np.random.uniform(0.15,0.45), np.random.uniform(0.1,0.35), np.random.uniform(0.15,0.45)
                else:
                    if rock_type=="gigante":   sx,sy,sz = np.random.uniform(2.5,6.0), np.random.uniform(2.0,5.0), np.random.uniform(2.5,6.0); base=[0.38,0.38,0.40]
                    elif rock_type=="grande":  sx,sy,sz = np.random.uniform(1.2,2.5), np.random.uniform(0.8,2.0), np.random.uniform(1.2,2.5); base=[0.45,0.42,0.38]
                    else:                      sx,sy,sz = np.random.uniform(0.3,0.9), np.random.uniform(0.2,0.7), np.random.uniform(0.3,0.9); base=[0.42,0.42,0.42]

                col_rock = [max(0,min(1,c+np.random.uniform(-0.03,0.03))) for c in base]
                rock_data.append((rx, suelo, rz, sx, sy, sz, col_rock))

                if rock_type in ("gigante","grande") and np.random.rand()<0.1:
                    ssx, ssy, ssz = sx*0.6, sy*0.3, sz*0.6
                    top = suelo + sy
                    col_small = [min(1,c*1.2) for c in col_rock]
                    rock_data.append((rx, top, rz, ssx, ssy, ssz, col_small))

            # Decoraciones
            if local_deco_type and np.random.rand() < local_deco_chance:
                rx = np.random.uniform(x1,x2)
                rz = np.random.uniform(z1,z2)
                tx = (rx-x1)/step
                tz = (rz-z1)/step
                h0 = h00*(1-tx)+h10*tx
                h1 = h01*(1-tx)+h11*tx
                suelo = h0*(1-tz)+h1*tz
                deco_variant = np.random.choice(["rojo","amarillo"]) if local_deco_type=="flores" else "normal"
                if local_deco_type in ("arbol_bosque", "arbol_pantano") and es_orilla and np.random.rand() < 0.25:
                    deco_variant = "alto"
                deco_data.append((local_deco_type, rx, suelo, rz, deco_variant))

            # Flores, arbustos y muy pocos árboles alrededor del lago para crear sensacion de oasis.
            if es_orilla:
                # Árboles raros: el anillo se lee como oasis sin comerse el lago ni matar rendimiento.
                if np.random.rand() < ((0.003 + oasis_factor * 0.004) * detail_density["oasis_tree"]):
                    rx = np.random.uniform(x1,x2)
                    rz = np.random.uniform(z1,z2)
                    tx = (rx-x1)/step
                    tz = (rz-z1)/step
                    h0 = h00*(1-tx)+h10*tx
                    h1 = h01*(1-tx)+h11*tx
                    suelo = h0*(1-tz)+h1*tz
                    tree_type = "arbol_pantano" if avg_m > 0.62 else "arbol_bosque"
                    deco_data.append((tree_type, rx, suelo, rz, "normal"))
                if np.random.rand() < ((0.08 + oasis_factor * 0.12) * detail_density["deco"]):
                    rx = np.random.uniform(x1,x2)
                    rz = np.random.uniform(z1,z2)
                    tx = (rx-x1)/step
                    tz = (rz-z1)/step
                    h0 = h00*(1-tx)+h10*tx
                    h1 = h01*(1-tx)+h11*tx
                    suelo = h0*(1-tz)+h1*tz
                    deco_data.append(("flores", rx, suelo, rz, np.random.choice(["rojo","amarillo"])))
                if np.random.rand() < ((0.045 + oasis_factor * 0.060) * detail_density["deco"]):
                    rx = np.random.uniform(x1,x2)
                    rz = np.random.uniform(z1,z2)
                    tx = (rx-x1)/step
                    tz = (rz-z1)/step
                    h0 = h00*(1-tx)+h10*tx
                    h1 = h01*(1-tx)+h11*tx
                    suelo = h0*(1-tz)+h1*tz
                    deco_data.append(("arbusto_verde", rx, suelo, rz, "normal"))

    return cx, cz, quads_data, grass_data, rock_data, deco_data, water_data, h_map

def terrain_worker_process(pipe, size, sub, seed):
    while True:
        try:
            msg = pipe.recv()
            if msg=="STOP": break
            pipe.send(calculate_chunk_data_background(msg[0], msg[1], size, sub, seed))
        except: break


def _shade_color(color, factor):
    return tuple(max(0.0, min(1.0, float(c) * factor)) for c in color)


def _add_box_to_mesh(mesh, name, cx, cy, cz, sx, sy, sz, color, material=None):
    """Caja simple neutral para MeshData. Sirve para rocas/deco rumbo a Vulkan."""
    material = material or name
    batch = mesh.batch(name, primitive="quads", material=material, alpha=1.0)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy, cy + sy
    z0, z1 = cz - hz, cz + hz
    front = _shade_color(color, 1.00)
    back = _shade_color(color, 0.70)
    side = _shade_color(color, 0.82)
    top = _shade_color(color, 1.15)
    bottom = _shade_color(color, 0.55)
    batch.add_quad(front,  (x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1))
    batch.add_quad(back,   (x1,y0,z0), (x0,y0,z0), (x0,y1,z0), (x1,y1,z0))
    batch.add_quad(side,   (x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0))
    batch.add_quad(side,   (x1,y0,z1), (x1,y0,z0), (x1,y1,z0), (x1,y1,z1))
    batch.add_quad(top,    (x0,y1,z1), (x1,y1,z1), (x1,y1,z0), (x0,y1,z0))
    batch.add_quad(bottom, (x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1))

def _add_shadow_to_mesh(mesh, cx, cy, cz, sx, sz, alpha=0.12):
    """Sombra plana barata en MeshData; reemplaza shadows legacy para arboles."""
    batch = mesh.batch("shadows", primitive="quads", material="shadow", alpha=alpha)
    col = (0.03, 0.03, 0.04, alpha)
    x0, x1 = cx - sx * 0.5, cx + sx * 0.5
    z0, z1 = cz - sz * 0.5, cz + sz * 0.5
    y = cy + 0.018
    batch.add_quad(col, (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))


def _add_leaf_impostor_to_mesh(mesh, cx, cy, cz, width, height, depth, main_color, dark_color=None, light_color=None):
    """Copa tipo billboard: pocos planos cruzados en vez de muchas cajas."""
    batch = mesh.batch("tree_leaf_impostors", primitive="quads", material="tree_leaf", alpha=1.0)
    planes = int(_world_detail_density().get("leaf_planes", 3))
    dark_color = dark_color or _shade_color(main_color, 0.72)
    light_color = light_color or _shade_color(main_color, 1.16)
    xh = width * 0.5
    zh = depth * 0.5
    y0 = cy - height * 0.5
    y1 = cy + height * 0.5

    # Dos planos cruzados principales: silueta 3D barata estilo N64.
    batch.add_quad(main_color, (cx - xh, y0, cz), (cx + xh, y0, cz), (cx + xh, y1, cz), (cx - xh, y1, cz))
    if planes >= 2:
        batch.add_quad(dark_color, (cx, y0, cz - zh), (cx, y0, cz + zh), (cx, y1, cz + zh), (cx, y1, cz - zh))

    # Un plano diagonal pequeno rompe la cruz perfecta sin volver a llenar de cubos.
    if planes >= 3:
        dx = xh * 0.70
        dz = zh * 0.70
        batch.add_quad(light_color, (cx - dx, y0 + height * 0.16, cz - dz), (cx + dx, y0 + height * 0.16, cz + dz), (cx + dx, y1, cz + dz), (cx - dx, y1, cz - dz))


def _add_deco_impostor_to_mesh(mesh, name, cx, cy, cz, width, height, color, color2=None, material="plant"):
    """Decoracion baja en planos cruzados: barata y legible a media distancia."""
    batch = mesh.batch(name, primitive="quads", material=material, alpha=1.0)
    planes = int(_world_detail_density().get("deco_planes", 2))
    color2 = color2 or _shade_color(color, 0.82)
    half = width * 0.5
    y0 = cy
    y1 = cy + height
    batch.add_quad(color,  (cx - half, y0, cz), (cx + half, y0, cz), (cx + half, y1, cz), (cx - half, y1, cz))
    if planes >= 2:
        batch.add_quad(color2, (cx, y0, cz - half), (cx, y0, cz + half), (cx, y1, cz + half), (cx, y1, cz - half))


def _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant):
    """Arbol boxel simplificado en MeshData.

    No intenta copiar cada cubo legacy, pero conserva silueta: tronco + copa por bloques.
    Esto reduce llamadas inmediatas de OpenGL y deja los arboles listos para buffers Vulkan.
    """
    detail = _world_detail_density()
    tree_layers = int(detail.get("tree_layers", 2))
    low_tree = tree_layers <= 1
    if d_type == "arbol_bosque":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.15, 2.0, 0.13)
        trunk = [0.36, 0.23, 0.13]
        leaf_main = [0.10, 0.38, 0.13]
        leaf_dark = [0.07, 0.30, 0.09]
        leaf_light = [0.13, 0.45, 0.16]
        alto = 3.10 if variant == "alto" else 2.65
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.34, alto, 0.34, trunk, "tree_trunk")
        top = dy + alto
        core_size = 0.42 if low_tree else 0.58
        _add_box_to_mesh(mesh, "tree_leaves_core", dx, top - 0.18, dz, core_size, 0.34, core_size, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.35, dz, 1.95, 1.34, 1.78, leaf_main, leaf_dark, leaf_light)
        if not low_tree:
            _add_leaf_impostor_to_mesh(mesh, dx + 0.18, top + 0.84, dz - 0.10, 1.18, 0.72, 1.02, leaf_light, leaf_main, leaf_light)
        return True

    if d_type == "arbol_pantano":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.0, 1.95, 0.14)
        trunk = [0.22, 0.16, 0.10]
        leaf_main = [0.12, 0.28, 0.12]
        leaf_dark = [0.08, 0.20, 0.08]
        leaf_sick = [0.18, 0.34, 0.12]
        alto = 2.55
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.36, alto, 0.36, trunk, "tree_trunk")
        top = dy + alto
        core_size = 0.40 if low_tree else 0.56
        _add_box_to_mesh(mesh, "tree_leaves_core", dx, top - 0.20, dz, core_size, 0.32, core_size, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.25, dz, 1.78, 1.08, 1.62, leaf_main, leaf_dark, leaf_sick)
        if not low_tree:
            _add_leaf_impostor_to_mesh(mesh, dx - 0.14, top + 0.76, dz + 0.10, 1.06, 0.62, 0.94, leaf_sick, leaf_dark, leaf_sick)
        # Musgo/raíces colgantes como cajas finas.
        if not low_tree:
            _add_box_to_mesh(mesh, "tree_moss", dx-0.26, dy+1.12, dz+0.18, 0.08, 0.82, 0.08, [0.10,0.20,0.09], "tree_leaf")
            _add_box_to_mesh(mesh, "tree_moss", dx+0.30, dy+1.02, dz-0.14, 0.07, 0.66, 0.07, [0.10,0.20,0.09], "tree_leaf")
        return True

    if d_type == "arbol_seco":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 1.65, 1.55, 0.10)
        trunk = [0.48, 0.36, 0.20]
        leaf = [0.56, 0.45, 0.20]
        leaf_dark = [0.45, 0.34, 0.15]
        alto = 2.45
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.28, alto, 0.28, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_box_to_mesh(mesh, "tree_leaves_core", dx, top + 0.02, dz, 0.42, 0.24, 0.40, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.38, dz, 1.18, 0.76, 1.02, leaf, leaf_dark, [0.62,0.50,0.24])
        return True

    return False


def _add_rock_to_mesh(mesh, bx, base_y, bz, sx, sy, sz, col):
    """Roca prismática en MeshData: lados en quads y tapa en triangles."""
    if int(_world_detail_density().get("rock_detail", 2)) <= 1:
        _add_box_to_mesh(mesh, "rocks_simple", bx, base_y, bz, sx, sy, sz, col, "rock")
        return
    c_top = _shade_color(col, 1.12)
    c_s1 = _shade_color(col, 0.92)
    c_s2 = _shade_color(col, 0.78)
    c_s3 = _shade_color(col, 0.68)
    sides = mesh.batch("rocks_sides", primitive="quads", material="rock", alpha=1.0)
    caps = mesh.batch("rocks_caps", primitive="triangles", material="rock", alpha=1.0)
    hx, hz = sx/2, sz/2
    seed = math.sin(bx * 12.9898 + bz * 78.233) * 43758.5453
    frac = seed - math.floor(seed)
    frac2 = (seed * 1.371) - math.floor(seed * 1.371)
    frac3 = (seed * 1.917) - math.floor(seed * 1.917)
    frac4 = (seed * 2.231) - math.floor(seed * 2.231)
    inset = 0.10 + 0.10 * frac
    lift0 = sy * (0.90 + 0.10 * frac2)
    lift1 = sy * (0.88 + 0.14 * frac3)
    lift2 = sy * (0.92 + 0.08 * frac4)
    lift3 = sy * (0.86 + 0.12 * frac)
    b0 = (bx-hx, base_y, bz-hz)
    b1 = (bx+hx, base_y, bz-hz)
    b2 = (bx+hx, base_y, bz+hz)
    b3 = (bx-hx, base_y, bz+hz)
    t0 = (bx-hx*(1.0-inset), base_y + lift0, bz-hz*(1.0-0.08-frac*0.04))
    t1 = (bx+hx*(1.0-inset*0.8), base_y + lift1, bz-hz*(1.0-inset))
    t2 = (bx+hx*(1.0-0.06-frac2*0.05), base_y + lift2, bz+hz*(1.0-inset*0.9))
    t3 = (bx-hx*(1.0-inset), base_y + lift3, bz+hz*(1.0-0.05-frac3*0.05))
    peak = (bx + (frac-0.5)*hx*0.25, base_y + sy * (1.02 + 0.08 * frac2), bz + (frac3-0.5)*hz*0.25)
    sides.add_quad(c_s1, b0, b1, t1, t0)
    sides.add_quad(c_s2, b1, b2, t2, t1)
    sides.add_quad(c_s3, b2, b3, t3, t2)
    sides.add_quad(c_s2, b3, b0, t0, t3)
    caps.add_triangle(c_top, t0, t1, peak)
    caps.add_triangle(c_top, t1, t2, peak)
    caps.add_triangle(c_top, t2, t3, peak)
    caps.add_triangle(c_top, t3, t0, peak)


def _add_small_deco_to_mesh(mesh, d_type, dx, dy, dz, variant):
    """Migra decoracion y arboles a MeshData. Devuelve False si debe quedarse legacy."""
    if d_type in ("arbol_bosque", "arbol_pantano", "arbol_seco"):
        return _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant)
    if d_type == "hongo":
        _add_deco_impostor_to_mesh(mesh, "deco_mushrooms", dx, dy, dz, 0.14, 0.20, [0.90,0.86,0.72], [0.72,0.64,0.52], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_mushrooms", dx, dy+0.12, dz, 0.30, 0.13, [0.85,0.15,0.15], [0.62,0.08,0.10], "plant")
        return True
    if d_type == "cactus":
        _add_box_to_mesh(mesh, "deco_cactus", dx, dy, dz, 0.22, 1.6, 0.22, [0.13,0.48,0.16], "plant")
        _add_box_to_mesh(mesh, "deco_cactus", dx+0.22, dy+0.65, dz, 0.18, 0.55, 0.18, [0.12,0.42,0.14], "plant")
        _add_box_to_mesh(mesh, "deco_cactus", dx-0.20, dy+0.85, dz, 0.16, 0.45, 0.16, [0.12,0.42,0.14], "plant")
        return True
    if d_type == "cristal":
        _add_rock_to_mesh(mesh, dx, dy, dz, 0.22, 0.70, 0.22, [0,0.9,0.9])
        return True
    if d_type == "flores":
        col_f = [0.85,0.15,0.45] if variant == "rojo" else [0.9,0.8,0.1]
        _add_deco_impostor_to_mesh(mesh, "deco_flowers", dx, dy, dz, 0.18, 0.34, [0.18,0.48,0.18], [0.12,0.36,0.13], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_flowers", dx, dy+0.20, dz, 0.20, 0.10, col_f, _shade_color(col_f, 0.74), "plant")
        return True
    if d_type == "arbusto_verde":
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx, dy, dz, 0.78, 0.48, [0.12,0.44,0.14], [0.08,0.32,0.10], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx+0.18, dy+0.10, dz-0.08, 0.52, 0.34, [0.16,0.52,0.18], [0.10,0.36,0.12], "plant")
        return True
    if d_type == "arbusto_seco":
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx, dy, dz, 0.68, 0.42, [0.46,0.38,0.26], [0.34,0.26,0.16], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx-0.16, dy+0.08, dz+0.10, 0.42, 0.28, [0.38,0.30,0.18], [0.30,0.22,0.12], "plant")
        return True
    return False

def build_chunk_mesh_data(cx, cz, quads, grass, rocks, deco, water=None, size=100, lod="detail", height_map=None):
    """Convierte los datos procedurales del chunk a un formato neutral.

    Esta es la pieza importante rumbo a Vulkan: el chunk ya puede existir como
    datos de malla antes de ser subido a OpenGL. En etapas posteriores, rocas y
    decoraciones tambien dejaran de ser legacy.
    """
    if water is None:
        water = []
    mesh = ChunkMeshData(coord=(int(cx), int(cz)), size=float(size), lod=str(lod), height_map=height_map)

    terrain_batch = mesh.batch("terrain", primitive="quads", material="terrain", alpha=1.0)
    for col, v0, v1, v2, v3 in quads:
        terrain_batch.add_quad(col, v0, v1, v2, v3)

    if water:
        water_batch = mesh.batch("water", primitive="quads", material="water", alpha=0.34)
        for item in water:
            col, v0, v1, v2, v3 = item
            water_batch.add_quad(tuple(col) + (0.34,), v0, v1, v2, v3)

    if grass:
        grass_batch = mesh.batch("grass", primitive="quads", material="grass", alpha=1.0)
        grass_planes = int(_world_detail_density().get("grass_planes", 2))
        for gcol, gx, gy, gz, gh in grass:
            w = 0.05
            grass_batch.add_quad(gcol, (gx-w, gy, gz-w), (gx+w, gy+gh, gz+w), (gx+w, gy+gh, gz+w), (gx-w, gy+gh, gz-w))
            if grass_planes >= 2:
                grass_batch.add_quad(gcol, (gx-w, gy, gz+w), (gx+w, gy+gh, gz-w), (gx+w, gy+gh, gz-w), (gx-w, gy+gh, gz+w))

    # Stage31 Pre-K: rocas, decoracion pequeña y arboles simplificados ya entran a MeshData.
    # Esto baja el acoplamiento a OpenGL y prepara buffers de Vulkan.
    for rock in (rocks or []):
        try:
            _add_rock_to_mesh(mesh, *rock)
        except Exception:
            mesh.legacy_rocks.append(rock)

    for item in (deco or []):
        try:
            if not _add_small_deco_to_mesh(mesh, *item):
                # Decoracion compleja no migrada queda legacy por ahora.
                mesh.legacy_deco.append(item)
        except Exception:
            mesh.legacy_deco.append(item)
    return mesh


def _draw_mesh_batch(batch):
    if not batch.vertices:
        return
    mat = get_material(getattr(batch, "material", "default"))
    translucent = bool(getattr(batch, "blend", False) or mat.blend or float(getattr(batch, "alpha", mat.alpha)) < 0.999)
    if translucent:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE if not mat.depth_write else GL_TRUE)
    glBegin(GL_QUADS if batch.primitive == "quads" else GL_TRIANGLES)
    for color, vertex in zip(batch.colors, batch.vertices):
        if len(color) >= 4 or batch.material == "water":
            a = float(color[3]) if len(color) >= 4 else float(batch.alpha)
            glColor4f(float(color[0]), float(color[1]), float(color[2]), a)
        else:
            glColor3f(float(color[0]), float(color[1]), float(color[2]))
        glVertex3f(float(vertex[0]), float(vertex[1]), float(vertex[2]))
    glEnd()
    if translucent:
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)


def build_gpu_list_from_mesh_data(mesh_data):
    """Sube ChunkMeshData al backend OpenGL actual usando display lists.

    Vulkan no usara esta funcion; usara el mismo mesh_data para crear buffers.
    """
    list_id = glGenLists(1)
    glNewList(list_id, GL_COMPILE)

    # Stage31 Pre-L: orden por material/sort_order. Esto imita el orden de pipelines
    # que luego usara Vulkan: opacos primero, translucidos al final.
    try:
        ordered_batches = mesh_data.sorted_batches()
    except Exception:
        ordered_batches = sorted(mesh_data.batches.values(), key=lambda b: getattr(b, "sort_order", 100))

    for batch in ordered_batches:
        if not getattr(batch, "blend", False) and getattr(batch, "material", "") not in ("water", "shadow"):
            _draw_mesh_batch(batch)

    # Respaldo temporal: cualquier decoracion compleja aun usa el renderer legacy.
    for r in mesh_data.legacy_rocks:
        _draw_optimized_rock(*r)
    for d in mesh_data.legacy_deco:
        _draw_decorations(*d)

    for batch in ordered_batches:
        if getattr(batch, "blend", False) or getattr(batch, "material", "") in ("water", "shadow"):
            _draw_mesh_batch(batch)

    glEndList()
    return list_id


def build_gpu_list_from_data(quads, grass, rocks, deco, water=None):
    # Compatibilidad con codigo viejo: convierte a MeshData y luego sube a OpenGL.
    mesh = build_chunk_mesh_data(0, 0, quads, grass, rocks, deco, water or [], size=100, lod="legacy")
    return build_gpu_list_from_mesh_data(mesh)

def _draw_optimized_rock(bx, base_y, bz, sx, sy, sz, col):
    # Roca prismática simple pero irregular, con ligera teselación y tapa no perfectamente plana.
    c_top = [min(1,c*1.12) for c in col]
    c_s1 = [c*0.92 for c in col]
    c_s2 = [c*0.78 for c in col]
    c_s3 = [c*0.68 for c in col]
    hx, hz = sx/2, sz/2

    # Variación determinista basada en la posición para romper el aspecto de cubo perfecto.
    seed = math.sin(bx * 12.9898 + bz * 78.233) * 43758.5453
    frac = seed - math.floor(seed)
    frac2 = (seed * 1.371) - math.floor(seed * 1.371)
    frac3 = (seed * 1.917) - math.floor(seed * 1.917)
    frac4 = (seed * 2.231) - math.floor(seed * 2.231)
    inset = 0.10 + 0.10 * frac
    lift0 = sy * (0.90 + 0.10 * frac2)
    lift1 = sy * (0.88 + 0.14 * frac3)
    lift2 = sy * (0.92 + 0.08 * frac4)
    lift3 = sy * (0.86 + 0.12 * frac)

    # Base.
    b0 = [bx-hx, base_y, bz-hz]
    b1 = [bx+hx, base_y, bz-hz]
    b2 = [bx+hx, base_y, bz+hz]
    b3 = [bx-hx, base_y, bz+hz]

    # Parte alta ligeramente estrechada y desplazada.
    t0 = [bx-hx*(1.0-inset), base_y + lift0, bz-hz*(1.0-0.08-frac*0.04)]
    t1 = [bx+hx*(1.0-inset*0.8), base_y + lift1, bz-hz*(1.0-inset)]
    t2 = [bx+hx*(1.0-0.06-frac2*0.05), base_y + lift2, bz+hz*(1.0-inset*0.9)]
    t3 = [bx-hx*(1.0-inset), base_y + lift3, bz+hz*(1.0-0.05-frac3*0.05)]

    # Pico superior muy sutil para romper la tapa plana.
    peak = [bx + (frac-0.5)*hx*0.25, base_y + sy * (1.02 + 0.08 * frac2), bz + (frac3-0.5)*hz*0.25]

    glBegin(GL_QUADS)
    # Lados
    glColor3fv(c_s1); glVertex3fv(b0); glVertex3fv(b1); glVertex3fv(t1); glVertex3fv(t0)
    glColor3fv(c_s2); glVertex3fv(b1); glVertex3fv(b2); glVertex3fv(t2); glVertex3fv(t1)
    glColor3fv(c_s3); glVertex3fv(b2); glVertex3fv(b3); glVertex3fv(t3); glVertex3fv(t2)
    glColor3fv(c_s2); glVertex3fv(b3); glVertex3fv(b0); glVertex3fv(t0); glVertex3fv(t3)
    glEnd()

    # Tapa subdividida en 4 triángulos para dar una teselación muy básica.
    glBegin(GL_TRIANGLES)
    glColor3fv(c_top); glVertex3fv(t0); glVertex3fv(t1); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t1); glVertex3fv(t2); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t2); glVertex3fv(t3); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t3); glVertex3fv(t0); glVertex3fv(peak)
    glEnd()





def _draw_ground_shadow(cx, y, cz, sx, sz, alpha=0.10):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glColor4f(0.02, 0.03, 0.02, alpha)
    glBegin(GL_QUADS)
    glVertex3f(cx - sx*0.5, y + 0.01, cz - sz*0.5)
    glVertex3f(cx + sx*0.5, y + 0.01, cz - sz*0.5)
    glVertex3f(cx + sx*0.5, y + 0.01, cz + sz*0.5)
    glVertex3f(cx - sx*0.5, y + 0.01, cz + sz*0.5)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

def _draw_round_trunk(cx, base_y, cz, radius, height, col, segments=5):
    """Tronco pseudo redondo con teselación muy básica."""
    top_col = [min(1.0, c * 1.10) for c in col]
    for i in range(segments):
        a0 = (i / segments) * math.pi * 2.0
        a1 = ((i + 1) / segments) * math.pi * 2.0
        x0 = cx + math.cos(a0) * radius
        z0 = cz + math.sin(a0) * radius
        x1 = cx + math.cos(a1) * radius
        z1 = cz + math.sin(a1) * radius
        shade = 0.78 + 0.18 * ((i % 2) / 1.0)
        side_col = [max(0.0, min(1.0, c * shade)) for c in col]
        glBegin(GL_QUADS)
        glColor3fv(side_col)
        glVertex3f(x0, base_y, z0)
        glVertex3f(x1, base_y, z1)
        glVertex3f(x1, base_y + height, z1)
        glVertex3f(x0, base_y + height, z0)
        glEnd()
    # Tapa superior sencilla en abanico
    peak_y = base_y + height
    glBegin(GL_TRIANGLES)
    for i in range(segments):
        a0 = (i / segments) * math.pi * 2.0
        a1 = ((i + 1) / segments) * math.pi * 2.0
        x0 = cx + math.cos(a0) * radius
        z0 = cz + math.sin(a0) * radius
        x1 = cx + math.cos(a1) * radius
        z1 = cz + math.sin(a1) * radius
        glColor3fv(top_col)
        glVertex3f(cx, peak_y + radius * 0.06, cz)
        glVertex3f(x0, peak_y, z0)
        glVertex3f(x1, peak_y, z1)
    glEnd()

def _draw_decorations(d_type, dx, dy, dz, variant):
    # Plantas pequeñas existentes
    if d_type == "hongo":
        _draw_optimized_rock(dx, dy, dz, 0.08,0.16,0.08,[0.9,0.9,0.9])
        _draw_optimized_rock(dx, dy+0.1, dz, 0.24,0.08,0.24,[0.85,0.15,0.15])
    elif d_type == "cactus":
        _draw_optimized_rock(dx, dy, dz, 0.22, 1.6, 0.22, [0.13,0.48,0.16])
        _draw_optimized_rock(dx+0.22, dy+0.65, dz, 0.18, 0.55, 0.18, [0.12,0.42,0.14])
        _draw_optimized_rock(dx-0.20, dy+0.85, dz, 0.16, 0.45, 0.16, [0.12,0.42,0.14])
    elif d_type == "cristal":
        _draw_optimized_rock(dx, dy, dz, 0.22,0.7,0.22, [0,0.9,0.9])
    elif d_type == "flores":
        _draw_optimized_rock(dx, dy, dz, 0.04,0.3,0.04, [0.2,0.5,0.2])
        col_f = [0.85,0.15,0.45] if variant=="rojo" else [0.9,0.8,0.1]
        _draw_optimized_rock(dx, dy+0.15, dz, 0.14,0.06,0.14, col_f)
    elif d_type == "arbusto_verde":
        _draw_optimized_rock(dx, dy, dz, 0.55,0.36,0.55, [0.12,0.44,0.14])
        _draw_optimized_rock(dx+0.22, dy+0.05, dz-0.10, 0.35,0.28,0.35, [0.10,0.38,0.12])
    elif d_type == "arbusto_seco":
        _draw_optimized_rock(dx, dy, dz, 0.45,0.35,0.45, [0.46,0.38,0.26])
        _draw_optimized_rock(dx-0.18, dy+0.06, dz+0.12, 0.28,0.28,0.28, [0.38,0.30,0.18])
    # Árboles con tronco pseudo redondo y copa de 6 cubos teselados.
    elif d_type == "arbol_bosque":
        _draw_ground_shadow(dx, dy, dz, 2.20, 2.05, 0.13)
        trunk = [0.36, 0.23, 0.13]
        leaf_main = [0.10, 0.38, 0.13]
        leaf_dark = [0.07, 0.30, 0.09]
        leaf_light = [0.13, 0.45, 0.16]
        alto = 3.10 if variant == "alto" else 2.65
        _draw_round_trunk(dx, dy, dz, 0.30, alto, trunk, segments=5)
        top = dy + alto

        # Conector central: evita que la copa parezca flotante.
        _draw_optimized_rock(dx, top - 0.16, dz, 0.86, 0.66, 0.86, leaf_dark)

        # Copa frondosa: bloques encimados y conectados.
        _draw_optimized_rock(dx,       top + 0.28, dz,       1.34, 0.82, 1.24, leaf_main)
        _draw_optimized_rock(dx+0.58,  top + 0.18, dz+0.04,  0.92, 0.66, 0.88, leaf_dark)
        _draw_optimized_rock(dx-0.56,  top + 0.16, dz-0.05,  0.90, 0.64, 0.86, leaf_dark)
        _draw_optimized_rock(dx+0.05,  top + 0.15, dz+0.58,  0.92, 0.66, 0.86, leaf_main)
        _draw_optimized_rock(dx-0.05,  top + 0.13, dz-0.58,  0.90, 0.62, 0.84, leaf_main)
        _draw_optimized_rock(dx,       top + 0.78, dz,       0.84, 0.56, 0.80, leaf_light)
        _draw_optimized_rock(dx+0.30,  top + 0.68, dz-0.28,  0.62, 0.42, 0.58, leaf_light)
    elif d_type == "arbol_pantano":
        _draw_ground_shadow(dx, dy, dz, 2.00, 1.95, 0.14)
        trunk = [0.22, 0.16, 0.10]
        leaf_main = [0.12, 0.28, 0.12]
        leaf_dark = [0.08, 0.20, 0.08]
        leaf_sick = [0.18, 0.34, 0.12]
        alto = 2.55
        _draw_round_trunk(dx, dy, dz, 0.32, alto, trunk, segments=5)
        top = dy + alto

        # Copa baja y pesada, conectada al tronco.
        _draw_optimized_rock(dx,       top - 0.16, dz,       0.88, 0.62, 0.84, leaf_dark)
        _draw_optimized_rock(dx,       top + 0.18, dz,       1.24, 0.72, 1.14, leaf_main)
        _draw_optimized_rock(dx+0.50,  top + 0.08, dz+0.10,  0.82, 0.56, 0.76, leaf_dark)
        _draw_optimized_rock(dx-0.48,  top + 0.06, dz-0.08,  0.82, 0.56, 0.76, leaf_dark)
        _draw_optimized_rock(dx,       top + 0.06, dz+0.52,  0.80, 0.54, 0.74, leaf_main)
        _draw_optimized_rock(dx,       top + 0.04, dz-0.50,  0.78, 0.52, 0.72, leaf_main)
        _draw_optimized_rock(dx,       top + 0.60, dz,       0.70, 0.44, 0.66, leaf_sick)

        # Musgo/raíces colgantes.
        _draw_optimized_rock(dx-0.28, dy+1.20, dz+0.22, 0.10, 0.95, 0.10, [0.10,0.20,0.09])
        _draw_optimized_rock(dx+0.32, dy+1.05, dz-0.18, 0.09, 0.78, 0.09, [0.10,0.20,0.09])
        _draw_optimized_rock(dx+0.08, dy+1.36, dz+0.34, 0.08, 0.68, 0.08, [0.12,0.23,0.10])
    elif d_type == "arbol_seco":
        _draw_ground_shadow(dx, dy, dz, 1.65, 1.55, 0.10)
        trunk = [0.48, 0.36, 0.20]
        alto = 2.45
        _draw_round_trunk(dx, dy, dz, 0.24, alto, trunk, segments=7)
        top = dy + alto
        leaf = [0.56, 0.45, 0.20]
        leaf_dark = [0.45, 0.34, 0.15]

        # Árbol seco pero no vacío: copa quebrada conectada.
        _draw_optimized_rock(dx,       top + 0.04, dz,       0.64, 0.34, 0.60, leaf_dark)
        _draw_optimized_rock(dx,       top + 0.32, dz,       0.92, 0.44, 0.82, leaf)
        _draw_optimized_rock(dx+0.48,  top + 0.20, dz,       0.52, 0.28, 0.42, leaf_dark)
        _draw_optimized_rock(dx-0.46,  top + 0.18, dz,       0.48, 0.26, 0.40, leaf_dark)
        _draw_optimized_rock(dx,       top + 0.16, dz+0.44,  0.48, 0.26, 0.40, leaf)
        _draw_optimized_rock(dx,       top + 0.14, dz-0.42,  0.46, 0.24, 0.38, leaf)
        _draw_optimized_rock(dx,       top + 0.64, dz,       0.46, 0.24, 0.40, [0.62,0.50,0.24])



def _draw_water_surfaces(water_quads):
    """
    Superficies de lagos interiores.
    FIX O: base transparente + reflejos blur baratos, sin texturas ni shaders.
    """
    if not water_quads:
        return

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)

    # Base del agua.
    glBegin(GL_QUADS)
    for col, v0, v1, v2, v3 in water_quads:
        glColor4f(col[0], col[1], col[2], 0.38)
        glVertex3f(*v0); glVertex3f(*v1); glVertex3f(*v2); glVertex3f(*v3)
    glEnd()

    # Reflejo blur muy barato: varias bandas grandes, suaves y transparentes.
    # No es reflejo real; solo da vida al agua sin costo alto.
    glBegin(GL_QUADS)
    for idx, (col, v0, v1, v2, v3) in enumerate(water_quads):
        if idx % 3 != 0:
            continue
        x_min = min(v0[0], v1[0], v2[0], v3[0])
        x_max = max(v0[0], v1[0], v2[0], v3[0])
        z_min = min(v0[2], v1[2], v2[2], v3[2])
        z_max = max(v0[2], v1[2], v2[2], v3[2])
        cx = (x_min + x_max) * 0.5
        cz = (z_min + z_max) * 0.5
        wy = (v0[1] + v1[1] + v2[1] + v3[1]) * 0.25 + 0.012
        w = max(0.18, (x_max - x_min) * 0.36)
        l = max(0.28, (z_max - z_min) * 0.78)
        # Variacion determinista para que no se vea como patrón perfecto.
        n = math.sin(cx * 12.9898 + cz * 78.233)
        dx = 0.10 * n
        dz = 0.05 * math.cos(cx * 4.7 + cz * 3.1)
        glColor4f(0.80, 0.93, 1.00, 0.055)
        glVertex3f(cx - w + dx, wy, cz - l + dz)
        glVertex3f(cx + w + dx, wy, cz - l*0.55 + dz)
        glVertex3f(cx + w*0.72 + dx, wy, cz + l + dz)
        glVertex3f(cx - w*0.72 + dx, wy, cz + l*0.55 + dz)
    glEnd()

    # Tinte de borde muy sutil para unir visualmente celdas vecinas.
    glBegin(GL_QUADS)
    for idx, (col, v0, v1, v2, v3) in enumerate(water_quads):
        if idx % 5 != 0:
            continue
        glColor4f(0.45, 0.75, 0.85, 0.035)
        glVertex3f(v0[0], v0[1] + 0.018, v0[2])
        glVertex3f(v1[0], v1[1] + 0.018, v1[2])
        glVertex3f(v2[0], v2[1] + 0.018, v2[2])
        glVertex3f(v3[0], v3[1] + 0.018, v3[2])
    glEnd()

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


def get_terrain_height_at(x, z, seed=1):
    """Altura procedural directa para entidades cuando el chunk aun no esta en cache."""
    gx = np.array([[float(x)]])
    gz = np.array([[float(z)]])
    h_map, _, _, _, _ = calculate_runtime_terrain_properties(gx, gz, seed)
    return float(h_map[0, 0])


def get_cached_height_at(x, z, size=100, subdivisions=90, seed=1):
    """Altura interpolada del chunk cacheado; cae a procedural directo si falta cache."""
    cx = int(math.floor(float(x) / float(size)))
    cz = int(math.floor(float(z) / float(size)))
    h_map = _height_cache.get((cx, cz))
    if h_map is None:
        return get_terrain_height_at(x, z, seed=seed)
    try:
        map_subdivisions = min(int(h_map.shape[0]) - 1, int(h_map.shape[1]) - 1)
    except Exception:
        map_subdivisions = int(subdivisions)
    if map_subdivisions <= 0:
        return get_terrain_height_at(x, z, seed=seed)

    world_start_x = cx * size
    world_start_z = cz * size
    step = float(size) / float(map_subdivisions)
    lx = (float(x) - world_start_x) / step
    lz = (float(z) - world_start_z) / step
    i = max(0, min(map_subdivisions - 1, int(math.floor(lx))))
    j = max(0, min(map_subdivisions - 1, int(math.floor(lz))))
    tx = max(0.0, min(1.0, lx - i))
    tz = max(0.0, min(1.0, lz - j))

    h00 = h_map[i, j]
    h10 = h_map[i + 1, j]
    h01 = h_map[i, j + 1]
    h11 = h_map[i + 1, j + 1]
    h0 = h00 * (1.0 - tx) + h10 * tx
    h1 = h01 * (1.0 - tx) + h11 * tx
    return float(h0 * (1.0 - tz) + h1 * tz)


def get_water_surface_at(x, z, seed=1, size=100, subdivisions=90):
    """Devuelve (hay_agua, nivel_agua) con un muestreo local pequeño."""
    step = 1.2
    offs = np.linspace(-2.0 * step, 2.0 * step, 5)
    gx, gz = np.meshgrid(float(x) + offs, float(z) + offs, indexing='ij')
    h_map, m_map, _, temp_map, rareza_map = calculate_runtime_terrain_properties(gx, gz, seed)
    water_mask, _, water_level_map, _ = calculate_runtime_water_properties(gx, gz, h_map, m_map, temp_map, rareza_map, seed)
    ground_y = get_cached_height_at(x, z, size=size, subdivisions=subdivisions, seed=seed)
    return bool(water_mask[2, 2]), _water_surface_y(water_level_map[2, 2], ground_y)

def get_world_context_at(x, z, seed=1, size=100, subdivisions=90):
    """
    Diagnostico jugable del terreno en un punto.
    Sirve para HUD, depuracion de lagos/capas y activar nado.
    """
    step = 1.2
    offs = np.linspace(-2.0 * step, 2.0 * step, 5)
    gx, gz = np.meshgrid(float(x) + offs, float(z) + offs, indexing='ij')
    h_map, m_map, cave_map, temp_map, rareza_map = calculate_runtime_terrain_properties(gx, gz, seed)
    water_mask, shore_mask, water_level_map, depth_map = calculate_runtime_water_properties(gx, gz, h_map, m_map, temp_map, rareza_map, seed)

    h = float(h_map[2, 2])
    moisture = float(m_map[2, 2])
    temp = float(temp_map[2, 2])
    rareza = float(rareza_map[2, 2])
    water = bool(water_mask[2, 2])
    shore = bool(shore_mask[2, 2])
    ground_y = get_cached_height_at(x, z, size=size, subdivisions=subdivisions, seed=seed)
    water_level = _water_surface_y(water_level_map[2, 2], ground_y)
    depth = max(0.0, water_level - ground_y)

    # Campos macro del sistema de 3 alturas. Usamos funciones internas del bioma
    # para diagnostico; si fallan, caemos a valores neutros.
    try:
        gx1 = np.array([[float(x)]])
        gz1 = np.array([[float(z)]])
        lake_basin = float(biomes._lake_basin_field(gx1, gz1, seed)[0, 0])
        low_macro, high_macro, macro = biomes._macro_layer_field(gx1, gz1, seed)
        low_macro = float(low_macro[0, 0])
        high_macro = float(high_macro[0, 0])
        mesa_strength, _ = biomes._mesa_field(gx1, gz1, seed)
        mesa_strength = float(mesa_strength[0, 0])
    except Exception:
        lake_basin, low_macro, high_macro, mesa_strength = 0.0, 0.0, 0.0, 0.0

    if water:
        biome_name = "Lago"
    elif bool(cave_map[2, 2]):
        biome_name = "Cueva"
    elif h > 15.2:
        biome_name = "Cumbre fría"
    elif h > 12.0 or high_macro > 0.26 or mesa_strength > 0.34:
        biome_name = "Montaña/Meseta"
    elif moisture < 0.35 and temp > 0.45:
        biome_name = "Desierto/Seco"
    elif moisture > 0.68 and h < 8.0:
        biome_name = "Pantano/Humedal"
    elif moisture > 0.55:
        biome_name = "Bosque húmedo"
    else:
        biome_name = "Pradera/Bosque"

    if water:
        if h > 10.0:
            feature = "Dentro de laguna alta"
            layer = "Capa 3 alta/fresca"
        else:
            feature = "Dentro de lago"
            layer = "Capa 1 baja"
    elif shore:
        if h > 10.0:
            feature = "Orilla de laguna alta"
            layer = "Transición alta"
        else:
            feature = "Orilla/Oasis"
            layer = "Transición baja-media"
    elif h > 15.2:
        feature = "Cumbre/altura extrema"
        layer = "Capa 4 cumbre/fria"
    elif mesa_strength > 0.42 or high_macro > 0.28 or h > 12.0:
        feature = "Meseta/altura alta"
        layer = "Capa 3 alta/fresca"
    elif lake_basin > 0.42 or low_macro > 0.24 or h < 5.7:
        feature = "Depresión/zona baja"
        layer = "Capa 1 baja/caliente"
    else:
        feature = "Plano normal"
        layer = "Capa 2 media/templada"

    return {
        "biome": biome_name,
        "feature": feature,
        "layer": layer,
        "in_water": water,
        "on_shore": shore,
        "terrain_height": h,
        "water_level": water_level,
        "water_depth": depth,
        "moisture": moisture,
        "temperature": temp,
        "lake_basin": lake_basin,
        "low_macro": low_macro,
        "high_macro": high_macro,
        "mesa_strength": mesa_strength,
        "rareza": rareza,
    }



def draw_procedural_skybox(size=300.0):
    """Cielo simple con gradiente, barato para OpenGL inmediato."""
    glDisable(GL_DEPTH_TEST)
    half = size * 0.5
    y_low = -20.0
    y_high = size * 0.45
    horizon = [0.70, 0.86, 1.00]
    zenith = [0.20, 0.36, 0.70]

    glBegin(GL_QUADS)
    # cuatro paredes de cielo, degradado vertical
    for a0, a1 in ((0, math.pi/2), (math.pi/2, math.pi), (math.pi, math.pi*1.5), (math.pi*1.5, math.pi*2)):
        x0, z0 = math.cos(a0) * half, math.sin(a0) * half
        x1, z1 = math.cos(a1) * half, math.sin(a1) * half
        glColor3fv(horizon); glVertex3f(x0, y_low, z0); glVertex3f(x1, y_low, z1)
        glColor3fv(zenith);  glVertex3f(x1, y_high, z1); glVertex3f(x0, y_high, z0)
    glEnd()
    glBegin(GL_TRIANGLES)
    for a0, a1 in ((0, math.pi/2), (math.pi/2, math.pi), (math.pi, math.pi*1.5), (math.pi*1.5, math.pi*2)):
        x0, z0 = math.cos(a0) * half, math.sin(a0) * half
        x1, z1 = math.cos(a1) * half, math.sin(a1) * half
        glColor3fv(zenith); glVertex3f(0.0, y_high + 40.0, 0.0)
        glVertex3f(x0, y_high, z0); glVertex3f(x1, y_high, z1)
    glEnd()
    glEnable(GL_DEPTH_TEST)



def build_simple_chunk_list(cx, cz, size=100, seed=1, subdivisions=18):
    """
    LOD temporal/barato para evitar zonas negras mientras el chunk detallado termina.
    Dibuja solo terreno de baja resolucion + agua simple, sin pasto/arboles/rocas.
    """
    step = float(size) / float(subdivisions)
    world_start_x, world_start_z = cx * size, cz * size
    PAD = 6
    lin_x_ext = world_start_x + (np.arange(-PAD, subdivisions + 1 + PAD) * step)
    lin_z_ext = world_start_z + (np.arange(-PAD, subdivisions + 1 + PAD) * step)
    gx_ext, gz_ext = np.meshgrid(lin_x_ext, lin_z_ext, indexing='ij')
    h_ext, m_ext, c_ext, temp_ext, rareza_ext = calculate_runtime_terrain_properties(gx_ext, gz_ext, seed)
    water_ext, shore_ext, water_level_ext, water_depth_ext = calculate_runtime_water_properties(
        gx_ext, gz_ext, h_ext, m_ext, temp_ext, rareza_ext, seed
    )
    sl = slice(PAD, PAD + subdivisions + 1)
    h_map, m_map, c_map, temp_map, rareza_map = h_ext[sl, sl], m_ext[sl, sl], c_ext[sl, sl], temp_ext[sl, sl], rareza_ext[sl, sl]
    water_mask, shore_mask = water_ext[sl, sl], shore_ext[sl, sl]
    water_level_map, water_depth_map = water_level_ext[sl, sl], water_depth_ext[sl, sl]
    # Cache de altura disponible enseguida para físicas aunque falte el chunk detallado.
    _height_cache[(int(cx), int(cz))] = h_map

    list_id = glGenLists(1)
    glNewList(list_id, GL_COMPILE)
    glBegin(GL_QUADS)
    for i in range(subdivisions):
        for j in range(subdivisions):
            x1 = world_start_x + i * step
            x2 = world_start_x + (i + 1) * step
            z1 = world_start_z + j * step
            z2 = world_start_z + (j + 1) * step
            h00, h10, h11, h01 = h_map[i,j], h_map[i+1,j], h_map[i+1,j+1], h_map[i,j+1]
            avg_h = (h00 + h10 + h11 + h01) / 4.0
            avg_m = (m_map[i,j] + m_map[i+1,j] + m_map[i+1,j+1] + m_map[i,j+1]) / 4.0
            avg_temp = (temp_map[i,j] + temp_map[i+1,j] + temp_map[i+1,j+1] + temp_map[i,j+1]) / 4.0
            avg_rareza = (rareza_map[i,j] + rareza_map[i+1,j] + rareza_map[i+1,j+1] + rareza_map[i,j+1]) / 4.0
            es_cueva = bool(c_map[i,j])
            color, _, _, _, _, _, _ = biomes.get_biome_color_and_features(avg_h, avg_m, es_cueva, avg_temp, avg_rareza)
            avg_water = (float(water_mask[i,j]) + float(water_mask[i+1,j]) + float(water_mask[i+1,j+1]) + float(water_mask[i,j+1])) / 4.0
            avg_shore = (float(shore_mask[i,j]) + float(shore_mask[i+1,j]) + float(shore_mask[i+1,j+1]) + float(shore_mask[i,j+1])) / 4.0
            if avg_water >= 0.25:
                color = biomes._lerp_color(color, [0.18, 0.34, 0.26], 0.10)
            elif avg_shore >= 0.16:
                color = biomes._lerp_color(color, [0.24, 0.50, 0.20], 0.32)
            glColor3fv(color)
            glVertex3f(x1,h00,z1); glVertex3f(x2,h10,z1); glVertex3f(x2,h11,z2); glVertex3f(x1,h01,z2)
    glEnd()

    # Agua simple del LOD, con pocos quads y sin decoracion.
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glBegin(GL_QUADS)
    for i in range(subdivisions):
        for j in range(subdivisions):
            avg_water = (float(water_mask[i,j]) + float(water_mask[i+1,j]) + float(water_mask[i+1,j+1]) + float(water_mask[i,j+1])) / 4.0
            if avg_water < 0.25:
                continue
            x1 = world_start_x + i * step
            x2 = world_start_x + (i + 1) * step
            z1 = world_start_z + j * step
            z2 = world_start_z + (j + 1) * step
            h00, h10, h11, h01 = h_map[i,j], h_map[i+1,j], h_map[i+1,j+1], h_map[i,j+1]
            avg_h = float((h00 + h10 + h11 + h01) / 4.0)
            avg_wlevel = float((water_level_map[i,j] + water_level_map[i+1,j] + water_level_map[i+1,j+1] + water_level_map[i,j+1]) / 4.0)
            wy = _water_surface_y(avg_wlevel, avg_h)
            overlap = step * 0.018
            glColor4f(0.14, 0.39, 0.56, 0.34)
            glVertex3f(x1-overlap, wy, z1-overlap); glVertex3f(x2+overlap, wy, z1-overlap); glVertex3f(x2+overlap, wy, z2+overlap); glVertex3f(x1-overlap, wy, z2+overlap)
            if (i + j) % 4 == 0:
                glColor4f(0.80, 0.93, 1.00, 0.045)
                cx2 = (x1+x2)*0.5; cz2=(z1+z2)*0.5; ww=(x2-x1)*0.25; ll=(z2-z1)*0.55
                glVertex3f(cx2-ww, wy+0.012, cz2-ll); glVertex3f(cx2+ww, wy+0.012, cz2-ll*0.5); glVertex3f(cx2+ww*0.7, wy+0.012, cz2+ll); glVertex3f(cx2-ww*0.7, wy+0.012, cz2+ll*0.5)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEndList()
    return list_id

def draw_compiled_chunk(list_id):
    glCallList(list_id)


def is_chunk_visible(cx, cz, px, pz, lx, lz, size=100, max_distance=230.0, back_margin=0.28):
    """Culling barato por distancia + cono horizontal de cámara.

    No es oclusion real todavía, pero evita dibujar chunks que quedan claramente
    detras de la cámara o demasiado lejos. Mantiene siempre un radio cercano
    para que al girar no aparezcan huecos.
    """
    center_x = cx * size + size / 2
    center_z = cz * size + size / 2
    vx = center_x - px
    vz = center_z - pz
    dist_sq = vx * vx + vz * vz

    near_keep = size * 2.05
    if dist_sq <= near_keep * near_keep:
        return True

    if dist_sq > max_distance * max_distance:
        return False

    fx = lx - px
    fz = lz - pz
    flen = (fx * fx + fz * fz) ** 0.5
    dlen = dist_sq ** 0.5
    if flen <= 0.0001 or dlen <= 0.0001:
        return True

    dot = (vx * fx + vz * fz) / (dlen * flen)
    # back_margin negativo permite un poco de visión lateral para evitar popping.
    return dot >= -float(back_margin)


def is_point_visible_for_render(x, z, px, pz, lx, lz, near_keep=18.0, max_distance=125.0, back_margin=0.18):
    """Culling barato para enemigos, NPCs y restos.

    Sirve como paso previo a una futura render queue/Vulkan: primero decidimos
    QUE se va a dibujar, luego el renderer lo ejecuta.
    """
    vx = x - px
    vz = z - pz
    dist_sq = vx * vx + vz * vz
    if dist_sq <= near_keep * near_keep:
        return True
    if dist_sq > max_distance * max_distance:
        return False
    fx = lx - px
    fz = lz - pz
    flen = (fx * fx + fz * fz) ** 0.5
    dlen = dist_sq ** 0.5
    if flen <= 0.0001 or dlen <= 0.0001:
        return True
    dot = (vx * fx + vz * fz) / (dlen * flen)
    return dot >= -float(back_margin)


def clean_cache_for_chunk(cx, cz):
    global _height_cache
    if (cx, cz) in _height_cache:
        del _height_cache[(cx, cz)]
