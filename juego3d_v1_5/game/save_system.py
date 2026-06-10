import json
import os
import time
try:
    from game.debug_log import log_event, log_exception
except Exception:
    def log_event(*args, **kwargs): pass
    def log_exception(*args, **kwargs): pass
try:
    from game.npc_manager import export_npc_memory, import_npc_memory
except Exception:
    def export_npc_memory():
        return {"version": "unavailable", "records": []}
    def import_npc_memory(*args, **kwargs):
        return 0

SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "world_save.json")


def _ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def has_save():
    return os.path.exists(SAVE_FILE)


def get_save_summary():
    try:
        data = load_game_data()
        if not data:
            return None
        return {
            "seed": data.get("seed", 1),
            "x": data.get("x", 0.0),
            "y": data.get("y", 0.0),
            "z": data.get("z", 0.0),
            "saved_at": data.get("saved_at", "desconocido"),
            "npc_memory_records": len((data.get("npc_memory") or {}).get("records", [])),
        }
    except Exception:
        return None


def save_game(player, seed=1):
    _ensure_save_dir()
    data = {
        "version": "stage35_l_save_world_memory",
        "seed": int(seed),
        "x": float(player.pos_x),
        "y": float(player.pos_y),
        "z": float(player.pos_z),
        "yaw": float(getattr(player, "yaw", -90.0)),
        "pitch": float(getattr(player, "pitch", 0.0)),
        "camera_mode": getattr(player, "camera_mode", "first"),
        "third_person_distance": float(getattr(player, "third_person_distance", 5.5)),
        "health": float(player.health),
        "hunger": float(player.hunger),
        "stamina": float(player.stamina),
        "bag_name": getattr(player, "bag_name", "mochila basica"),
        "bag_capacity": int(getattr(player, "bag_capacity", 18)),
        "inventory": player.normalize_inventory() if hasattr(player, "normalize_inventory") else player.inventory,
        "active_weapon": getattr(player, "active_weapon", None),
        "npc_memory": export_npc_memory(),
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log_event("SAVE_WRITE", file=SAVE_FILE, seed=seed, x=player.pos_x, y=player.pos_y, z=player.pos_z,
              health=player.health, respawn_x=getattr(player, "respawn_x", None), respawn_z=getattr(player, "respawn_z", None))
    return data


def load_game_data():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        memory_count = import_npc_memory(data.get("npc_memory"), merge=True)
        log_event("SAVE_READ", file=SAVE_FILE, seed=data.get("seed"), x=data.get("x"), y=data.get("y"), z=data.get("z"), health=data.get("health"))
        if memory_count:
            log_event("NPC_MEMORY_LOAD", records=memory_count)
        return data
    except FileNotFoundError:
        return None
    except Exception as exc:
        print(f"[LOAD] No se pudo leer la partida: {exc}")
        log_exception("SAVE_READ_ERROR", exc)
        return None


def apply_save_to_player(player, data):
    if not data:
        return False
    player.pos_x = float(data.get("x", player.pos_x))
    player.pos_y = float(data.get("y", player.pos_y))
    player.pos_z = float(data.get("z", player.pos_z))
    player.yaw = float(data.get("yaw", getattr(player, "yaw", -90.0)))
    player.pitch = float(data.get("pitch", getattr(player, "pitch", 0.0)))
    player.camera_mode = data.get("camera_mode", getattr(player, "camera_mode", "first"))
    player.third_person_distance = float(data.get("third_person_distance", getattr(player, "third_person_distance", 5.5)))
    player.health = float(data.get("health", player.health))
    player.hunger = float(data.get("hunger", player.hunger))
    player.stamina = float(data.get("stamina", player.stamina))
    player.bag_name = str(data.get("bag_name", getattr(player, "bag_name", "mochila basica")))
    player.bag_capacity = int(data.get("bag_capacity", getattr(player, "bag_capacity", 18)))
    player.inventory = data.get("inventory", player.inventory)
    if hasattr(player, "normalize_inventory"):
        player.normalize_inventory()
    player.active_weapon = data.get("active_weapon", getattr(player, "active_weapon", None))
    if hasattr(player, "normalize_active_weapon"):
        player.normalize_active_weapon()
    player.velocity_y = 0
    log_event("SAVE_APPLY_TO_PLAYER", x=player.pos_x, y=player.pos_y, z=player.pos_z, health=player.health)
    return True


def load_game(player):
    data = load_game_data()
    if not data:
        print("No se encontró partida guardada")
        return False
    return apply_save_to_player(player, data)
