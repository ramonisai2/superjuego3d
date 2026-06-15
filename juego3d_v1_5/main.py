from motor_juegos import GameEngine, AudioManager, r3d, r2d, env
from motor_juegos.render_backend import create_render_backend
import os
from motor_juegos.frame_graph import RenderFrameGraph
from motor_juegos.runtime_perf import perf_tracker
import pygame
import random
import math
import multiprocessing
from motor_juegos.render_mode_status import print_render_mode_banner
from motor_juegos.version_info import full_update_name
print_render_mode_banner("main.py startup")

from game.player import Player
from game.enemy import Enemy, SlimeRemnant
from game.projectiles import entity_alive
from game.npc_manager import NPC
from game.ui import draw_ui, draw_world_context, draw_npc_label, draw_npc_prompt, draw_npc_description, draw_npc_dialog, draw_npc_world_label, draw_z_target_ui, draw_z_target_marker, draw_npc_ai_telemetry, draw_pickup_notices, draw_combat_notices, draw_fps_counter, draw_adaptive_quality
from game.save_system import apply_save_to_player
from game.admin_hub import AdminHub
from game.debug_log import log_event, log_exception, log_throttled
from main_config import *
from main_adaptive_quality import AdaptiveQualityRuntime
from main_resources import WorldResourceRuntime
from main_preset_logging import append_preset_session_start, update_runtime_logs, world_detail_debug_status
from main_spawn import SpawnRuntime
from main_hud_render import render_runtime_hud
from main_world_runtime import WorldRuntime
from main_render3d import render_runtime_3d
from main_screens import show_loading_screen as draw_loading_screen, show_start_menu as run_start_menu
from main_preload import preload_initial_chunks
from main_save_runtime import handle_save_hotkeys
from main_entity_runtime import handle_npc_interaction, update_entities_runtime
from main_combat_runtime import update_combat_runtime
from main_chunk_runtime import MainChunkRuntime

# ------------------------------
# Constantes
# ------------------------------
# Importadas desde main_config.py para mantener main.py mas pequeno.

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
pipe_juego = None
worker_process = None
chunk_runtime = None
mundo_chunks = {}
mundo_chunks_simple = {}
cola_de_peticiones = []
cola_lod_peticiones = []
chunks_pendientes = {}
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
    "fps_now": 0.0,
    "low_time": 0.0,
    "high_time": 0.0,
    "frame_index": 0,
    "rescue_level": 0,
    "rescue_label": "OK",
}
adaptive_streaming = {
    "enabled": ADAPTIVE_STREAMING_ENABLED,
    "interval": 0.05,
    "lod_limit": int(LODS_CREAR_POR_TANDA),
    "forced": 0,
}
adaptive_runtime = AdaptiveQualityRuntime(
    adaptive_quality,
    chunk_size=CHUNK_SIZE,
    radio_vision=RADIO_VISION,
    radio_detalle=RADIO_DETALLE,
    chunk_render_extra=CHUNK_RENDER_EXTRA,
    chunk_render_min_extra=CHUNK_RENDER_MIN_EXTRA,
    detail_chunk_render_extra=DETAIL_CHUNK_RENDER_EXTRA,
    entity_full_detail_distance=ENTITY_FULL_DETAIL_DISTANCE,
    entity_mid_detail_distance=ENTITY_MID_DETAIL_DISTANCE,
    lods_crear_por_tanda=LODS_CREAR_POR_TANDA,
    fps_low=ADAPTIVE_FPS_LOW,
    fps_high=ADAPTIVE_FPS_HIGH,
    adaptive_chunk_render_enabled=ADAPTIVE_CHUNK_RENDER_ENABLED,
    adaptive_streaming_enabled=ADAPTIVE_STREAMING_ENABLED,
    frame_rescue_enabled=ADAPTIVE_RESCUE_ENABLED,
    rescue_fps=ADAPTIVE_RESCUE_FPS,
    emergency_fps=ADAPTIVE_EMERGENCY_FPS,
)
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

# ------------------------------
# Funciones auxiliares
# ------------------------------


def player_chunk_coord(pos):
    return world_runtime.player_chunk_coord(pos)

def get_terrain_only(x, z):
    return world_runtime.get_terrain_only(x, z)

def get_water_surface_cached(x, z):
    """Consulta estable de agua con cache espacial para movimiento/IA."""
    return world_runtime.get_water_surface_cached(x, z)

def clear_total_height_query_cache():
    world_runtime.clear_total_height_query_cache()

def begin_total_height_query_frame():
    world_runtime.begin_total_height_query_frame()

def _total_height_cache_key(x, z):
    return world_runtime._total_height_cache_key(x, z)

def get_total_height(x, z):
    return world_runtime.get_total_height(x, z)


def is_water_position(x, z):
    """True si el punto cae dentro de agua visible; se usa para evitar spawns terrestres en lagos."""
    return world_runtime.is_water_position(x, z)


def update_player_world_context(dt):
    """Actualiza HUD de zona y modo nado/flotacion."""
    world_runtime.update_player_world_context(player, dt)

spawn_runtime = SpawnRuntime(
    seed=SEMILLA_MUNDO,
    get_total_height=get_total_height,
    is_water_position=is_water_position,
    log_event=log_event,
    log_exception=log_exception,
)


def _entity_distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz


def _resource_amount_for_world_detail(kind):
    """Compensa presets bajos: menos piezas visuales, recursos por nodo mas generosos."""
    try:
        status = env.get_world_detail_density_status()
    except Exception:
        return 1
    reference = {
        "fibra": ("grass", env.GRASS_DENSITY),
        "madera": ("deco", env.DECO_DENSITY),
        "piedra": ("rock", env.ROCK_DENSITY),
    }.get(str(kind))
    if not reference:
        return 1
    density_key, balanced_value = reference
    current_value = max(0.05, float(status.get(density_key, balanced_value) or balanced_value))
    return max(1, min(4, int(math.ceil(float(balanced_value) / current_value))))

resource_runtime = WorldResourceRuntime(
    resource_cell_size=RESOURCE_CELL_SIZE,
    rock_collision_cell_size=ROCK_COLLISION_CELL_SIZE,
    resource_amount_func=_resource_amount_for_world_detail,
    clear_height_cache=clear_total_height_query_cache,
)
world_runtime = WorldRuntime(
    env=env,
    resource_runtime=resource_runtime,
    seed=SEMILLA_MUNDO,
    chunk_size=CHUNK_SIZE,
    subdivisions=SUBDIVISIONES,
    water_query_grid=WATER_QUERY_GRID,
    total_height_query_grid=TOTAL_HEIGHT_QUERY_GRID,
    world_context_interval=WORLD_CONTEXT_INTERVAL,
    world_context_move_step=WORLD_CONTEXT_MOVE_STEP,
    log_event=log_event,
    log_exception=log_exception,
    log_throttled=log_throttled,
)

def _entity_alive(entity):
    return entity_alive(entity)


# ------------------------------
# Bucle principal
# ------------------------------
def update(dt):
    global tiempo_log, tiempo_chunks, target_fov, current_fov, last_attack_time, enemies, admin_hub, z_target, z_target_type, slime_remnants, stone_projectiles
    begin_total_height_query_frame()
    engine.handle_events()
    adaptive_runtime.update(dt, engine)
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
    player.is_sprinting = bool(update.is_sprinting and norm > 0.001)

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
            resource_runtime.try_gather_basic_resource(player, current_time, log_throttled)
        update.last_resource_gather = current_time

    px, py, pz, _, _, _ = player.get_camera_vectors()
    chunk_actual_x = player_chunk_coord(px)
    chunk_actual_z = player_chunk_coord(pz)

    # Gestión de chunks (cada 50 ms)
    stream_interval = adaptive_runtime.stream_interval()
    lod_limit = adaptive_runtime.lod_limit()
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
                chunk_runtime.administrar_rejilla_chunks(chunk_actual_x, chunk_actual_z, dx_move, dz_move)
            with perf_tracker.measure("chunk_lod"):
                chunk_runtime.procesar_lods_pendientes(chunk_actual_x, chunk_actual_z, limit_override=lod_limit)
            with perf_tracker.measure("chunk_comm"):
                chunk_runtime.procesar_comunicacion_multiproceso()
            with perf_tracker.measure("chunk_compile"):
                for _ in range(CHUNKS_COMPILAR_POR_FRAME):
                    if not chunk_runtime.compilar_un_chunk_pendiente(player):
                        break

    combat_state = update_combat_runtime(
        current_time=current_time,
        dt=dt,
        player=player,
        enemies=enemies,
        npcs=npcs,
        stone_projectiles=stone_projectiles,
        z_target=z_target,
        z_target_type=z_target_type,
        last_attack_time=last_attack_time,
        attack_cooldown=attack_cooldown,
        audio=audio,
        get_total_height=get_total_height,
        entity_alive=_entity_alive,
        distance_sq_func=_entity_distance_sq_2d,
        px=px,
        pz=pz,
    )
    stone_projectiles = combat_state["stone_projectiles"]
    z_target = combat_state["z_target"]
    z_target_type = combat_state["z_target_type"]
    last_attack_time = combat_state["last_attack_time"]

    # Interacción con NPCs
    global npc_dialog, npc_prompt, npc_name_label, npc_description, last_interact_time
    global npc_label_screen
    interaction = handle_npc_interaction(
        keys,
        current_time,
        px,
        pz,
        npcs,
        last_interact_time,
        _entity_distance_sq_2d,
    )
    npc_prompt = interaction["prompt"]
    npc_name_label = interaction["name_label"]
    npc_description = interaction["description"]
    npc_label_screen = interaction["label_screen"]
    last_interact_time = interaction["last_interact_time"]
    if interaction["dialog"] is not None:
        npc_dialog = interaction["dialog"]

    # Actualizar entidades. El Admin Hub puede pausar la IA.
    update_entities_runtime(
        dt=dt,
        px=px,
        pz=pz,
        player=player,
        npcs=npcs,
        enemies=enemies,
        slime_remnants=slime_remnants,
        admin_hub=admin_hub,
        perf_tracker=perf_tracker,
        npc_full_ai_distance=NPC_FULL_AI_DISTANCE,
        npc_far_ai_interval=NPC_FAR_AI_INTERVAL,
        enemy_full_ai_distance=ENEMY_FULL_AI_DISTANCE,
        enemy_far_ai_interval=ENEMY_FAR_AI_INTERVAL,
    )

    handle_save_hotkeys(keys, player, SEMILLA_MUNDO, spawn_runtime, log_event)

    tiempo_log, update.preset_sample_accum = update_runtime_logs(
        dt,
        tiempo_log,
        float(getattr(update, "preset_sample_accum", 0.0)),
        current_fov=current_fov,
        chunk_actual_x=chunk_actual_x,
        chunk_actual_z=chunk_actual_z,
        player=player,
        enemies=enemies,
        enable_stream_bridge=ENABLE_STREAM_BRIDGE_SAFE,
        stream_bridge_stats=stream_bridge_stats,
        preset_sample_log_enabled=PRESET_SAMPLE_LOG_ENABLED,
        preset_sample_log_interval=PRESET_SAMPLE_LOG_INTERVAL,
        preset_sample_session=PRESET_SAMPLE_SESSION,
        engine=engine,
        env=env,
        resource_amount_func=_resource_amount_for_world_detail,
        adaptive_quality=adaptive_quality,
        adaptive_streaming=adaptive_streaming,
        render_stats=render_stats,
        chunk_render_extra=CHUNK_RENDER_EXTRA,
        detail_chunk_back_margin=DETAIL_CHUNK_BACK_MARGIN,
    )

def render_3d():
    global z_target_screen, render_stats, npc_label_screen
    render_stats, z_target_screen, npc_label_screen = render_runtime_3d(
        current_fov=current_fov,
        ancho=ANCHO,
        alto=ALTO,
        r3d=r3d,
        env=env,
        render_backend=render_backend,
        render_graph=render_graph,
        perf_tracker=perf_tracker,
        stream_bridge_stats=stream_bridge_stats,
        adaptive_quality=adaptive_quality,
        adaptive_runtime=adaptive_runtime,
        adaptive_streaming=adaptive_streaming,
        world_detail_debug_status=world_detail_debug_status,
        resource_amount_func=_resource_amount_for_world_detail,
        resource_runtime=resource_runtime,
        player=player,
        enemies=enemies,
        npcs=npcs,
        slime_remnants=slime_remnants,
        stone_projectiles=stone_projectiles,
        admin_hub=admin_hub,
        z_target=z_target,
        z_target_type=z_target_type,
        mundo_chunks_simple=mundo_chunks_simple,
        mundo_chunks=mundo_chunks,
        debug_render_all_chunks=DEBUG_RENDER_ALL_CHUNKS,
        debug_render_all_entities=DEBUG_RENDER_ALL_ENTITIES,
        chunk_size=CHUNK_SIZE,
        detail_chunk_near_keep=DETAIL_CHUNK_NEAR_KEEP,
        detail_chunk_back_margin=DETAIL_CHUNK_BACK_MARGIN,
        chunk_render_extra=CHUNK_RENDER_EXTRA,
        chunk_render_min_extra=CHUNK_RENDER_MIN_EXTRA,
        lods_crear_por_tanda=LODS_CREAR_POR_TANDA,
        remnant_render_distance=REMNANT_RENDER_DISTANCE,
        entity_render_distance=ENTITY_RENDER_DISTANCE,
        entity_label_distance=ENTITY_LABEL_DISTANCE,
        seed=SEMILLA_MUNDO,
    )

def render_2d():
    render_runtime_hud(
        r2d=r2d,
        ancho=ANCHO,
        alto=ALTO,
        engine=engine,
        player=player,
        enemies=enemies,
        npcs=npcs,
        admin_hub=admin_hub,
        render_stats=render_stats,
        adaptive_quality=adaptive_quality,
        npc_name_label=npc_name_label,
        npc_prompt=npc_prompt,
        npc_description=npc_description,
        npc_dialog=npc_dialog,
        npc_label_screen=npc_label_screen,
        z_target=z_target,
        z_target_type=z_target_type,
        z_target_screen=z_target_screen,
        draw_ui=draw_ui,
        draw_pickup_notices=draw_pickup_notices,
        draw_combat_notices=draw_combat_notices,
        draw_world_context=draw_world_context,
        draw_adaptive_quality=draw_adaptive_quality,
        draw_fps_counter=draw_fps_counter,
        draw_npc_label=draw_npc_label,
        draw_npc_prompt=draw_npc_prompt,
        draw_npc_description=draw_npc_description,
        draw_npc_dialog=draw_npc_dialog,
        draw_npc_world_label=draw_npc_world_label,
        draw_z_target_ui=draw_z_target_ui,
        draw_z_target_marker=draw_z_target_marker,
        draw_npc_ai_telemetry=draw_npc_ai_telemetry,
    )

# ------------------------------
# Inicio
# ------------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()
    engine = GameEngine(ANCHO, ALTO, f"JUEGO 1.6 - {full_update_name()}")
    render_backend = create_render_backend(os.environ.get("JUEGO_RENDER_BACKEND", "opengl"))

    menu_result = run_start_menu(engine, render_backend, r2d, ANCHO, ALTO)
    if menu_result.get("mode") == "quit":
        pygame.quit()
        raise SystemExit

    SEMILLA_MUNDO = int(menu_result.get("seed") or random.randint(1, 1000000))
    world_runtime.seed = SEMILLA_MUNDO
    world_runtime.water_surface_cache.clear()
    world_runtime.clear_total_height_query_cache()
    spawn_runtime.seed = SEMILLA_MUNDO
    log_event("GAME_START", mode=menu_result.get("mode"), seed=SEMILLA_MUNDO, has_save=bool(menu_result.get("save_data")))
    append_preset_session_start(enabled=PRESET_SAMPLE_LOG_ENABLED, session=PRESET_SAMPLE_SESSION, env=env)
    draw_loading_screen(engine, render_backend, r2d, ANCHO, ALTO, f"Cargando semilla {SEMILLA_MUNDO}...")

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
        safe_x, suelo, safe_z = spawn_runtime.find_safe_player_position(player.pos_x, player.pos_z, reason="continue_save")
        player.pos_x = safe_x
        player.pos_z = safe_z
        player.pos_y = suelo + player.player_height + 0.08
        player.velocity_y = 0
        player.is_grounded = True
        player._last_safe_x = player.pos_x
        player._last_safe_y = player.pos_y
        player._last_safe_z = player.pos_z
    else:
        safe_x, suelo, safe_z = spawn_runtime.find_safe_player_position(SPAWN_CENTER_X, SPAWN_CENTER_Z, reason="new_world_center_chunk")
        player.pos_x = safe_x
        player.pos_z = safe_z
        player.pos_y = suelo + player.player_height + 0.08
        player.is_grounded = True
        player._last_safe_x = player.pos_x
        player._last_safe_y = player.pos_y
        player._last_safe_z = player.pos_z
    spawn_runtime.set_player_respawn_point(player, player.pos_x, player.pos_z)
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
        x, y, z = spawn_runtime.find_dry_position(player.pos_x, player.pos_z, 60, 100)
        enemy = Enemy(x, y, z, get_total_height)
        enemy.lock_spawn_biome_color(SEMILLA_MUNDO)
        enemies.append(enemy)

    # Crear un NPC interactivo cerca del jugador/spawn actual.
    # FIX E: NPC terrestre evita nacer dentro del agua.
    npcs = []
    npc_spawn_x, npc_spawn_y, npc_spawn_z = spawn_runtime.find_dry_position(player.pos_x, player.pos_z, 5.0, 12.0)
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
    chunk_runtime = MainChunkRuntime(
        env=env,
        render_backend=render_backend,
        resource_runtime=resource_runtime,
        stream_bridge_stats=stream_bridge_stats,
        mundo_chunks=mundo_chunks,
        mundo_chunks_simple=mundo_chunks_simple,
        cola_de_peticiones=cola_de_peticiones,
        cola_lod_peticiones=cola_lod_peticiones,
        chunks_pendientes=chunks_pendientes,
        pipe_juego=pipe_juego,
        chunk_size=CHUNK_SIZE,
        seed=SEMILLA_MUNDO,
        subdivisions_lod=SUBDIVISIONES_LOD,
        lods_crear_por_tanda=LODS_CREAR_POR_TANDA,
        radio_detalle=RADIO_DETALLE,
        radio_vision=RADIO_VISION,
        max_cola_peticiones=MAX_COLA_PETICIONES,
        enable_stream_bridge_safe=ENABLE_STREAM_BRIDGE_SAFE,
        chunks_compilar_por_frame=CHUNKS_COMPILAR_POR_FRAME,
    )

    print("[INICIO] Pantalla de carga: preparando chunks iniciales...")
    base_cx = player_chunk_coord(player.pos_x)
    base_cz = player_chunk_coord(player.pos_z)
    preload_initial_chunks(
        base_cx,
        base_cz,
        mundo_chunks=mundo_chunks,
        mundo_chunks_simple=mundo_chunks_simple,
        draw_loading_screen=draw_loading_screen,
        engine=engine,
        render_backend=render_backend,
        r2d=r2d,
        ancho=ANCHO,
        alto=ALTO,
        env=env,
        resource_runtime=resource_runtime,
        chunk_size=CHUNK_SIZE,
        seed=SEMILLA_MUNDO,
        subdivisions=SUBDIVISIONES,
        subdivisions_lod=SUBDIVISIONES_LOD,
        radio_vision=RADIO_VISION,
        radio_detalle=RADIO_DETALLE,
    )

    draw_loading_screen(engine, render_backend, r2d, ANCHO, ALTO, "Listo. Entrando al mundo...")
    pygame.time.wait(250)
    print(f"[INICIO] Listo. Semilla={SEMILLA_MUNDO}. {len(enemies)} enemigos.")
    engine.run(update, render_2d, render_3d)
