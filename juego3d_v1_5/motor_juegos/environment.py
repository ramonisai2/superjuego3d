try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    # Permite usar benchmarks de generacion de terreno sin cargar OpenGL.
    pass
import numpy as np
import math
from . import biomes
from .env_config import read_env_float, read_env_text
from .atmospheric_sky import draw_atmospheric_skybox
from .terrain_noise_experiment import calculate_fast_noise_terrain_properties, calculate_fast_noise_water_properties
from .chunk_mesh_builder import build_chunk_mesh_data
from .environment_legacy_draw import draw_decorations, draw_optimized_rock
from .materials import get_material
from .gpu_resources import NeutralBufferDesc, NeutralMeshHandle

_height_cache = {}

from .world_detail import (
    DECO_DENSITY,
    GRASS_DENSITY,
    OASIS_TREE_DENSITY,
    PERF_AGGRESSIVE,
    ROCK_DENSITY,
    WATER_SURFACE_MAX_ABOVE_GROUND,
    WORLD_DETAIL_PROFILES,
    _world_detail_density,
    get_world_detail_density_status,
)


def _water_surface_y(raw_level, ground_y):
    """
    Mantiene escorrentia pegada al terreno, pero deja que lagos profundos lean
    como una superficie mas plana.

    Antes el fondo visual del lago podia bajarse mas que el nivel procedural del
    agua, dejando placas flotando. Despues lo pegamos demasiado al suelo y el
    lago parecia agua bajando por una ladera. Esta version distingue por
    profundidad: charcos/rios de meseta siguen al terreno; lagos recuperan plano.
    """
    try:
        raw = float(raw_level)
        ground = float(ground_y)
    except (TypeError, ValueError):
        return float(raw_level)
    if not np.isfinite(raw) or not np.isfinite(ground):
        return raw
    shallow_above = read_env_float(
        "JUEGO_WATER_SURFACE_MAX_ABOVE_GROUND",
        WATER_SURFACE_MAX_ABOVE_GROUND,
        -0.04,
        0.10,
    )
    lake_above = read_env_float("JUEGO_WATER_LAKE_MAX_ABOVE_GROUND", 1.10, 0.10, 3.0)
    flat_start = read_env_float("JUEGO_WATER_LAKE_FLAT_DEPTH", 0.72, 0.12, 3.0)
    depth_hint = max(0.0, raw - ground)
    lake_t = max(0.0, min(1.0, (depth_hint - flat_start) / max(0.10, flat_start)))
    allowed_above = shallow_above * (1.0 - lake_t) + min(lake_above, max(shallow_above, depth_hint)) * lake_t
    return min(raw + 0.004, ground + allowed_above)

def _terrain_mode():
    return read_env_text("JUEGO_TERRAIN_MODE", "current", lower=True) or "current"


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
    lake_impostor_cells = []
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
                # Solape minimo: demasiado solape oscurece la cuadricula del agua translucida.
                overlap = step * read_env_float("JUEGO_WATER_CELL_OVERLAP", 0.002, 0.0, 0.020)
                water_data.append((wcol,
                                   (x1 - overlap, wy, z1 - overlap),
                                   (x2 + overlap, wy, z1 - overlap),
                                   (x2 + overlap, wy, z2 + overlap),
                                   (x1 - overlap, wy, z2 + overlap)))
                if avg_depth >= read_env_float("JUEGO_WATER_IMPOSTOR_MIN_DEPTH", 0.42, 0.05, 3.0):
                    lake_impostor_cells.append((x1, x2, z1, z2, wy, wcol))

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
                if local_deco_type in ("arbol_bosque", "arbol_pantano", "arbol_roble", "arbol_pino", "arbol_abedul", "arbol_sauce", "arbol_cipres") and es_orilla and np.random.rand() < 0.25:
                    deco_variant = "alto"
                deco_data.append((local_deco_type, rx, suelo, rz, deco_variant))

            # Sotobosque por bioma: piezas bajas, baratas y dependientes del terreno.
            if has_grass and (not es_agua) and (not es_cueva):
                understory_type = None
                understory_chance = 0.0
                if es_orilla or (avg_m > 0.74 and avg_h < 8.5):
                    understory_type = "junco"
                    understory_chance = 0.030 + avg_m * 0.030
                elif avg_m > 0.74 and avg_temp < 0.62 and avg_rareza > 0.10:
                    understory_type = "hongo"
                    understory_chance = 0.012 + avg_m * 0.014
                elif avg_m > 0.70 and avg_temp < 0.72:
                    understory_type = "helecho"
                    understory_chance = 0.026 + avg_m * 0.024
                elif avg_m > 0.64 and avg_temp < 0.58 and avg_rareza < -0.18:
                    understory_type = "maleza_oscura"
                    understory_chance = 0.024 + min(0.025, -avg_rareza * 0.020)
                elif 0.48 < avg_m < 0.78 and avg_temp > 0.28 and avg_rareza > 0.24:
                    understory_type = "arbusto_verde"
                    understory_chance = 0.010 + avg_m * 0.012
                elif avg_m < 0.30 and avg_temp > 0.46 and avg_h < 13.0:
                    understory_type = "arbusto_seco"
                    understory_chance = 0.010 + (0.30 - avg_m) * 0.040
                elif 0.40 < avg_m < 0.72 and avg_temp < 0.66 and avg_rareza < 0.18:
                    understory_type = "flor_azul"
                    understory_chance = 0.018 + avg_m * 0.014
                elif avg_m > 0.34:
                    understory_type = "hierba_alta"
                    understory_chance = 0.018 + avg_m * 0.012
                if understory_type and np.random.rand() < (understory_chance * detail_density["deco"]):
                    rx = np.random.uniform(x1,x2)
                    rz = np.random.uniform(z1,z2)
                    tx = (rx-x1)/step
                    tz = (rz-z1)/step
                    h0 = h00*(1-tx)+h10*tx
                    h1 = h01*(1-tx)+h11*tx
                    suelo = h0*(1-tz)+h1*tz
                    deco_data.append((understory_type, rx, suelo, rz, "normal"))

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
                    tree_type = "arbol_sauce" if avg_m > 0.62 else "arbol_roble"
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

    _append_lake_impostor(water_data, lake_impostor_cells, step)
    return cx, cz, quads_data, grass_data, rock_data, deco_data, water_data, h_map


def _append_lake_impostor(water_data, cells, step):
    if not cells:
        return
    min_cells = int(read_env_float("JUEGO_WATER_IMPOSTOR_MIN_CELLS", 10.0, 3.0, 120.0))
    if len(cells) < min_cells:
        return
    x0 = min(item[0] for item in cells)
    x1 = max(item[1] for item in cells)
    z0 = min(item[2] for item in cells)
    z1 = max(item[3] for item in cells)
    bbox_area = max(0.001, (x1 - x0) * (z1 - z0))
    fill = (len(cells) * float(step) * float(step)) / bbox_area
    min_fill = read_env_float("JUEGO_WATER_IMPOSTOR_MIN_FILL", 0.24, 0.05, 0.95)
    if fill < min_fill:
        return
    avg_y = sum(item[4] for item in cells) / len(cells)
    avg_col = [sum(item[5][idx] for item in cells) / len(cells) for idx in range(3)]
    inset = float(step) * read_env_float("JUEGO_WATER_IMPOSTOR_INSET", 0.35, -1.0, 2.0)
    water_data.append((
        "lake_impostor",
        avg_col,
        (x0 + inset, avg_y + 0.018, z0 + inset),
        (x1 - inset, avg_y + 0.018, z0 + inset),
        (x1 - inset, avg_y + 0.018, z1 - inset),
        (x0 + inset, avg_y + 0.018, z1 - inset),
    ))

def terrain_worker_process(pipe, size, sub, seed):
    while True:
        try:
            msg = pipe.recv()
            if msg=="STOP": break
            pipe.send(calculate_chunk_data_background(msg[0], msg[1], size, sub, seed))
        except: break


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
        draw_optimized_rock(*r)
    for d in mesh_data.legacy_deco:
        draw_decorations(*d)

    for batch in ordered_batches:
        if getattr(batch, "blend", False) or getattr(batch, "material", "") in ("water", "shadow"):
            _draw_mesh_batch(batch)

    glEndList()
    return list_id


def build_gpu_list_from_data(quads, grass, rocks, deco, water=None):
    # Compatibilidad con codigo viejo: convierte a MeshData y luego sube a OpenGL.
    mesh = build_chunk_mesh_data(0, 0, quads, grass, rocks, deco, water or [], size=100, lod="legacy")
    return build_gpu_list_from_mesh_data(mesh)


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
        plain_strength = float(biomes._playable_plain_field(gx1, gz1, seed)[0, 0])
    except Exception:
        lake_basin, low_macro, high_macro, mesa_strength, plain_strength = 0.0, 0.0, 0.0, 0.0, 0.0

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
    elif plain_strength > 0.45:
        feature = "Llanura jugable"
        layer = "Capa 2 media/templada"
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
        "plain_strength": plain_strength,
        "rareza": rareza,
    }



def draw_procedural_skybox(size=300.0):
    """Fachada estable para el backend OpenGL actual."""
    draw_atmospheric_skybox(size=float(size))



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
    terrain_quads = int(subdivisions) * int(subdivisions)
    water_quads = 0
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
            water_quads += 1
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
                water_quads += 1
                glColor4f(0.80, 0.93, 1.00, 0.045)
                cx2 = (x1+x2)*0.5; cz2=(z1+z2)*0.5; ww=(x2-x1)*0.25; ll=(z2-z1)*0.55
                glVertex3f(cx2-ww, wy+0.012, cz2-ll); glVertex3f(cx2+ww, wy+0.012, cz2-ll*0.5); glVertex3f(cx2+ww*0.7, wy+0.012, cz2+ll); glVertex3f(cx2-ww*0.7, wy+0.012, cz2+ll*0.5)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEndList()
    total_quads = terrain_quads + water_quads
    vertex_count = total_quads * 4
    index_count = total_quads * 6
    byte_size = vertex_count * (3 * 4 + 4 * 4) + index_count * 4
    return NeutralMeshHandle(
        backend="opengl",
        backend_handle=list_id,
        desc=NeutralBufferDesc(
            kind="simple_lod_chunk",
            vertex_count=vertex_count,
            index_count=index_count,
            byte_size=byte_size,
            material_batches=2 if water_quads else 1,
            transparent=bool(water_quads),
        ),
        label="simple_lod_chunk",
        coord=(int(cx), int(cz)),
        lod="lod",
        metadata={
            "terrain_quads": terrain_quads,
            "water_quads": water_quads,
            "subdivisions": int(subdivisions),
        },
    )

def draw_compiled_chunk(list_id):
    glCallList(list_id)


def is_chunk_visible(cx, cz, px, pz, lx, lz, size=100, max_distance=230.0, back_margin=0.28, near_keep=None):
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

    keep_radius = float(near_keep) if near_keep is not None else size * 2.05
    if dist_sq <= keep_radius * keep_radius:
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

