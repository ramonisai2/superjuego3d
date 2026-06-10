from motor_juegos import GameEngine, AudioManager, r3d, r2d, env
from motor_juegos.render_backend import create_render_backend
from motor_juegos.world_chunk_stream_bridge import build_world_chunk_stream_plan
from motor_juegos.stream_bridge_budget import get_stream_bridge_budget
import os
from motor_juegos.render_api import FogConfig
from motor_juegos.frame_graph import RenderFrameGraph
from motor_juegos.runtime_perf import perf_tracker
import pygame
import random
import math
import multiprocessing
import time
from motor_juegos.render_mode_status import print_render_mode_banner, get_render_mode_status
from motor_juegos.version_info import full_update_name, UPDATE_CODENAME, UPDATE_SUBTITLE
print_render_mode_banner("main.py startup")

from game.player import Player
from game.enemy import Enemy, SlimeRemnant
from game.npc_manager import NPC
from game.combat import attack_enemy
from game.ui import draw_ui, draw_world_context, draw_npc_label, draw_npc_prompt, draw_npc_description, draw_npc_dialog, draw_npc_world_label, draw_z_target_ui, draw_z_target_marker, draw_npc_ai_telemetry, draw_pickup_notices, draw_fps_counter, draw_adaptive_quality
from game.save_system import save_game, load_game, load_game_data, apply_save_to_player, has_save, get_save_summary
from game.admin_hub import AdminHub
from game.debug_log import log_event, log_exception, log_throttled
from game.voxel_models import render_player_avatar, render_first_person_weapon, draw_box

# ------------------------------
# Constantes
# ------------------------------
ANCHO = 1280
ALTO = 720
SEMILLA_MUNDO = random.randint(1, 1000000)  # se reemplaza desde el menu inicial si se continua o se elige nueva semilla
GRAPHICS_PRESET = os.environ.get("JUEGO_GRAPHICS_PRESET", "balanced").strip().lower() or "balanced"
GRAPHICS_PRESETS = {
    "low": {
        "subdivisiones": 40,
        "radio_vision": 2,
        "radio_detalle": 1,
        "subdivisiones_lod": 8,
        "lods_por_tanda": 1,
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
SUBDIVISIONES = 48
RADIO_VISION = 2                # chunks mas pequeños: mas anillo simple, cada pieza pesa menos
RADIO_DETALLE = 1               # menos agresivo: detalle en el chunk actual + 8 adyacentes
SUBDIVISIONES_LOD = 10          # LOD simple barato, un poco menos tosco
MAX_COLA_PETICIONES = 3         # cola moderada: prepara chunks cercanos sin saturar tanto
CHUNKS_COMPILAR_POR_FRAME = 1   # optimizacion G: compila 1 por frame para evitar picos
LODS_CREAR_POR_TANDA = int(os.environ.get("JUEGO_LOD_CREAR_POR_TANDA", "2") or "2")
ENABLE_STREAM_BRIDGE_SAFE = os.environ.get("JUEGO_STREAM_BRIDGE_SAFE", "0").strip() == "1"
DEBUG_RENDER_ALL_CHUNKS = os.environ.get("JUEGO_DEBUG_RENDER_ALL_CHUNKS", "0").strip() == "1"
DEBUG_RENDER_ALL_ENTITIES = os.environ.get("JUEGO_DEBUG_RENDER_ALL_ENTITIES", "0").strip() == "1"
ENTITY_RENDER_DISTANCE = 125.0    # no dibujar entidades claramente lejanas
ENTITY_LABEL_DISTANCE = 48.0      # etiquetas solo cerca
ENTITY_FULL_DETAIL_DISTANCE = 34.0
ENTITY_MID_DETAIL_DISTANCE = 72.0
REMNANT_RENDER_DISTANCE = 58.0
ADAPTIVE_QUALITY_ENABLED = os.environ.get("JUEGO_ADAPTIVE_QUALITY", "1").strip() != "0"
ADAPTIVE_FPS_LOW = float(os.environ.get("JUEGO_ADAPTIVE_FPS_LOW", "28") or "28")
ADAPTIVE_FPS_HIGH = float(os.environ.get("JUEGO_ADAPTIVE_FPS_HIGH", "48") or "48")
ADAPTIVE_CHUNK_RENDER_ENABLED = os.environ.get("JUEGO_ADAPTIVE_CHUNKS", "1").strip() != "0"
ADAPTIVE_STREAMING_ENABLED = os.environ.get("JUEGO_ADAPTIVE_STREAMING", "1").strip() != "0"
PRESET_SAMPLE_LOG_ENABLED = os.environ.get("JUEGO_PRESET_SAMPLE_LOG", "1").strip() != "0"
PRESET_SAMPLE_LOG_INTERVAL = float(os.environ.get("JUEGO_PRESET_SAMPLE_LOG_INTERVAL", "3.0") or "3.0")
PRESET_SAMPLE_SESSION = os.environ.get("JUEGO_PRESET_SAMPLE_SESSION", "").strip() or time.strftime("%Y%m%d_%H%M%S")
SUBDIVISIONES = int(os.environ.get("JUEGO_SUBDIVISIONES", GRAPHICS_SETTINGS["subdivisiones"]))
RADIO_VISION = int(os.environ.get("JUEGO_RADIO_VISION", GRAPHICS_SETTINGS["radio_vision"]))
RADIO_DETALLE = int(os.environ.get("JUEGO_RADIO_DETALLE", GRAPHICS_SETTINGS["radio_detalle"]))
SUBDIVISIONES_LOD = int(os.environ.get("JUEGO_SUBDIVISIONES_LOD", GRAPHICS_SETTINGS["subdivisiones_lod"]))
LODS_CREAR_POR_TANDA = int(os.environ.get("JUEGO_LOD_CREAR_POR_TANDA", str(GRAPHICS_SETTINGS["lods_por_tanda"])) or str(GRAPHICS_SETTINGS["lods_por_tanda"]))
ENTITY_RENDER_DISTANCE = float(os.environ.get("JUEGO_ENTITY_RENDER_DISTANCE", GRAPHICS_SETTINGS["entity_render_distance"]))
ENTITY_LABEL_DISTANCE = float(os.environ.get("JUEGO_ENTITY_LABEL_DISTANCE", GRAPHICS_SETTINGS["entity_label_distance"]))
ENTITY_FULL_DETAIL_DISTANCE = float(os.environ.get("JUEGO_ENTITY_FULL_DETAIL_DISTANCE", GRAPHICS_SETTINGS["entity_full_detail"]))
ENTITY_MID_DETAIL_DISTANCE = float(os.environ.get("JUEGO_ENTITY_MID_DETAIL_DISTANCE", GRAPHICS_SETTINGS["entity_mid_detail"]))
REMNANT_RENDER_DISTANCE = float(os.environ.get("JUEGO_REMNANT_RENDER_DISTANCE", GRAPHICS_SETTINGS["remnant_render_distance"]))
WATER_QUERY_GRID = 0.75           # cache barato para consultas repetidas de agua/altura
TOTAL_HEIGHT_QUERY_GRID = 0.25    # cache fino por frame para movimiento y colision
RESOURCE_CELL_SIZE = 4.0          # indice barato para no recorrer chunks completos al recoger
ROCK_COLLISION_CELL_SIZE = 4.0    # indice barato para rocas que elevan el suelo
WORLD_CONTEXT_INTERVAL = 0.18     # HUD/nado no necesita recalcularse cada frame
WORLD_CONTEXT_MOVE_STEP = 1.25
NPC_FULL_AI_DISTANCE = 36.0       # NPCs cercanos reaccionan cada frame
NPC_FAR_AI_INTERVAL = 0.35        # NPCs lejanos piensan por tandas
ENEMY_FULL_AI_DISTANCE = 42.0     # enemigos cercanos siguen suaves y peligrosos
ENEMY_FAR_AI_INTERVAL = 0.25      # enemigos lejanos no necesitan update completo cada frame
SPAWN_CHUNK_X = 0
SPAWN_CHUNK_Z = 0
SPAWN_CENTER_X = SPAWN_CHUNK_X * CHUNK_SIZE + CHUNK_SIZE * 0.5
SPAWN_CENTER_Z = SPAWN_CHUNK_Z * CHUNK_SIZE + CHUNK_SIZE * 0.5

# ------------------------------
# Variables globales
# ------------------------------
engine = None
render_backend = None
render_graph = RenderFrameGraph()
audio = None
player = None
enemies = []
slime_remnants = []
stone_projectiles = []
npcs = []
npc_dialog = ""
npc_prompt = ""
npc_name_label = ""
npc_description = ""
npc_label_screen = None
z_target_screen = None
last_attack_time = 0.0
last_interact_time = 0.0
global_rocks = {}
global_grass = {}
global_trees = {}
global_resource_cells = {}
global_rock_collision_cells = {}
resource_pickup_cooldowns = {}
total_height_query_cache = {}
total_height_query_frame = 0
pipe_juego = None
worker_process = None
mundo_chunks = {}
mundo_chunks_simple = {}
cola_de_peticiones = []
cola_lod_peticiones = []
chunks_pendientes = {}
water_surface_cache = {}
chunk_generándose_ahora = False
tiempo_log = 0.0
tiempo_chunks = 0.0
render_stats = {
    "chunks_detalle": 0,
    "chunks_lod": 0,
    "chunks_ocultos": 0,
    "entidades_render": 0,
    "entidades_ocultas": 0,
    "backend": "opengl",
}
adaptive_quality = {
    "enabled": ADAPTIVE_QUALITY_ENABLED,
    "scale": 1.0,
    "state": "OK",
    "fps_avg": 0.0,
    "low_time": 0.0,
    "high_time": 0.0,
}
adaptive_streaming = {
    "enabled": ADAPTIVE_STREAMING_ENABLED,
    "interval": 0.05,
    "lod_limit": int(LODS_CREAR_POR_TANDA),
    "forced": 0,
}
stream_bridge_stats = {
    "enabled": int(ENABLE_STREAM_BRIDGE_SAFE),
    "preset": os.environ.get("JUEGO_STREAM_BRIDGE_PRESET", "safe").strip() or "safe",
    "detail_radius": RADIO_DETALLE,
    "lod_radius": RADIO_VISION,
    "max_requests": MAX_COLA_PETICIONES,
    "calls": 0,
    "last_center_x": 0,
    "last_center_z": 0,
    "lod_queued_total": 0,
    "lod_created_total": 0,
    "detail_requested_total": 0,
    "detail_released_total": 0,
    "lod_released_total": 0,
    "requests_cancelled_total": 0,
    "queue_len": 0,
    "lod_queue_len": 0,
    "pending_len": 0,
    "detail_loaded": 0,
    "lod_loaded": 0,
}

current_fov = 45.0
target_fov = 45.0
last_attack_time = 0.0
attack_cooldown = 0.5
admin_hub = None
z_target = None
z_target_type = None
z_target_q_down = False
z_target_cycle_down = False

# ------------------------------
# Funciones auxiliares
# ------------------------------


def draw_simple_screen(engine, titulo, lineas=None, subtitulo=None):
    """Pantalla 2D simple para menú/carga usando el contexto OpenGL ya abierto."""
    if lineas is None:
        lineas = []
    if render_backend:
        render_backend.clear()
    r2d.begin_2d(ANCHO, ALTO)
    r2d.draw_rect_2d(0, 0, ANCHO, ALTO, (0.04, 0.07, 0.09))
    r2d.draw_rect_2d(160, 115, ANCHO - 320, ALTO - 230, (0.02, 0.025, 0.03))
    r2d.draw_text_2d(titulo, 205, 155, (240, 240, 220))
    y = 210
    if subtitulo:
        r2d.draw_text_2d(subtitulo, 205, y, (170, 220, 210))
        y += 48
    for linea in lineas:
        r2d.draw_text_2d(linea, 205, y, (220, 230, 220))
        y += 34
    r2d.end_2d()
    pygame.display.flip()


def show_loading_screen(mensaje="Cargando mundo..."):
    draw_simple_screen(engine, "JUEGO 1.6", [mensaje, "Generando chunks iniciales y preparando entidades...", f"Actualizacion: {full_update_name()}"], UPDATE_SUBTITLE)
    pygame.event.pump()


def show_start_menu(engine):
    """Menu inicial: continuar mundo guardado o empezar con otra semilla."""
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    typing_seed = False
    seed_text = ""
    selected_seed = None
    save_summary = get_save_summary()

    while True:
        if selected_seed is not None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            pygame.mouse.get_rel()
            return {"mode": "new", "seed": selected_seed, "save_data": None}

        lineas = []
        lineas.append(get_render_mode_status().hud_label())
        lineas.append("")
        lineas.append(f"Actualizacion: {full_update_name()}")
        lineas.append(f"Nombre clave: {UPDATE_CODENAME}")
        lineas.append(UPDATE_SUBTITLE)
        lineas.append("")
        if save_summary:
            lineas.append(f"C - Continuar mundo guardado | Semilla {save_summary['seed']} | X {save_summary['x']:.1f} Z {save_summary['z']:.1f}")
            lineas.append(f"    Guardado: {save_summary.get('saved_at', 'desconocido')}")
        else:
            lineas.append("C - Continuar mundo guardado: no hay partida todavia")
        lineas.append("N - Nueva partida con semilla aleatoria")
        lineas.append("S - Escribir otra semilla manual")
        lineas.append("ESC - Salir")
        if typing_seed:
            lineas.append("")
            lineas.append("Escribe una semilla numerica y pulsa ENTER:")
            lineas.append(seed_text if seed_text else "_")
        else:
            lineas.append("")
            lineas.append("Controles dentro del juego: F5 guarda, F9 recarga, V camara, Q fijar objetivo")

        draw_simple_screen(engine, "Menu de Mundo", lineas, f"{full_update_name()} | Continuar o empezar")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"mode": "quit", "seed": None, "save_data": None}
            if event.type == pygame.KEYDOWN:
                if typing_seed:
                    if event.key == pygame.K_RETURN:
                        if seed_text.strip():
                            try:
                                selected_seed = int(seed_text.strip())
                            except ValueError:
                                selected_seed = abs(hash(seed_text.strip())) % 1000000
                        typing_seed = False
                    elif event.key == pygame.K_ESCAPE:
                        typing_seed = False
                        seed_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        seed_text = seed_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and (ch.isdigit() or (ch == '-' and not seed_text)):
                            seed_text += ch
                    continue

                if event.key == pygame.K_ESCAPE:
                    return {"mode": "quit", "seed": None, "save_data": None}
                if event.key == pygame.K_c and save_summary:
                    data = load_game_data()
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    pygame.mouse.get_rel()
                    return {"mode": "continue", "seed": int(data.get("seed", 1)), "save_data": data}
                if event.key == pygame.K_n:
                    selected_seed = random.randint(1, 1000000)
                if event.key == pygame.K_s:
                    typing_seed = True
                    seed_text = ""
        pygame.time.wait(16)

def player_chunk_coord(pos):
    return int(math.floor(pos / float(CHUNK_SIZE)))

def get_terrain_only(x, z):
    try:
        return env.get_cached_height_at(x, z, size=CHUNK_SIZE, subdivisions=SUBDIVISIONES, seed=SEMILLA_MUNDO)
    except:
        return env.get_terrain_height_at(x, z, seed=SEMILLA_MUNDO)

def get_water_surface_cached(x, z):
    """Consulta estable de agua con cache espacial para movimiento/IA."""
    global water_surface_cache
    grid = max(0.25, float(WATER_QUERY_GRID))
    key = (
        int(round(float(x) / grid)),
        int(round(float(z) / grid)),
        int(SEMILLA_MUNDO),
        int(CHUNK_SIZE),
        int(SUBDIVISIONES),
    )
    cached = water_surface_cache.get(key)
    if cached is not None:
        return cached
    value = env.get_water_surface_at(
        x,
        z,
        seed=SEMILLA_MUNDO,
        size=CHUNK_SIZE,
        subdivisions=SUBDIVISIONES,
    )
    if len(water_surface_cache) > 4096:
        water_surface_cache.clear()
    water_surface_cache[key] = value
    return value

def clear_total_height_query_cache():
    global total_height_query_cache
    total_height_query_cache.clear()

def begin_total_height_query_frame():
    global total_height_query_frame
    total_height_query_frame += 1
    clear_total_height_query_cache()

def _total_height_cache_key(x, z):
    grid = max(0.05, float(TOTAL_HEIGHT_QUERY_GRID))
    return (
        int(round(float(x) / grid)),
        int(round(float(z) / grid)),
        int(total_height_query_frame),
    )

def get_total_height(x, z):
    key = _total_height_cache_key(x, z)
    cached = total_height_query_cache.get(key)
    if cached is not None:
        return cached

    h = get_terrain_only(x, z)
    if not math.isfinite(h):
        log_event("HEIGHT_NOT_FINITE", x=x, z=z, h=h)
    # Stage 28: para esta build de prueba, la superficie de lago actua como suelo
    # si queda por encima del terreno, evitando que el jugador/NPCs caminen bajo el agua.
    try:
        hay_agua, nivel_agua = get_water_surface_cached(x, z)
        if hay_agua and nivel_agua > h:
            log_throttled("HEIGHT_WATER_SURFACE_USED", 2.0, x=x, z=z, terrain_h=h, water_level=nivel_agua)
            h = nivel_agua + 0.03
    except Exception as exc:
        log_exception("HEIGHT_WATER_CHECK_ERROR", exc)
    for rock in _nearby_rock_colliders(x, z):
        rx, ry, rz, sx, sy, sz = rock[:6]
        # Stage 30 Fix N: no usar objetos delgados/vegetacion como collider vertical.
        # Esto permite atravesar arboles/arbustos si entran por error a la lista de rocas.
        is_tall_skinny = sy > 1.4 and max(sx, sz) < 1.15
        is_tiny_bush = sy < 0.45 and max(sx, sz) < 0.75
        if is_tall_skinny or is_tiny_bush:
            continue
        if abs(x - rx) <= sx/2 and abs(z - rz) <= sz/2:
            h = max(h, ry + sy)
    if len(total_height_query_cache) > 512:
        total_height_query_cache.clear()
    total_height_query_cache[key] = h
    return h


def is_water_position(x, z):
    """True si el punto cae dentro de agua visible; se usa para evitar spawns terrestres en lagos."""
    try:
        hay_agua, _ = get_water_surface_cached(x, z)
        return bool(hay_agua)
    except Exception:
        return False


def update_player_world_context(dt):
    """Actualiza HUD de zona y modo nado/flotacion."""
    last_x = getattr(update_player_world_context, "last_x", None)
    last_z = getattr(update_player_world_context, "last_z", None)
    elapsed = getattr(update_player_world_context, "elapsed", WORLD_CONTEXT_INTERVAL)
    elapsed += float(dt)
    moved_far = (
        last_x is None
        or last_z is None
        or ((player.pos_x - last_x) ** 2 + (player.pos_z - last_z) ** 2) >= WORLD_CONTEXT_MOVE_STEP ** 2
    )
    ctx = getattr(player, "world_context", None)
    if ctx is None or elapsed >= WORLD_CONTEXT_INTERVAL or moved_far:
        try:
            ctx = env.get_world_context_at(
                player.pos_x,
                player.pos_z,
                seed=SEMILLA_MUNDO,
                size=CHUNK_SIZE,
                subdivisions=SUBDIVISIONES,
            )
        except Exception as exc:
            log_exception("WORLD_CONTEXT_ERROR", exc)
            ctx = {"biome": "Desconocido", "feature": "Sin datos", "layer": "?", "in_water": False}
        update_player_world_context.last_x = player.pos_x
        update_player_world_context.last_z = player.pos_z
        elapsed = 0.0
    update_player_world_context.elapsed = elapsed

    player.world_context = ctx
    in_water = bool(ctx.get("in_water", False))
    player.is_swimming = in_water

    if in_water:
        # Flotacion: el jugador no se hunde hasta el fondo, queda a nivel de superficie
        # con un cabeceo suave. Esto tambien sirve para depurar visualmente los lagos.
        phase = getattr(player, "swim_phase", 0.0) + dt * 3.2
        player.swim_phase = phase
        bob = math.sin(phase) * 0.08
        player.surface_offset = 0.82 + bob
        player.speed = min(player.speed, 3.2)
        player.velocity_y = 0.0
    else:
        player.surface_offset = player.player_height

def find_dry_spawn_position(base_x, base_z, min_radius, max_radius, attempts=40):
    """Busca una posición seca alrededor del jugador para NPCs/enemigos terrestres."""
    best = None
    for _ in range(attempts):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(min_radius, max_radius)
        x = base_x + math.cos(angle) * radius
        z = base_z + math.sin(angle) * radius
        if is_water_position(x, z):
            continue
        y = get_total_height(x, z)
        best = (x, y, z)
        break
    if best is None:
        # Si todo falla, usa una posición cercana pero seca alrededor del spawn.
        x = base_x + min_radius
        z = base_z
        y = get_total_height(x, z)
        best = (x, y, z)
    return best


def find_safe_player_position(base_x, base_z, attempts=72, reason="unknown"):
    """
    Busca una zona seca y estable cerca del punto pedido.
    FIX H agrega log detallado para encontrar el culpable del ciclo de reaparicion.
    """
    log_event("SAFE_SEARCH_START", reason=reason, base_x=base_x, base_z=base_z, attempts=attempts, seed=SEMILLA_MUNDO)
    try:
        base_water = is_water_position(base_x, base_z)
        base_y = get_total_height(base_x, base_z)
        log_event("SAFE_BASE_CHECK", x=base_x, z=base_z, water=base_water, y=base_y, finite=math.isfinite(base_y))
        if (not base_water) and math.isfinite(base_y) and -20.0 < base_y < 160.0:
            log_event("SAFE_BASE_ACCEPTED", x=base_x, y=base_y, z=base_z)
            return base_x, base_y, base_z
    except Exception as exc:
        log_exception("SAFE_BASE_ERROR", exc)

    checked = 0
    for radius in (3.0, 6.0, 10.0, 16.0, 24.0, 36.0, 55.0):
        for i in range(attempts):
            checked += 1
            angle = (i / float(attempts)) * math.pi * 2.0 + random.uniform(-0.03, 0.03)
            x = base_x + math.cos(angle) * radius
            z = base_z + math.sin(angle) * radius
            water = is_water_position(x, z)
            if water:
                if checked <= 8 or checked % 40 == 0:
                    log_event("SAFE_CANDIDATE_REJECT_WATER", radius=radius, x=x, z=z)
                continue
            y = get_total_height(x, z)
            if not math.isfinite(y) or y < -20.0 or y > 160.0:
                if checked <= 8 or checked % 40 == 0:
                    log_event("SAFE_CANDIDATE_REJECT_HEIGHT", radius=radius, x=x, z=z, y=y)
                continue
            log_event("SAFE_CANDIDATE_ACCEPTED", checked=checked, radius=radius, x=x, y=y, z=z)
            return x, y, z

    log_event("SAFE_SEARCH_FALLBACK_ORIGIN", checked=checked)
    return find_dry_spawn_position(0.0, 0.0, 0.0, 18.0, attempts=80)

def set_player_respawn_point(player, x=None, z=None):
    old_x = getattr(player, "respawn_x", None)
    old_z = getattr(player, "respawn_z", None)
    player.respawn_x = float(player.pos_x if x is None else x)
    player.respawn_z = float(player.pos_z if z is None else z)
    player._last_safe_x = player.respawn_x
    player._last_safe_z = player.respawn_z
    try:
        player._last_safe_y = get_total_height(player.respawn_x, player.respawn_z) + player.player_height
    except Exception:
        player._last_safe_y = getattr(player, "pos_y", 10.0)
    log_event("RESPAWN_POINT_SET", old_x=old_x, old_z=old_z, new_x=player.respawn_x, new_z=player.respawn_z, safe_y=player._last_safe_y)


def world_to_screen(x, y, z):
    return render_backend.project_to_screen(x, y, z) if render_backend else None


def _entity_distance_2d(a_x, a_z, b_x, b_z):
    return math.hypot(a_x - b_x, a_z - b_z)

def _entity_distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz


def update_adaptive_render_quality(dt):
    if not adaptive_quality.get("enabled", True) or not engine or not hasattr(engine, "clock"):
        adaptive_quality["state"] = "FIJO"
        adaptive_quality["scale"] = 1.0
        return
    fps = float(engine.clock.get_fps() or 0.0)
    if fps <= 1.0:
        return
    previous = float(adaptive_quality.get("fps_avg", 0.0) or 0.0)
    fps_avg = fps if previous <= 1.0 else previous + (fps - previous) * 0.08
    adaptive_quality["fps_avg"] = fps_avg
    scale = float(adaptive_quality.get("scale", 1.0) or 1.0)
    if fps_avg < ADAPTIVE_FPS_LOW:
        adaptive_quality["low_time"] = float(adaptive_quality.get("low_time", 0.0)) + dt
        adaptive_quality["high_time"] = 0.0
        if adaptive_quality["low_time"] >= 0.65:
            scale = max(0.58, scale - 0.08)
            adaptive_quality["low_time"] = 0.0
            adaptive_quality["state"] = "AHORRO"
    elif fps_avg > ADAPTIVE_FPS_HIGH:
        adaptive_quality["high_time"] = float(adaptive_quality.get("high_time", 0.0)) + dt
        adaptive_quality["low_time"] = 0.0
        if adaptive_quality["high_time"] >= 1.4:
            scale = min(1.0, scale + 0.04)
            adaptive_quality["high_time"] = 0.0
            adaptive_quality["state"] = "RECUP" if scale < 0.999 else "OK"
    else:
        adaptive_quality["low_time"] = 0.0
        adaptive_quality["high_time"] = 0.0
        adaptive_quality["state"] = "OK" if scale >= 0.999 else "AHORRO"
    adaptive_quality["scale"] = scale


def _adaptive_distance(base_distance, min_scale=0.55):
    if not adaptive_quality.get("enabled", True):
        return float(base_distance)
    scale = max(float(min_scale), min(1.0, float(adaptive_quality.get("scale", 1.0) or 1.0)))
    return float(base_distance) * scale


def _adaptive_chunk_render_distance():
    base_distance = CHUNK_SIZE * (RADIO_VISION + 1.8)
    if not ADAPTIVE_CHUNK_RENDER_ENABLED or not adaptive_quality.get("enabled", True):
        return float(base_distance)
    min_distance = CHUNK_SIZE * (RADIO_DETALLE + 1.8)
    scale = max(0.70, min(1.0, float(adaptive_quality.get("scale", 1.0) or 1.0)))
    return max(float(min_distance), float(base_distance) * scale)


def _adaptive_fog_range():
    chunk_distance = _adaptive_chunk_render_distance()
    fog_end = max(115.0, min(220.0, chunk_distance * 0.78))
    fog_start = max(42.0, fog_end * 0.34)
    return fog_start, fog_end


def _adaptive_stream_interval():
    if not ADAPTIVE_STREAMING_ENABLED or not adaptive_quality.get("enabled", True):
        return 0.05
    scale = max(0.58, min(1.0, float(adaptive_quality.get("scale", 1.0) or 1.0)))
    return 0.05 + (1.0 - scale) * 0.17


def _adaptive_lod_limit():
    base = max(1, int(LODS_CREAR_POR_TANDA))
    if not ADAPTIVE_STREAMING_ENABLED or not adaptive_quality.get("enabled", True):
        return base
    scale = max(0.58, min(1.0, float(adaptive_quality.get("scale", 1.0) or 1.0)))
    if scale < 0.76:
        return 1
    return base


def _entity_detail_level(px, pz, x, z, *, forced_full=False):
    if forced_full:
        return "full"
    dist2 = _entity_distance_sq_2d(px, pz, x, z)
    full_distance = _adaptive_distance(ENTITY_FULL_DETAIL_DISTANCE, 0.62)
    mid_distance = _adaptive_distance(ENTITY_MID_DETAIL_DISTANCE, 0.58)
    if dist2 <= full_distance * full_distance:
        return "full"
    if dist2 <= mid_distance * mid_distance:
        return "mid"
    return "far"

def _world_cell_coord(x, z, size):
    size = max(0.5, float(size))
    return (int(math.floor(float(x) / size)), int(math.floor(float(z) / size)))

def _nearby_cells(x, z, size, radius=1):
    cx, cz = _world_cell_coord(x, z, size)
    radius = max(0, int(radius))
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            yield (cx + dx, cz + dz)

def _resource_entry(kind, x, z, cx, cz, amount, radius):
    return (
        str(kind),
        float(x),
        float(z),
        int(cx),
        int(cz),
        int(amount),
        float(radius) * float(radius),
    )

def _index_resource_entry(kind, x, z, cx, cz, amount=1, radius=1.0):
    cell = _world_cell_coord(x, z, RESOURCE_CELL_SIZE)
    global_resource_cells.setdefault(cell, []).append(_resource_entry(kind, x, z, cx, cz, amount, radius))

def _resource_amount_for_world_detail(kind):
    """Compensa presets bajos: menos piezas visuales, recursos por nodo mas generosos."""
    try:
        status = env.get_world_detail_density_status()
    except Exception:
        return 1
    reference = {
        "fibra": ("grass", 0.35),
        "madera": ("deco", 0.35),
        "piedra": ("rock", 0.55),
    }.get(str(kind))
    if not reference:
        return 1
    density_key, balanced_value = reference
    current_value = max(0.05, float(status.get(density_key, balanced_value) or balanced_value))
    return max(1, min(4, int(math.ceil(float(balanced_value) / current_value))))

def _world_detail_debug_status():
    try:
        status = env.get_world_detail_density_status()
    except Exception:
        status = {"preset": "balanced"}
    status = dict(status)
    status["fibra_amount"] = _resource_amount_for_world_detail("fibra")
    status["madera_amount"] = _resource_amount_for_world_detail("madera")
    status["piedra_amount"] = _resource_amount_for_world_detail("piedra")
    return status

def _preset_sample_log_path():
    return os.path.join(os.getcwd(), "logs", "preset_runtime_samples.log")

def _append_preset_runtime_sample(fps):
    if not PRESET_SAMPLE_LOG_ENABLED:
        return
    try:
        os.makedirs(os.path.dirname(_preset_sample_log_path()), exist_ok=True)
        world_detail = _world_detail_debug_status()
        line = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"session={PRESET_SAMPLE_SESSION} "
            f"preset={os.environ.get('JUEGO_GRAPHICS_PRESET', 'balanced')} "
            f"world={world_detail.get('preset', 'balanced')} "
            f"fps={float(fps):.1f} "
            f"fpsAvg={float(adaptive_quality.get('fps_avg', 0.0) or 0.0):.1f} "
            f"auto={adaptive_quality.get('state', 'OK')} "
            f"scale={float(adaptive_quality.get('scale', 1.0) or 1.0):.2f} "
            f"chunksD={render_stats.get('chunks_detalle', 0)} "
            f"chunksLOD={render_stats.get('chunks_lod', 0)} "
            f"hiddenChunks={render_stats.get('chunks_ocultos', 0)} "
            f"ent={render_stats.get('entidades_render', 0)} "
            f"hiddenEnt={render_stats.get('entidades_ocultas', 0)} "
            f"verts={render_stats.get('mesh_vertices', 0)} "
            f"uploads={render_stats.get('uploads_frame', 0)} "
            f"streamMs={int(float(adaptive_streaming.get('interval', 0.05)) * 1000)} "
            f"densityG={float(world_detail.get('grass', 0.0) or 0.0):.2f} "
            f"densityD={float(world_detail.get('deco', 0.0) or 0.0):.2f} "
            f"densityR={float(world_detail.get('rock', 0.0) or 0.0):.2f} "
            f"resFMP={world_detail.get('fibra_amount', 1)}/{world_detail.get('madera_amount', 1)}/{world_detail.get('piedra_amount', 1)}"
        )
        with open(_preset_sample_log_path(), "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except Exception:
        pass

def _append_preset_session_start():
    if not PRESET_SAMPLE_LOG_ENABLED:
        return
    try:
        os.makedirs(os.path.dirname(_preset_sample_log_path()), exist_ok=True)
        with open(_preset_sample_log_path(), "a", encoding="utf-8") as handle:
            handle.write(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"session={PRESET_SAMPLE_SESSION} "
                f"event=session_start "
                f"preset={os.environ.get('JUEGO_GRAPHICS_PRESET', 'balanced')} "
                f"world={env.get_world_detail_density_status().get('preset', 'balanced')}\n"
            )
    except Exception:
        pass

def _clear_resource_index_for_chunk(coord, kinds=None):
    coord = (int(coord[0]), int(coord[1]))
    kind_set = {str(kind) for kind in kinds} if kinds else None
    for cell, entries in list(global_resource_cells.items()):
        kept = [
            entry for entry in entries
            if (entry[3], entry[4]) != coord or (kind_set is not None and entry[0] not in kind_set)
        ]
        if kept:
            global_resource_cells[cell] = kept
        else:
            global_resource_cells.pop(cell, None)

def _nearby_resource_entries(x, z):
    for cell in _nearby_cells(x, z, RESOURCE_CELL_SIZE, radius=1):
        for entry in global_resource_cells.get(cell, ()):
            yield entry

def _index_rock_collider(rock, cx, cz):
    try:
        rx, _, rz, sx, _, sz = rock[:6]
    except Exception:
        return
    half_x = max(0.1, float(sx) * 0.5)
    half_z = max(0.1, float(sz) * 0.5)
    min_cell = _world_cell_coord(float(rx) - half_x, float(rz) - half_z, ROCK_COLLISION_CELL_SIZE)
    max_cell = _world_cell_coord(float(rx) + half_x, float(rz) + half_z, ROCK_COLLISION_CELL_SIZE)
    for cell_x in range(min_cell[0], max_cell[0] + 1):
        for cell_z in range(min_cell[1], max_cell[1] + 1):
            global_rock_collision_cells.setdefault((cell_x, cell_z), []).append(rock)

def _clear_rock_collision_index_for_chunk(coord):
    coord = (int(coord[0]), int(coord[1]))
    for cell, rocks in list(global_rock_collision_cells.items()):
        kept = [rock for rock in rocks if len(rock) < 8 or (int(rock[6]), int(rock[7])) != coord]
        if kept:
            global_rock_collision_cells[cell] = kept
        else:
            global_rock_collision_cells.pop(cell, None)

def _nearby_rock_colliders(x, z):
    cell = _world_cell_coord(x, z, ROCK_COLLISION_CELL_SIZE)
    return global_rock_collision_cells.get(cell, ())

def _run_throttled_entity_update(entity, dt, interval, attr_name, update_fn):
    accumulated = float(getattr(entity, attr_name, 0.0)) + float(dt)
    if accumulated < interval:
        setattr(entity, attr_name, accumulated)
        return False
    setattr(entity, attr_name, 0.0)
    update_fn(accumulated)
    return True

def _update_npc_with_budget(npc, dt, px, pz):
    if getattr(npc, "highlight", False) or getattr(npc, "z_locked", False):
        npc._ai_far_accum = 0.0
        npc.update(dt)
        return True
    dist2 = _entity_distance_sq_2d(px, pz, npc.x, npc.z)
    if dist2 <= NPC_FULL_AI_DISTANCE * NPC_FULL_AI_DISTANCE:
        npc._ai_far_accum = 0.0
        npc.update(dt)
        return True
    return _run_throttled_entity_update(
        npc,
        dt,
        NPC_FAR_AI_INTERVAL,
        "_ai_far_accum",
        lambda step_dt: npc.update(step_dt),
    )

def _update_enemy_with_budget(enemy, dt, px, pz):
    if getattr(enemy, "selected", False) or getattr(enemy, "z_locked", False):
        enemy._ai_far_accum = 0.0
        enemy.update(player, dt)
        return True
    dist2 = _entity_distance_sq_2d(px, pz, enemy.x, enemy.z)
    active_distance = max(ENEMY_FULL_AI_DISTANCE, float(getattr(enemy, "aggro_range", 0.0)) + 8.0)
    if dist2 <= active_distance * active_distance:
        enemy._ai_far_accum = 0.0
        enemy.update(player, dt)
        return True
    return _run_throttled_entity_update(
        enemy,
        dt,
        ENEMY_FAR_AI_INTERVAL,
        "_ai_far_accum",
        lambda step_dt: enemy.update(player, step_dt),
    )

def _resource_node_key(kind, x, z, cx, cz):
    return (str(kind), int(cx), int(cz), int(round(float(x) * 2.0)), int(round(float(z) * 2.0)))

def _resource_ready(key, now, cooldown=3.5):
    last = resource_pickup_cooldowns.get(key, -9999.0)
    return (float(now) - float(last)) >= float(cooldown)

def _mark_resource_taken(key, now):
    resource_pickup_cooldowns[key] = float(now)
    if len(resource_pickup_cooldowns) > 2048:
        cutoff = float(now) - 120.0
        for old_key, last in list(resource_pickup_cooldowns.items()):
            if last < cutoff:
                resource_pickup_cooldowns.pop(old_key, None)

def _nearby_resource_chunks(px, pz):
    cx = player_chunk_coord(px)
    cz = player_chunk_coord(pz)
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            yield (cx + dx, cz + dz)

def try_gather_basic_resource(now):
    if player is None:
        return None
    if player.inventory_free() <= 0:
        player.last_pickup_message = f"{getattr(player, 'bag_name', 'mochila')} llena"
        player.last_pickup_time = float(now)
        return None
    px, pz = float(player.pos_x), float(player.pos_z)

    best = None
    best_dist2 = 999999999.0
    for kind, x, z, cx, cz, amount, radius2 in _nearby_resource_entries(px, pz):
        dist2 = _entity_distance_sq_2d(px, pz, x, z)
        if dist2 <= radius2 and dist2 < best_dist2:
            best = (kind, x, z, cx, cz, amount)
            best_dist2 = dist2

    if not best:
        return None
    item, x, z, cx, cz, amount = best
    key = _resource_node_key(item, x, z, cx, cz)
    if not _resource_ready(key, now):
        return None
    added = player.add_item(item, amount)
    player.last_pickup_time = float(now)
    if added > 0:
        _mark_resource_taken(key, now)
        log_throttled("RESOURCE_PICKUP", 0.2, item=item, amount=added, used=player.inventory_used(), cap=player.bag_capacity)
        return item
    return None

def _entity_alive(entity):
    return entity is not None and getattr(entity, "health", 1) > 0

class StoneProjectile:
    def __init__(self, x, y, z, vx, vy, vz, damage=2.0, max_distance=34.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vz = float(vz)
        self.damage = float(damage)
        self.distance_traveled = 0.0
        self.max_distance = float(max_distance)

    def update(self, dt, enemies):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vy -= 24.0 * dt
        self.distance_traveled += math.hypot(self.vx * dt, self.vz * dt)

        if self.y < -16.0 or self.distance_traveled > self.max_distance:
            return False

        ground_y = get_total_height(self.x, self.z)
        if self.y <= ground_y + 0.05:
            self.y = ground_y + 0.05
            return False

        for enemy in enemies:
            if not _entity_alive(enemy):
                continue
            dx = enemy.x - self.x
            dz = enemy.z - self.z
            dist2 = dx * dx + dz * dz
            if dist2 <= 0.8 * 0.8:
                if hasattr(enemy, "take_hit"):
                    enemy.take_hit(self.damage, source_x=self.x, source_z=self.z)
                else:
                    enemy.health -= self.damage
                return False

        return True

    def render(self):
        draw_box(self.x, self.y, self.z, 0.18, 0.18, 0.18, (0.40, 0.38, 0.34))


def spawn_stone_projectile(player, target):
    start_x = player.pos_x
    start_y = player.pos_y + getattr(player, 'player_height', 1.4) * 0.9
    start_z = player.pos_z
    if target is not None:
        target_y = getattr(target, 'y', player.pos_y) + 0.55
        dx = target.x - start_x
        dz = target.z - start_z
        dist = math.hypot(dx, dz)
        if dist < 0.5:
            dist = 0.5
        speed = 18.0
        vx = dx / dist * speed
        vz = dz / dist * speed
        vy = (target_y - start_y) * 0.75 + 5.5
    else:
        yaw = math.radians(player.yaw)
        pitch = math.radians(player.pitch)
        speed = 18.0
        vx = math.cos(yaw) * math.cos(pitch) * speed
        vz = math.sin(yaw) * math.cos(pitch) * speed
        vy = math.sin(pitch) * 12.0 + 4.0
    stone_projectiles.append(StoneProjectile(start_x, start_y, start_z, vx, vy, vz))


def update_stone_projectiles(dt):
    global stone_projectiles
    if not stone_projectiles:
        return
    alive = []
    for proj in stone_projectiles:
        if proj.update(dt, enemies):
            alive.append(proj)
    stone_projectiles = alive


def find_z_target(player, enemies, npcs, max_distance=22.0, max_angle_deg=85.0):
    """Busca el objetivo más útil cerca del centro de la mirada."""
    px = player.pos_x
    pz = player.pos_z
    yaw = math.radians(player.yaw)
    fx = math.cos(yaw)
    fz = math.sin(yaw)

    candidates = []
    for enemy in enemies:
        candidates.append(("enemy", enemy, 0.0))
    for npc in npcs:
        candidates.append(("npc", npc, 2.5))

    best = None
    best_score = 999999.0
    max_distance2 = max_distance * max_distance

    for kind, ent, penalty in candidates:
        dx = ent.x - px
        dz = ent.z - pz
        dist2 = dx * dx + dz * dz
        if dist2 <= 0.01 * 0.01 or dist2 > max_distance2:
            continue

        dist = math.sqrt(dist2)
        dot = (dx / dist) * fx + (dz / dist) * fz
        dot = max(-1.0, min(1.0, dot))
        angle = math.degrees(math.acos(dot))
        if angle > max_angle_deg:
            continue

        # Puntaje: prioriza estar cerca del centro de la cámara, luego distancia.
        score = angle * 1.8 + dist * 0.55 + penalty
        if score < best_score:
            best_score = score
            best = (kind, ent)

    return best

def update_z_target_lock(keys, player, enemies, npcs):
    """Q fija/suelta objetivo. Si el objetivo muere o se aleja, se libera."""
    global z_target, z_target_type, z_target_q_down

    q_down = bool(keys[pygame.K_q])
    if q_down and not z_target_q_down:
        if z_target is not None:
            z_target = None
            z_target_type = None
        else:
            found = find_z_target(player, enemies, npcs)
            if found:
                z_target_type, z_target = found
    z_target_q_down = q_down

    if z_target is None:
        return

    if z_target_type == "enemy":
        valid = z_target in enemies and _entity_alive(z_target)
    else:
        valid = z_target in npcs

    if not valid:
        z_target = None
        z_target_type = None
        return

    dist2 = _entity_distance_sq_2d(player.pos_x, player.pos_z, z_target.x, z_target.z)
    if dist2 > 28.0 * 28.0:
        z_target = None
        z_target_type = None


def _z_target_candidates(player, enemies, npcs, max_distance=26.0, max_angle_deg=110.0):
    px = player.pos_x
    pz = player.pos_z
    yaw = math.radians(player.yaw)
    fx = math.cos(yaw)
    fz = math.sin(yaw)
    result = []
    max_distance2 = max_distance * max_distance

    for kind, collection, penalty in (("enemy", enemies, 0.0), ("npc", npcs, 3.5)):
        for ent in collection:
            dx = ent.x - px
            dz = ent.z - pz
            dist2 = dx * dx + dz * dz
            if dist2 <= 0.01 * 0.01 or dist2 > max_distance2:
                continue
            dist = math.sqrt(dist2)
            dot = (dx / dist) * fx + (dz / dist) * fz
            dot = max(-1.0, min(1.0, dot))
            angle = math.degrees(math.acos(dot))
            if angle > max_angle_deg:
                continue
            score = angle * 1.4 + dist * 0.45 + penalty
            result.append((score, kind, ent))

    result.sort(key=lambda item: item[0])
    return result

def cycle_z_target(player, enemies, npcs):
    """Cambia al siguiente objetivo visible con TAB."""
    global z_target, z_target_type
    candidates = _z_target_candidates(player, enemies, npcs)
    if not candidates:
        z_target = None
        z_target_type = None
        return

    if z_target is None:
        _, z_target_type, z_target = candidates[0]
        return

    current_index = -1
    for i, (_, kind, ent) in enumerate(candidates):
        if ent is z_target:
            current_index = i
            break

    next_index = (current_index + 1) % len(candidates)
    _, z_target_type, z_target = candidates[next_index]

def apply_z_target_camera(player, dt):
    """Suaviza la mirada hacia el objetivo fijado. En tercera persona se siente tipo lock-on."""
    global z_target
    if z_target is None:
        return

    dx = z_target.x - player.pos_x
    dz = z_target.z - player.pos_z
    dist = math.hypot(dx, dz)
    if dist <= 0.01:
        return

    target_y = getattr(z_target, "y", player.pos_y)
    dy = (target_y + 0.45) - player.pos_y

    desired_yaw = math.degrees(math.atan2(dz, dx))
    desired_pitch = math.degrees(math.atan2(dy, max(0.1, dist)))

    yaw_diff = (desired_yaw - player.yaw + 180.0) % 360.0 - 180.0
    player.yaw += yaw_diff * min(1.0, dt * 5.8)
    player.pitch += (desired_pitch - player.pitch) * min(1.0, dt * 4.2)
    player.pitch = max(-38.0, min(38.0, player.pitch))

def agregar_rocas_de_chunk(rock_data, cx, cz):
    global global_rocks
    clear_total_height_query_cache()
    coord = (int(cx), int(cz))
    stone_amount = _resource_amount_for_world_detail("piedra")
    _clear_resource_index_for_chunk(coord, kinds=("piedra",))
    _clear_rock_collision_index_for_chunk(coord)
    global_rocks[coord] = []
    for rock in rock_data or []:
        try:
            indexed_rock = tuple(rock[:6]) + coord
            rx, _, rz, sx, sy, sz = indexed_rock[:6]
        except Exception:
            continue
        global_rocks[coord].append(indexed_rock)
        is_tall_skinny = sy > 1.4 and max(sx, sz) < 1.15
        is_tiny_bush = sy < 0.45 and max(sx, sz) < 0.75
        if not is_tall_skinny and not is_tiny_bush:
            _index_rock_collider(indexed_rock, coord[0], coord[1])
        if not is_tall_skinny:
            radius = max(0.85, min(2.0, max(sx, sz) * 0.70))
            _index_resource_entry("piedra", rx, rz, coord[0], coord[1], amount=stone_amount, radius=radius)

def agregar_recursos_de_chunk(grass_data, deco_data, cx, cz):
    global global_grass, global_trees
    coord = (int(cx), int(cz))
    fiber_amount = _resource_amount_for_world_detail("fibra")
    wood_amount = _resource_amount_for_world_detail("madera")
    _clear_resource_index_for_chunk(coord, kinds=("fibra", "madera"))
    global_grass[coord] = []
    for grass in grass_data or []:
        try:
            _, gx, gy, gz, gh = grass[:5]
            entry = (float(gx), float(gy), float(gz), float(gh), coord[0], coord[1])
            global_grass[coord].append(entry)
            if entry[3] >= 0.16:
                _index_resource_entry("fibra", entry[0], entry[2], coord[0], coord[1], amount=fiber_amount, radius=1.15)
        except Exception:
            continue
    global_trees[coord] = []
    for deco in deco_data or []:
        try:
            dtype, tx, ty, tz, variant = deco[:5]
        except Exception:
            continue
        if str(dtype).startswith("arbol_"):
            entry = (str(dtype), float(tx), float(ty), float(tz), str(variant), coord[0], coord[1])
            global_trees[coord].append(entry)
            _index_resource_entry("madera", entry[1], entry[3], coord[0], coord[1], amount=wood_amount, radius=2.15)

def eliminar_rocas_de_chunk(cx, cz):
    global global_rocks
    clear_total_height_query_cache()
    coord = (int(cx), int(cz))
    if coord in global_rocks:
        del global_rocks[coord]
    _clear_resource_index_for_chunk(coord, kinds=("piedra",))
    _clear_rock_collision_index_for_chunk(coord)
    eliminar_recursos_de_chunk(cx, cz)

def eliminar_recursos_de_chunk(cx, cz):
    coord = (int(cx), int(cz))
    global_grass.pop(coord, None)
    global_trees.pop(coord, None)
    _clear_resource_index_for_chunk(coord, kinds=("fibra", "madera"))

def encolar_lod_chunk(coord):
    global cola_lod_peticiones
    coord = (int(coord[0]), int(coord[1]))
    if coord in mundo_chunks or coord in mundo_chunks_simple or coord in cola_lod_peticiones:
        return False
    cola_lod_peticiones.append(coord)
    return True

def cancelar_lod_chunk(coord):
    global cola_lod_peticiones
    coord = (int(coord[0]), int(coord[1]))
    if coord in cola_lod_peticiones:
        cola_lod_peticiones.remove(coord)
        return True
    return False

def procesar_lods_pendientes(player_cx, player_cz, limit_override=None):
    """Crea pocos LOD por tanda para evitar picos al cruzar fronteras de chunk."""
    global cola_lod_peticiones, mundo_chunks_simple, stream_bridge_stats
    if not cola_lod_peticiones:
        return 0
    p_cx, p_cz = int(player_cx), int(player_cz)
    cola_lod_peticiones.sort(key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2)
    creados = 0
    intentos = 0
    limite = max(1, int(limit_override if limit_override is not None else LODS_CREAR_POR_TANDA))
    while cola_lod_peticiones and creados < limite and intentos < limite * 3:
        intentos += 1
        coord = cola_lod_peticiones.pop(0)
        if coord in mundo_chunks or coord in mundo_chunks_simple:
            continue
        try:
            mundo_chunks_simple[coord] = render_backend.register_gpu_handle(
                env.build_simple_chunk_list(
                    coord[0],
                    coord[1],
                    CHUNK_SIZE,
                    SEMILLA_MUNDO,
                    subdivisions=SUBDIVISIONES_LOD,
                )
            )
            creados += 1
        except Exception as exc:
            print(f"[LOD] No se pudo crear chunk simple {coord}: {exc}")
    stream_bridge_stats["lod_created_total"] += creados
    stream_bridge_stats["lod_queue_len"] = len(cola_lod_peticiones)
    stream_bridge_stats["lod_loaded"] = len(mundo_chunks_simple)
    return creados

def administrar_rejilla_chunks_stream_bridge(player_cx, player_cz):
    """Gestion experimental via Stage33 L. Solo corre con JUEGO_STREAM_BRIDGE_SAFE=1."""
    global cola_de_peticiones, mundo_chunks_simple, mundo_chunks, chunks_pendientes, stream_bridge_stats
    p_cx, p_cz = int(player_cx), int(player_cz)
    budget = get_stream_bridge_budget(RADIO_DETALLE, RADIO_VISION, MAX_COLA_PETICIONES)
    plan = build_world_chunk_stream_plan(
        center=(p_cx, p_cz),
        loaded_detail=mundo_chunks.keys(),
        loaded_lod=mundo_chunks_simple.keys(),
        queued_detail=cola_de_peticiones,
        pending_detail=chunks_pendientes.keys(),
        detail_radius=budget.detail_radius,
        lod_radius=budget.lod_radius,
        max_detail_requests=max(0, budget.max_detail_requests - len(cola_de_peticiones)),
    )
    stream_bridge_stats["enabled"] = 1
    stream_bridge_stats["preset"] = budget.preset
    stream_bridge_stats["detail_radius"] = budget.detail_radius
    stream_bridge_stats["lod_radius"] = budget.lod_radius
    stream_bridge_stats["max_requests"] = budget.max_detail_requests
    stream_bridge_stats["calls"] += 1
    stream_bridge_stats["last_center_x"] = p_cx
    stream_bridge_stats["last_center_z"] = p_cz

    lod_queued = 0
    detail_requested = 0
    detail_released = 0
    lod_released = 0
    requests_cancelled = 0

    for coord in plan.create_lod:
        if coord not in mundo_chunks and coord not in mundo_chunks_simple:
            if encolar_lod_chunk(coord):
                lod_queued += 1

    for coord in plan.request_detail:
        if len(cola_de_peticiones) >= MAX_COLA_PETICIONES:
            break
        if coord not in mundo_chunks and coord not in cola_de_peticiones and coord not in chunks_pendientes:
            cola_de_peticiones.append(coord)
            detail_requested += 1

    for coord in plan.release_detail:
        if coord in mundo_chunks:
            render_backend.release_gpu_handle(mundo_chunks[coord])
            del mundo_chunks[coord]
            env.clean_cache_for_chunk(*coord)
            eliminar_rocas_de_chunk(*coord)
            detail_released += 1
        if coord in cola_de_peticiones:
            cola_de_peticiones.remove(coord)
            requests_cancelled += 1
        if cancelar_lod_chunk(coord):
            requests_cancelled += 1
        if coord in chunks_pendientes:
            del chunks_pendientes[coord]
            requests_cancelled += 1

    for coord in plan.release_lod:
        cancelar_lod_chunk(coord)
        if coord in mundo_chunks_simple:
            render_backend.release_gpu_handle(mundo_chunks_simple[coord])
            del mundo_chunks_simple[coord]
            lod_released += 1

    for coord in plan.cancel_requests:
        if coord in cola_de_peticiones:
            cola_de_peticiones.remove(coord)
            requests_cancelled += 1
        if cancelar_lod_chunk(coord):
            requests_cancelled += 1
        if coord in chunks_pendientes:
            del chunks_pendientes[coord]
            requests_cancelled += 1

    stream_bridge_stats["lod_queued_total"] += lod_queued
    stream_bridge_stats["detail_requested_total"] += detail_requested
    stream_bridge_stats["detail_released_total"] += detail_released
    stream_bridge_stats["lod_released_total"] += lod_released
    stream_bridge_stats["requests_cancelled_total"] += requests_cancelled
    stream_bridge_stats["queue_len"] = len(cola_de_peticiones)
    stream_bridge_stats["lod_queue_len"] = len(cola_lod_peticiones)
    stream_bridge_stats["pending_len"] = len(chunks_pendientes)
    stream_bridge_stats["detail_loaded"] = len(mundo_chunks)
    stream_bridge_stats["lod_loaded"] = len(mundo_chunks_simple)

def administrar_rejilla_chunks(player_cx, player_cz, dir_x, dir_z):
    """Gestión menos agresiva de chunks.

    - El anillo visible se cubre con LOD simple.
    - Los 9 chunks alrededor del jugador usan detalle completo.
    - La predicción hacia adelante mantiene LOD simple para evitar zonas negras.
    """
    if ENABLE_STREAM_BRIDGE_SAFE:
        administrar_rejilla_chunks_stream_bridge(player_cx, player_cz)
        return

    global cola_de_peticiones, mundo_chunks_simple
    chunks_simples = set()
    chunks_detalle = set()
    p_cx, p_cz = int(player_cx), int(player_cz)

    for dx in range(-RADIO_VISION, RADIO_VISION + 1):
        for dz in range(-RADIO_VISION, RADIO_VISION + 1):
            chunks_simples.add((p_cx + dx, p_cz + dz))

    # 9 chunks con detalle: actual + 8 adyacentes.
    for dx in range(-RADIO_DETALLE, RADIO_DETALLE + 1):
        for dz in range(-RADIO_DETALLE, RADIO_DETALLE + 1):
            chunks_detalle.add((p_cx + dx, p_cz + dz))
            chunks_simples.add((p_cx + dx, p_cz + dz))

    if dir_x != 0 or dir_z != 0:
        norm = math.hypot(dir_x, dir_z)
        if norm > 0:
            dir_x /= norm
            dir_z /= norm
            pred_cx = p_cx + int(round(dir_x))
            pred_cz = p_cz + int(round(dir_z))
            chunks_simples.add((pred_cx, pred_cz))

    for coord in sorted(chunks_simples, key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2):
        if coord not in mundo_chunks and coord not in mundo_chunks_simple:
            encolar_lod_chunk(coord)

    detalle_ordenado = sorted(chunks_detalle, key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2)
    for coord in detalle_ordenado:
        if coord not in mundo_chunks and coord not in cola_de_peticiones and coord not in chunks_pendientes:
            if len(cola_de_peticiones) < MAX_COLA_PETICIONES:
                cola_de_peticiones.append(coord)

    for coord in list(mundo_chunks.keys()):
        if coord not in chunks_detalle:
            render_backend.release_gpu_handle(mundo_chunks[coord])
            del mundo_chunks[coord]
            env.clean_cache_for_chunk(*coord)
            eliminar_rocas_de_chunk(*coord)
            if coord in cola_de_peticiones:
                cola_de_peticiones.remove(coord)
            cancelar_lod_chunk(coord)
            if coord in chunks_pendientes:
                del chunks_pendientes[coord]

    for coord in list(mundo_chunks_simple.keys()):
        if coord not in chunks_simples or coord in mundo_chunks:
            render_backend.release_gpu_handle(mundo_chunks_simple[coord])
            del mundo_chunks_simple[coord]
            cancelar_lod_chunk(coord)

def procesar_comunicacion_multiproceso():
    global chunk_generándose_ahora, cola_de_peticiones, chunks_pendientes
    if not chunk_generándose_ahora and cola_de_peticiones:
        proximo = cola_de_peticiones.pop(0)
        pipe_juego.send((int(proximo[0]), int(proximo[1])))
        chunk_generándose_ahora = True

    if chunk_generándose_ahora and pipe_juego.poll():
        try:
            recibido = pipe_juego.recv()
            if len(recibido) == 8:
                cx, cz, q, g, r, d, w, h = recibido
            else:
                cx, cz, q, g, r, d, h = recibido
                w = []
            env._height_cache[(int(cx), int(cz))] = h
            chunks_pendientes[(int(cx), int(cz))] = (q, g, r, d, w)
            agregar_rocas_de_chunk(r, cx, cz)
            agregar_recursos_de_chunk(g, d, cx, cz)
        except Exception as e:
            print(f"[ERROR] al recibir chunk: {e}")
        chunk_generándose_ahora = False

def compilar_un_chunk_pendiente():
    global chunks_pendientes, mundo_chunks, mundo_chunks_simple
    if not chunks_pendientes:
        return False
    px, _, pz, _, _, _ = player.get_camera_vectors()
    def distancia(coord):
        cx, cz = coord
        return (cx*CHUNK_SIZE - px)**2 + (cz*CHUNK_SIZE - pz)**2
    coord = min(chunks_pendientes.keys(), key=distancia)
    data = chunks_pendientes.pop(coord)
    if len(data) == 5:
        q, g, r, d, w = data
    else:
        q, g, r, d = data
        w = []
    mesh_data = env.build_chunk_mesh_data(coord[0], coord[1], q, g, r, d, w, size=CHUNK_SIZE, lod="detail")
    mundo_chunks[coord] = render_backend.upload_chunk_mesh(mesh_data)
    if coord in mundo_chunks_simple:
        render_backend.release_gpu_handle(mundo_chunks_simple[coord])
        del mundo_chunks_simple[coord]
    return True

# ------------------------------
# Bucle principal
# ------------------------------
def update(dt):
    global tiempo_log, tiempo_chunks, target_fov, current_fov, last_attack_time, enemies, admin_hub, z_target, z_target_type, z_target_cycle_down, slime_remnants
    begin_total_height_query_frame()
    engine.handle_events()
    update_adaptive_render_quality(dt)
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks() / 1000.0
    craft_down = bool(keys[pygame.K_c])
    if craft_down and not getattr(update, "craft_down", False):
        ok, message, info = player.craft_best_weapon()
        player.last_craft_time = current_time
        log_throttled("CRAFT_WEAPON", 0.1, ok=ok, message=message, weapon=info.get("key"), uses=info.get("uses"))
    update.craft_down = craft_down

    # Admin Hub: F1 abre/cierra. Cuando está abierto, bloquea cámara/movimiento
    # para que los botones se puedan usar con mouse.
    if admin_hub:
        admin_hub.update(dt, keys, player, enemies, npcs, get_total_height, NPC, Enemy, SEMILLA_MUNDO)
        if admin_hub.visible:
            # Mantener entidades vivas, pero pausar controles de jugador/cámara.
            if admin_hub.ai_enabled:
                for npc in npcs:
                    npc.update(dt)
                for enemy in enemies[:]:
                    enemy.update(player, dt)
                    if enemy.health <= 0:
                        slime_remnants.append(enemy.create_remnant())
                        enemies.remove(enemy)
                for rem in slime_remnants[:]:
                    rem.update(dt)
                    if not rem.alive():
                        slime_remnants.remove(rem)
            return

    # Sprint
    if not hasattr(update, "is_sprinting"):
        update.is_sprinting = False
    if keys[pygame.K_LSHIFT] and player.stamina > 10:
        target_fov = 55.0
        player.speed = 10.0
        player.stamina -= 30 * dt
        if player.stamina < 0:
            player.stamina = 0
        update.is_sprinting = True
    else:
        if not keys[pygame.K_LSHIFT] or player.stamina <= 0:
            target_fov = 45.0
            player.speed = 5.0
            update.is_sprinting = False
        if player.stamina < 100:
            player.stamina += 15 * dt
            if player.stamina > 100:
                player.stamina = 100

    current_fov += (target_fov - current_fov) * 0.15
    if abs(current_fov - target_fov) < 0.01:
        current_fov = target_fov

    # Dirección del movimiento (para predicción de chunks)
    yaw_rad = math.radians(player.yaw)
    fx = math.cos(yaw_rad)
    fz = math.sin(yaw_rad)
    dx_move, dz_move = 0.0, 0.0
    if keys[pygame.K_w]:
        dx_move += fx; dz_move += fz
    if keys[pygame.K_s]:
        dx_move -= fx; dz_move -= fz
    if keys[pygame.K_a]:
        dx_move += fz; dz_move -= fx
    if keys[pygame.K_d]:
        dx_move -= fz; dz_move += fx
    norm = math.hypot(dx_move, dz_move)
    if norm > 0:
        dx_move /= norm; dz_move /= norm

    with perf_tracker.measure("world_context"):
        update_player_world_context(dt)
    with perf_tracker.measure("player_move"):
        player.process_mouse()
        player.process_keyboard(dt, get_total_height)
        if hasattr(player, "update_attack_animation"):
            player.update_attack_animation(dt)
        if hasattr(player, "update_pickup_notices"):
            player.update_pickup_notices(dt)
    last_gather = getattr(update, "last_resource_gather", 0.0)
    if current_time - last_gather >= 0.25:
        with perf_tracker.measure("resource_gather"):
            try_gather_basic_resource(current_time)
        update.last_resource_gather = current_time

    px, py, pz, _, _, _ = player.get_camera_vectors()
    chunk_actual_x = player_chunk_coord(px)
    chunk_actual_z = player_chunk_coord(pz)

    # Gestión de chunks (cada 50 ms)
    stream_interval = _adaptive_stream_interval()
    lod_limit = _adaptive_lod_limit()
    adaptive_streaming["interval"] = stream_interval
    adaptive_streaming["lod_limit"] = lod_limit
    stream_coord = (int(chunk_actual_x), int(chunk_actual_z))
    force_stream = stream_coord != getattr(update, "last_stream_chunk", None)
    adaptive_streaming["forced"] = int(bool(force_stream))
    tiempo_chunks += dt
    if force_stream or tiempo_chunks >= stream_interval:
        tiempo_chunks = 0.0
        update.last_stream_chunk = stream_coord
        with perf_tracker.measure("chunk_total"):
            with perf_tracker.measure("chunk_admin"):
                administrar_rejilla_chunks(chunk_actual_x, chunk_actual_z, dx_move, dz_move)
            with perf_tracker.measure("chunk_lod"):
                procesar_lods_pendientes(chunk_actual_x, chunk_actual_z, limit_override=lod_limit)
            with perf_tracker.measure("chunk_comm"):
                procesar_comunicacion_multiproceso()
            with perf_tracker.measure("chunk_compile"):
                for _ in range(CHUNKS_COMPILAR_POR_FRAME):
                    if not compilar_un_chunk_pendiente():
                        break

    # Ataque
    if pygame.mouse.get_pressed()[0] and (current_time - last_attack_time) >= attack_cooldown:
        if z_target_type == "enemy" and z_target is not None and player.has_items({"piedra": 1}):
            if player.consume_items({"piedra": 1}):
                spawn_stone_projectile(player, z_target)
                if audio and hasattr(audio, 'play_sound'):
                    audio.play_sound("lanzar", volume=0.7)
                last_attack_time = current_time
        else:
            if hasattr(player, "start_attack_swing"):
                player.start_attack_swing()
            locked_enemy = z_target if z_target_type == "enemy" else None
            hit_enemy = attack_enemy(player, enemies, locked_target=locked_enemy, attack_range=3.2)
            last_attack_time = current_time
            if hit_enemy:
                if audio and hasattr(audio, 'play_sound'):
                    audio.play_sound("golpe", volume=0.7)
                if z_target_type == "enemy" and z_target is not None and z_target not in enemies:
                    z_target = None
                    z_target_type = None

    update_stone_projectiles(dt)

    # Selección visual del enemigo cercano y Z Targeting.
    for enemy in enemies:
        enemy.selected = False
        enemy.z_locked = False
    for npc in npcs:
        npc.z_locked = False

    close_enemy = None
    close_enemy_dist2 = 999999999.0
    for enemy in enemies:
        ed2 = _entity_distance_sq_2d(px, pz, enemy.x, enemy.z)
        if ed2 < 4.0 * 4.0 and ed2 < close_enemy_dist2:
            close_enemy = enemy
            close_enemy_dist2 = ed2
    if close_enemy is not None:
        close_enemy.selected = True

    if z_target is not None:
        if z_target_type == "enemy":
            z_target.selected = True
        z_target.z_locked = True

    # Interacción con NPCs
    global npc_dialog, npc_prompt, npc_name_label, npc_description, last_interact_time
    npc_prompt = ""
    npc_name_label = ""
    npc_description = ""
    for npc in npcs:
        npc.highlight = False
    global npc_label_screen
    npc_label_screen = None
    for npc in npcs:
        dist2 = _entity_distance_sq_2d(px, pz, npc.x, npc.z)
        if dist2 < 4.0 * 4.0:
            npc_name_label = f"{npc.nombre} {npc.titulo}"
            npc_description = npc.descripcion
            npc_prompt = f"Pulsa botón E para interactuar con {npc.nombre}"
            npc.highlight = True
            npc.screen_label = None
            if keys[pygame.K_e] and (current_time - last_interact_time) >= 0.35:
                npc_dialog = npc.interactuar()
                last_interact_time = current_time
            break

    # Actualizar entidades. El Admin Hub puede pausar la IA.
    ai_active = True
    if admin_hub:
        ai_active = admin_hub.ai_enabled

    with perf_tracker.measure("ai"):
        if ai_active:
            for npc in npcs:
                _update_npc_with_budget(npc, dt, px, pz)

            for enemy in enemies[:]:
                _update_enemy_with_budget(enemy, dt, px, pz)
                if enemy.health <= 0:
                    slime_remnants.append(enemy.create_remnant())
                    enemies.remove(enemy)

        for rem in slime_remnants[:]:
            rem.update(dt)
            if not rem.alive():
                slime_remnants.remove(rem)

    # Guardado / carga
    if keys[pygame.K_F5]:
        save_game(player, SEMILLA_MUNDO)
        print(f"[SAVE] Mundo guardado. Semilla={SEMILLA_MUNDO} X={player.pos_x:.1f} Z={player.pos_z:.1f}")
        pygame.time.wait(200)
    if keys[pygame.K_F9]:
        data = load_game_data()
        if data and int(data.get("seed", SEMILLA_MUNDO)) == int(SEMILLA_MUNDO):
            apply_save_to_player(player, data)
            log_event("F9_RELOAD_RAW", x=player.pos_x, y=player.pos_y, z=player.pos_z, health=player.health)
            safe_x, suelo, safe_z = find_safe_player_position(player.pos_x, player.pos_z, reason="f9_reload")
            player.pos_x = safe_x
            player.pos_z = safe_z
            player.pos_y = suelo + player.player_height + 0.08
            player.velocity_y = 0
            player.is_grounded = True
            player._last_safe_x = player.pos_x
            player._last_safe_y = player.pos_y
            player._last_safe_z = player.pos_z
            set_player_respawn_point(player, player.pos_x, player.pos_z)
            print(f"[LOAD] Partida recargada. X={player.pos_x:.1f} Z={player.pos_z:.1f}")
        elif data:
            print("[LOAD] La partida guardada usa otra semilla. Reinicia y usa Continuar.")
        else:
            print("[LOAD] No hay partida guardada.")
        pygame.time.wait(200)

    # Log cada 0.5s
    tiempo_log += dt
    if tiempo_log >= 0.5:
        print(f"[INFO] FOV: {current_fov:.1f} | Chunk: ({chunk_actual_x},{chunk_actual_z}) | Vida: {player.health:.0f} | Stamina: {player.stamina:.0f} | Enemigos: {len(enemies)}")
        if ENABLE_STREAM_BRIDGE_SAFE:
            print(
                "[STREAM-BRIDGE] "
                f"calls={stream_bridge_stats.get('calls', 0)} "
                f"center=({stream_bridge_stats.get('last_center_x', 0)},{stream_bridge_stats.get('last_center_z', 0)}) "
                f"req={stream_bridge_stats.get('detail_requested_total', 0)} "
                f"lodQ={stream_bridge_stats.get('lod_queued_total', 0)} "
                f"lod={stream_bridge_stats.get('lod_created_total', 0)} "
                f"freeD={stream_bridge_stats.get('detail_released_total', 0)} "
                f"freeL={stream_bridge_stats.get('lod_released_total', 0)} "
                f"cancel={stream_bridge_stats.get('requests_cancelled_total', 0)} "
                f"queue={stream_bridge_stats.get('queue_len', 0)} "
                f"lodQueue={stream_bridge_stats.get('lod_queue_len', 0)} "
                f"pending={stream_bridge_stats.get('pending_len', 0)} "
                f"loadedD={stream_bridge_stats.get('detail_loaded', 0)} "
                f"loadedL={stream_bridge_stats.get('lod_loaded', 0)}"
            )
        tiempo_log = 0.0
    if PRESET_SAMPLE_LOG_ENABLED:
        update.preset_sample_accum = float(getattr(update, "preset_sample_accum", 0.0)) + float(dt)
        if update.preset_sample_accum >= max(0.5, float(PRESET_SAMPLE_LOG_INTERVAL)):
            update.preset_sample_accum = 0.0
            sample_fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0.0
            _append_preset_runtime_sample(sample_fps)

def render_3d():
    global current_fov, z_target_screen, render_stats, npc_label_screen
    z_target_screen = None
    npc_label_screen = None
    frame_stats = render_backend.begin_frame() if render_backend else None
    render_stats = frame_stats.as_dict() if frame_stats else {
        "chunks_detalle": 0,
        "chunks_lod": 0,
        "chunks_ocultos": 0,
        "entidades_render": 0,
        "entidades_ocultas": 0,
        "entidades_transparentes": 0,
        "backend": "opengl",
        "render_passes": 0,
        "render_packets": 0,
    }
    render_stats.update({f"stream_bridge_{k}": v for k, v in stream_bridge_stats.items()})
    render_stats.update({f"perf_{k}": v for k, v in perf_tracker.snapshot_for_render().items()})
    render_stats["adaptive_quality_enabled"] = int(bool(adaptive_quality.get("enabled", True)))
    render_stats["adaptive_quality_scale"] = float(adaptive_quality.get("scale", 1.0) or 1.0)
    render_stats["adaptive_quality_state"] = str(adaptive_quality.get("state", "OK"))
    render_stats["adaptive_quality_fps_avg"] = float(adaptive_quality.get("fps_avg", 0.0) or 0.0)
    chunk_render_distance = _adaptive_chunk_render_distance()
    fog_start, fog_end = _adaptive_fog_range()
    render_stats["adaptive_chunk_distance"] = int(chunk_render_distance)
    render_stats["adaptive_fog_end"] = int(fog_end)
    render_stats["adaptive_stream_interval_ms"] = int(float(adaptive_streaming.get("interval", 0.05)) * 1000)
    render_stats["adaptive_stream_lod_limit"] = int(adaptive_streaming.get("lod_limit", LODS_CREAR_POR_TANDA))
    render_stats["adaptive_stream_forced"] = int(adaptive_streaming.get("forced", 0))
    world_detail_status = _world_detail_debug_status()
    render_stats["world_detail_preset"] = str(world_detail_status.get("preset", "balanced")).upper()
    render_stats["world_detail_grass"] = float(world_detail_status.get("grass", 0.0) or 0.0)
    render_stats["world_detail_deco"] = float(world_detail_status.get("deco", 0.0) or 0.0)
    render_stats["world_detail_rock"] = float(world_detail_status.get("rock", 0.0) or 0.0)
    render_stats["world_detail_planes"] = (
        int(world_detail_status.get("grass_planes", 0) or 0),
        int(world_detail_status.get("deco_planes", 0) or 0),
        int(world_detail_status.get("leaf_planes", 0) or 0),
        int(world_detail_status.get("tree_layers", 0) or 0),
        int(world_detail_status.get("rock_detail", 0) or 0),
    )
    render_stats["world_resource_amounts"] = (
        int(world_detail_status.get("fibra_amount", 1) or 1),
        int(world_detail_status.get("madera_amount", 1) or 1),
        int(world_detail_status.get("piedra_amount", 1) or 1),
    )

    r3d.setup_perspective(current_fov, ANCHO / ALTO, 0.1, 400.0)
    px, py, pz, lx, ly, lz = player.get_camera_vectors()
    r3d.setup_camera(px, py, pz, lx, ly, lz)

    color_horizonte = [0.75, 0.88, 1.0]
    r3d.setup_fog(color_horizonte)
    render_backend.configure_fog(FogConfig(tuple(color_horizonte), fog_start, fog_end))
    render_backend.draw_skybox(env, px, py, pz, size=300.0)

    # FrameGraph: primero armamos paquetes visibles y despues los ejecutamos.
    # Esto prepara el motor para command buffers/RenderPasses de Vulkan.
    render_graph.begin_frame()
    if DEBUG_RENDER_ALL_CHUNKS:
        add_all_chunks_to_render_graph()
    else:
        add_visible_chunks_to_render_graph(px, pz, lx, lz)

    # El jugador y las entidades se agregan al FrameGraph como paquetes.
    # Esto prepara el camino para command buffers Vulkan sin romper el render actual.
    if DEBUG_RENDER_ALL_ENTITIES:
        add_all_entities_to_render_graph(px, pz, lx, lz)
    else:
        if getattr(player, "camera_mode", "first") == "third":
            render_graph.add_entity(
                "player", player,
                render_fn=lambda player=player: render_player_avatar(
                    player.pos_x,
                    player.pos_y - player.player_height,
                    player.pos_z,
                    yaw=getattr(player, "visual_yaw", player.yaw + 90.0),
                    walk_phase=getattr(player, "walk_phase", 0.0),
                    move_amount=getattr(player, "move_amount", 0.0),
                    swimming=getattr(player, "is_swimming", False),
                    held_weapon=player.weapon_key() if hasattr(player, "weapon_key") else None,
                    attack_swing=player.attack_swing_value() if hasattr(player, "attack_swing_value") else 0.0,
                ),
                transparent=False, priority=-5
            )

        remnant_distance = _adaptive_distance(REMNANT_RENDER_DISTANCE, 0.50)
        entity_distance = _adaptive_distance(ENTITY_RENDER_DISTANCE, 0.58)
        label_distance = _adaptive_distance(ENTITY_LABEL_DISTANCE, 0.62)

        for rem in slime_remnants:
            if env.is_point_visible_for_render(rem.x, rem.z, px, pz, lx, lz, max_distance=remnant_distance):
                render_graph.add_entity("slime_remnant", rem, render_fn=lambda rem=rem: rem.render(), transparent=True, priority=5)
            else:
                render_stats["entidades_ocultas"] += 1

        for enemy in enemies:
            locked = bool(getattr(enemy, "z_locked", False))
            visible = locked or env.is_point_visible_for_render(enemy.x, enemy.z, px, pz, lx, lz, max_distance=entity_distance)
            if visible:
                detail = _entity_detail_level(px, pz, enemy.x, enemy.z, forced_full=locked or bool(getattr(enemy, "selected", False)))
                render_graph.add_entity("enemy", enemy, render_fn=lambda enemy=enemy, detail=detail: enemy.render(detail_level=detail), transparent=False)
            else:
                render_stats["entidades_ocultas"] += 1
            if locked:
                z_target_screen = world_to_screen(enemy.x, enemy.y + 0.9, enemy.z)

        for npc in npcs:
            locked = bool(getattr(npc, "z_locked", False))
            highlighted = bool(npc.highlight)
            visible = locked or highlighted or env.is_point_visible_for_render(npc.x, npc.z, px, pz, lx, lz, max_distance=entity_distance)
            if visible:
                detail = _entity_detail_level(px, pz, npc.x, npc.z, forced_full=locked or highlighted)
                render_graph.add_entity(
                    "npc", npc,
                    render_fn=lambda npc=npc, highlighted=highlighted, locked=locked, detail=detail: npc.render(
                        highlight=bool(highlighted or locked),
                        debug_hitbox=bool(highlighted and admin_hub and admin_hub.visible),
                        detail_level=detail,
                    ),
                    transparent=False
                )
            else:
                render_stats["entidades_ocultas"] += 1

            if highlighted:
                # Las etiquetas en mundo se calculan sólo cerca para ahorrar proyección 2D.
                dx = npc.x - player.pos_x
                dz = npc.z - player.pos_z
                if dx * dx + dz * dz <= label_distance * label_distance:
                    npc.screen_label = world_to_screen(npc.x, npc.y + (npc.height if hasattr(npc, 'height') else 1.6) + 0.15, npc.z)
                    if npc.screen_label is not None:
                        npc_label_screen = npc.screen_label
            if locked:
                z_target_screen = world_to_screen(npc.x, npc.y + 2.1, npc.z)

        for idx, proj in enumerate(stone_projectiles):
            render_graph.add_entity(f"stone_projectile_{idx}", proj, render_fn=lambda proj=proj: proj.render(), transparent=False)

    render_graph.execute(render_backend, render_stats)
    render_stats.update(render_graph.as_stats())
    if getattr(player, "camera_mode", "first") == "first":
        render_first_person_weapon(
            px, py, pz, lx, ly, lz,
            weapon_key=player.weapon_key() if hasattr(player, "weapon_key") else None,
            attack_swing=player.attack_swing_value() if hasattr(player, "attack_swing_value") else 0.0,
        )

    r3d.disable_fog()


def add_visible_chunks_to_render_graph(px, pz, lx, lz):
    """Agrega sólo los chunks visibles al frame graph."""
    max_chunk_distance = _adaptive_chunk_render_distance()
    for chunk_map, lod in ((mundo_chunks_simple, "lod"), (mundo_chunks, "detail")):
        for (cx, cz), id_list in chunk_map.items():
            if render_backend.is_chunk_visible(env, cx, cz, px, pz, lx, lz, size=CHUNK_SIZE, max_distance=max_chunk_distance):
                render_graph.add_chunk((cx, cz), id_list, lod=lod)
            else:
                render_stats["chunks_ocultos"] += 1


def add_all_chunks_to_render_graph():
    """Agrega todos los chunks cargados sin comprobar visibilidad."""
    for chunk_map, lod in ((mundo_chunks_simple, "lod"), (mundo_chunks, "detail")):
        for coord, id_list in chunk_map.items():
            render_graph.add_chunk(coord, id_list, lod=lod)


def add_all_entities_to_render_graph(px, pz, lx, lz):
    """Agrega todas las entidades al frame graph sin comprobar visibilidad."""
    if getattr(player, "camera_mode", "first") == "third":
        render_graph.add_entity(
            "player", player,
            render_fn=lambda player=player: render_player_avatar(
                player.pos_x,
                player.pos_y - player.player_height,
                player.pos_z,
                yaw=getattr(player, "visual_yaw", player.yaw + 90.0),
                walk_phase=getattr(player, "walk_phase", 0.0),
                move_amount=getattr(player, "move_amount", 0.0),
                swimming=getattr(player, "is_swimming", False),
                held_weapon=player.weapon_key() if hasattr(player, "weapon_key") else None,
                attack_swing=player.attack_swing_value() if hasattr(player, "attack_swing_value") else 0.0,
            ),
            transparent=False, priority=-5
        )

    for rem in slime_remnants:
        render_graph.add_entity("slime_remnant", rem, render_fn=lambda rem=rem: rem.render(), transparent=True, priority=5)

    for enemy in enemies:
        render_graph.add_entity("enemy", enemy, render_fn=lambda enemy=enemy: enemy.render(), transparent=False)

    for npc in npcs:
        highlighted = bool(npc.highlight)
        render_graph.add_entity(
            "npc", npc,
            render_fn=lambda npc=npc, highlighted=highlighted: npc.render(
                highlight=highlighted,
                debug_hitbox=bool(highlighted and admin_hub and admin_hub.visible)
            ),
            transparent=False
        )


def render_2d():
    r2d.begin_2d(ANCHO, ALTO)
    draw_ui(player)
    draw_pickup_notices(player)
    draw_world_context(player)
    fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0
    draw_adaptive_quality(adaptive_quality.get("state", "OK"), adaptive_quality.get("scale", 1.0), ANCHO - 222, ALTO - 44)
    draw_fps_counter(fps, ANCHO - 104, ALTO - 44)
    if admin_hub and admin_hub.visible:
        r2d.draw_text_2d(
            f"Render[{render_stats.get('backend','opengl')}]: {fps:.0f} FPS | chunks D:{render_stats.get('chunks_detalle',0)} LOD:{render_stats.get('chunks_lod',0)} ocultos:{render_stats.get('chunks_ocultos',0)} | ent:{render_stats.get('entidades_render',0)}/{render_stats.get('entidades_ocultas',0)}",
            24, 132, (190, 235, 210)
        )
        r2d.draw_text_2d(
            f"AutoQuality: {render_stats.get('adaptive_quality_state','OK')} escala:{render_stats.get('adaptive_quality_scale',1.0):.2f} fpsAvg:{render_stats.get('adaptive_quality_fps_avg',0.0):.1f} chunk:{render_stats.get('adaptive_chunk_distance',0)} fog:{render_stats.get('adaptive_fog_end',0)} stream:{render_stats.get('adaptive_stream_interval_ms',0)}ms lod:{render_stats.get('adaptive_stream_lod_limit',0)} force:{render_stats.get('adaptive_stream_forced',0)}",
            24, 264, (180, 235, 180)
        )
        planes = render_stats.get("world_detail_planes", (0, 0, 0, 0, 0))
        amounts = render_stats.get("world_resource_amounts", (1, 1, 1))
        r2d.draw_text_2d(
            f"WorldPreset: {render_stats.get('world_detail_preset','BALANCED')} dens G:{render_stats.get('world_detail_grass',0):.2f} D:{render_stats.get('world_detail_deco',0):.2f} R:{render_stats.get('world_detail_rock',0):.2f} planes g/d/l/t/r:{planes[0]}/{planes[1]}/{planes[2]}/{planes[3]}/{planes[4]} res F/M/P:{amounts[0]}/{amounts[1]}/{amounts[2]}",
            24, 286, (205, 225, 255)
        )
        if render_stats.get("perf_frame"):
            r2d.draw_text_2d(
                f"Perf ms: frame:{render_stats.get('perf_frame',0):.1f} update:{render_stats.get('perf_update',0):.1f} chunks:{render_stats.get('perf_chunk_total',0):.1f} r3d:{render_stats.get('perf_render3d',0):.1f} flip:{render_stats.get('perf_flip',0):.1f}",
                24, 242, (255, 210, 140)
            )
        r2d.draw_text_2d(
            f"Mesh: V:{render_stats.get('mesh_vertices',0)} I:{render_stats.get('mesh_indices',0)} Q:{render_stats.get('mesh_quads',0)} Batches:{render_stats.get('material_batches',0)} RAM~GPU:{render_stats.get('mesh_bytes',0)//1024}KB Uploads:{render_stats.get('uploads_frame',0)} | Pass:{render_stats.get('render_passes',0)} Pack:{render_stats.get('render_packets',0)} TransEnt:{render_stats.get('entidades_transparentes',0)}",
            24, 154, (185, 220, 245)
        )
        r2d.draw_text_2d(
            f"Instances: total:{render_stats.get('instance_total',0)} kinds:{render_stats.get('instance_kinds',0)} transp:{render_stats.get('instance_transparent',0)} player:{render_stats.get('instance_player',0)} enemy:{render_stats.get('instance_enemy',0)} npc:{render_stats.get('instance_npc',0)} StaticDraw:{render_stats.get('entidades_staticmesh',0)} Debug:{render_stats.get('static_entity_debug',0)}",
            24, 176, (220, 210, 245)
        )
        r2d.draw_text_2d(
            f"VulkanPrep: probe:{render_stats.get('vulkan_probe_ok',0)} tri:{render_stats.get('vulkan_triangle_ok',0)} chunk:{render_stats.get('vulkan_chunk_upload_ok',0)} mem:{render_stats.get('vulkan_memory_ok',0)} map:{render_stats.get('vulkan_staging_mapped',0)} cmd:{render_stats.get('vulkan_command_ok',0)} draw:{render_stats.get('vulkan_draw_ok',0)} rp:{render_stats.get('vulkan_render_pass_plan',0)} pipe:{render_stats.get('vulkan_pipeline_plan',0)} idx:{render_stats.get('vulkan_draw_indexed_plan',0)} sh:{render_stats.get('vulkan_shader_ok',0)} spv:{render_stats.get('vulkan_spirv_generated',0)} mods:{render_stats.get('vulkan_shader_modules',0)} layout:{render_stats.get('vulkan_pipeline_layout_ok',0)} fb:{render_stats.get('vulkan_framebuffer_ok',0)} begin:{render_stats.get('vulkan_renderpass_begin_ok',0)} didx:{render_stats.get('vulkan_draw_indexed_recorded',0)} comp:{render_stats.get('vulkan_shader_compiler',0)} shKB:{render_stats.get('vulkan_shader_bytes',0)//1024} copy:{render_stats.get('vulkan_copy_commands',0)} sub:{render_stats.get('vulkan_submits',0)} writeKB:{render_stats.get('vulkan_staging_write_kb',0)} allocKB:{render_stats.get('vulkan_alloc_kb',0)} vkKB:{render_stats.get('vulkan_upload_bytes',0)//1024} dev:{render_stats.get('vulkan_devices',0)}",
            24, 198, (245, 220, 160)
        )
        if render_stats.get("stream_bridge_enabled"):
            r2d.draw_text_2d(
                f"StreamBridge: ON calls:{render_stats.get('stream_bridge_calls',0)} center:{render_stats.get('stream_bridge_last_center_x',0)},{render_stats.get('stream_bridge_last_center_z',0)} req:{render_stats.get('stream_bridge_detail_requested_total',0)} lod+:{render_stats.get('stream_bridge_lod_created_total',0)} freeD:{render_stats.get('stream_bridge_detail_released_total',0)} freeL:{render_stats.get('stream_bridge_lod_released_total',0)} cancel:{render_stats.get('stream_bridge_requests_cancelled_total',0)} q:{render_stats.get('stream_bridge_queue_len',0)} pend:{render_stats.get('stream_bridge_pending_len',0)} loaded D:{render_stats.get('stream_bridge_detail_loaded',0)} L:{render_stats.get('stream_bridge_lod_loaded',0)}",
                24, 220, (170, 245, 190)
            )
    r2d.draw_rect_2d((ANCHO // 2) - 2, (ALTO // 2) - 2, 4, 4, (1, 1, 1))
    draw_npc_label(npc_name_label)
    draw_npc_prompt(npc_prompt)
    draw_npc_description(npc_description)
    draw_npc_dialog(npc_dialog)
    if npc_label_screen:
        draw_npc_world_label(npc_name_label, npc_label_screen[0], npc_label_screen[1])

    draw_z_target_ui(z_target, z_target_type)
    draw_z_target_marker(z_target_screen)
    draw_npc_ai_telemetry()

    if admin_hub:
        fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0
        admin_hub.draw(player, enemies, npcs, fps)

    r2d.end_2d()


def preload_initial_chunks(base_cx, base_cz):
    """Pantalla de carga menos agresiva: LOD alrededor y 9 chunks detallados iniciales."""
    global mundo_chunks, mundo_chunks_simple
    lod_coords = []
    for dx in range(-RADIO_VISION, RADIO_VISION + 1):
        for dz in range(-RADIO_VISION, RADIO_VISION + 1):
            lod_coords.append((base_cx + dx, base_cz + dz))
    lod_coords.sort(key=lambda coord: (coord[0] - base_cx) ** 2 + (coord[1] - base_cz) ** 2)

    detail_coords = []
    for dx in range(-RADIO_DETALLE, RADIO_DETALLE + 1):
        for dz in range(-RADIO_DETALLE, RADIO_DETALLE + 1):
            detail_coords.append((base_cx + dx, base_cz + dz))
    detail_coords.sort(key=lambda coord: (coord[0] - base_cx) ** 2 + (coord[1] - base_cz) ** 2)

    total = len(lod_coords) + len(detail_coords)
    step_num = 0
    for coord in lod_coords:
        step_num += 1
        show_loading_screen(f"LOD alrededor {step_num}/{total}...")
        pygame.event.pump()
        if coord not in mundo_chunks_simple and coord not in mundo_chunks:
            try:
                mundo_chunks_simple[coord] = render_backend.register_gpu_handle(env.build_simple_chunk_list(coord[0], coord[1], CHUNK_SIZE, SEMILLA_MUNDO, subdivisions=SUBDIVISIONES_LOD))
            except Exception as exc:
                print(f"[PRELOAD] Error creando LOD {coord}: {exc}")

    for coord in detail_coords:
        step_num += 1
        show_loading_screen(f"Detalle 9 chunks cercanos {step_num}/{total}...")
        pygame.event.pump()
        try:
            cx, cz, q, g, r, d, w, h = env.calculate_chunk_data_background(coord[0], coord[1], CHUNK_SIZE, SUBDIVISIONES, SEMILLA_MUNDO)
            env._height_cache[(int(cx), int(cz))] = h
            agregar_rocas_de_chunk(r, cx, cz)
            agregar_recursos_de_chunk(g, d, cx, cz)
            mesh_data = env.build_chunk_mesh_data(cx, cz, q, g, r, d, w, size=CHUNK_SIZE, lod="detail", height_map=h)
            mundo_chunks[(int(cx), int(cz))] = render_backend.upload_chunk_mesh(mesh_data)
            if coord in mundo_chunks_simple:
                render_backend.release_gpu_handle(mundo_chunks_simple[coord])
                del mundo_chunks_simple[coord]
        except Exception as exc:
            print(f"[PRELOAD] Error creando detalle {coord}: {exc}")

# ------------------------------
# Inicio
# ------------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()
    engine = GameEngine(ANCHO, ALTO, f"JUEGO 1.6 - {full_update_name()}")
    render_backend = create_render_backend(os.environ.get("JUEGO_RENDER_BACKEND", "opengl"))

    menu_result = show_start_menu(engine)
    if menu_result.get("mode") == "quit":
        pygame.quit()
        raise SystemExit

    SEMILLA_MUNDO = int(menu_result.get("seed") or random.randint(1, 1000000))
    log_event("GAME_START", mode=menu_result.get("mode"), seed=SEMILLA_MUNDO, has_save=bool(menu_result.get("save_data")))
    _append_preset_session_start()
    show_loading_screen(f"Cargando semilla {SEMILLA_MUNDO}...")

    audio = AudioManager()
    player = Player(SPAWN_CENTER_X, 15.0, SPAWN_CENTER_Z, get_total_height)
    # FIX Q: permite que el movimiento sepa si el siguiente paso es agua.
    # Así la superficie del lago no se interpreta como una pared/meseta.
    player.water_probe_func = is_water_position
    loaded_save_data = menu_result.get("save_data")
    if loaded_save_data:
        log_event("LOAD_SAVE_RAW", x=loaded_save_data.get("x"), y=loaded_save_data.get("y"), z=loaded_save_data.get("z"),
                  health=loaded_save_data.get("health"), seed=loaded_save_data.get("seed"))
        apply_save_to_player(player, loaded_save_data)
        log_event("LOAD_SAVE_APPLIED", x=player.pos_x, y=player.pos_y, z=player.pos_z, health=player.health)
        safe_x, suelo, safe_z = find_safe_player_position(player.pos_x, player.pos_z, reason="continue_save")
        player.pos_x = safe_x
        player.pos_z = safe_z
        player.pos_y = suelo + player.player_height + 0.08
        player.velocity_y = 0
        player.is_grounded = True
        player._last_safe_x = player.pos_x
        player._last_safe_y = player.pos_y
        player._last_safe_z = player.pos_z
    else:
        safe_x, suelo, safe_z = find_safe_player_position(SPAWN_CENTER_X, SPAWN_CENTER_Z, reason="new_world_center_chunk")
        player.pos_x = safe_x
        player.pos_z = safe_z
        player.pos_y = suelo + player.player_height + 0.08
        player.is_grounded = True
        player._last_safe_x = player.pos_x
        player._last_safe_y = player.pos_y
        player._last_safe_z = player.pos_z
    set_player_respawn_point(player, player.pos_x, player.pos_z)
    admin_hub = AdminHub(ANCHO, ALTO)

    try:
        audio.load_music("musica_fondo.mp3")
        audio.play_music(loops=-1, volume=0.2)
    except:
        pass
    try:
        audio.load_sound_effect("golpe", "golpe.wav")
        audio.load_sound_effect("salto", "sonido_salto.wav")
    except:
        pass

    # Enemigos lejos del jugador/spawn actual.
    # FIX E: los terrestres no se generan sobre lagos/charcas.
    enemies = []
    for _ in range(2):
        x, y, z = find_dry_spawn_position(player.pos_x, player.pos_z, 60, 100)
        enemy = Enemy(x, y, z, get_total_height)
        enemy.lock_spawn_biome_color(SEMILLA_MUNDO)
        enemies.append(enemy)

    # Crear un NPC interactivo cerca del jugador/spawn actual.
    # FIX E: NPC terrestre evita nacer dentro del agua.
    npcs = []
    npc_spawn_x, npc_spawn_y, npc_spawn_z = find_dry_spawn_position(player.pos_x, player.pos_z, 5.0, 12.0)
    npc = NPC(123456, npc_spawn_x, npc_spawn_z, npc_spawn_y + 0.8)
    npc.terrain_height_func = get_total_height
    npc.wander_radius = 12.0
    npc.target_x = npc_spawn_x
    npc.target_z = npc_spawn_z
    npcs.append(npc)

    # Configurar multiproceso
    pipe_juego, pipe_worker = multiprocessing.Pipe()
    worker_process = multiprocessing.Process(
        target=env.terrain_worker_process,
        args=(pipe_worker, CHUNK_SIZE, SUBDIVISIONES, SEMILLA_MUNDO)
    )
    worker_process.daemon = True
    worker_process.start()

    print("[INICIO] Pantalla de carga: preparando chunks iniciales...")
    base_cx = player_chunk_coord(player.pos_x)
    base_cz = player_chunk_coord(player.pos_z)
    preload_initial_chunks(base_cx, base_cz)

    show_loading_screen("Listo. Entrando al mundo...")
    pygame.time.wait(250)
    print(f"[INICIO] Listo. Semilla={SEMILLA_MUNDO}. {len(enemies)} enemigos.")
    engine.run(update, render_2d, render_3d)
