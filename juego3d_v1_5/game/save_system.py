# save_system.py - Pseudocódigo para guardado completo de NPCs

def remove_and_add_hair(player_image_path: str, output_path: str) -> None:
    from PIL import Image
    
    # Abrir la imagen del personaje
    player_img = Image.open(player_image_path)
    
    # Crear una máscara negra para el pelo
    hair_mask = Image.new('L', player_img.size, color=0)  # Blanco en escala de grises (sin pelo)
    
    # Definir la región del pelo a retirar
    # Aquí puedes ajustar las coordenadas según necesites
    hair_region = (50, 100, 200, 300)  # Ejemplo: region del pelo
    
    # Aplicar la máscara al personaje
    player_img.putalpha(hair_mask)
    
    # Crear una imagen de pelo negro
    hair_image = Image.new('RGBA', player_img.size, color=(0, 0, 0, 255))  # Pelo negro
    
    # Pegar la imagen del pelo en la región definida
    player_img.paste(hair_image, hair_region, mask=hair_image)
    
    # Guardar la imagen modificada
    player_img.save(output_path)

# Función para guardar el juego completo (jugador + NPCs + memoria)
def save_game(player, npcs: List, seed: int = 1) -> Dict:
    """
    Guarda el estado del jugador, todos los NPCs y la memoria persistente.
    Retorna el diccionario guardado.
    """
    _ensure_save_dir()
    
    # Aplicar el cambio de pelo al personaje principal
    remove_and_add_hair('player.png', 'modified_player.png')
    
    # Continuar con el resto del código para guardar el juego
    player_data = {
        "x": player.pos_x,
        "y": player.pos_y,
        "z": player.pos_z,
        "yaw": player.yaw,
        "pitch": player.pitch,
        "camera_mode": player.camera_mode,
        "third_person_distance": player.third_person_distance,
        "health": player.health,
        "hunger": player.hunger,
        "stamina": player.stamina,
        "bag_name": player.bag_name,
        "bag_capacity": player.bag_capacity,
        "collected_empty_bag_keys": list(player.collected_empty_bag_keys),
        "inventory": player.normalize_inventory(),
        "active_weapon": player.active_weapon,
        "respawn_x": player.respawn_x,
        "respawn_z": player.respawn_z,
    }
    
    npcs_data = []
    for npc in npcs:
        rutina_serializable = {str(h): (accion, destino) for h, (accion, destino) in npc.rutina_dia.items()}
        npc_record = {
            "id_unico": npc.id,
            "nombre": npc.nombre,
            "titulo": npc.titulo,
            "apodo": getattr(npc, "apodo", ""),
            "profession": npc.profession,
            "seed": npc.seed,
            "skin_preset": npc.skin_preset,
            "cultura": getattr(npc, "cultura", "neutral"),
            "rango": getattr(npc, "rango", "aldeano"),
            "x": npc.x,
            "y": npc.y,
            "z": npc.z,
            "spawn_x": npc.spawn_x,
            "spawn_z": npc.spawn_z,
            "yaw": npc.yaw,
            "health": npc.health,
            "needs": dict(npc.needs),
            "stress": npc.stress,
            "current_need": npc.current_need,
            "intent": npc.intent,
            "activity": npc.activity,
            "activity_detail": npc.activity_detail,
            "activity_progress": npc.activity_progress,
            "memoria": npc.memoria,
            "pistas": getattr(npc, "pistas", {}),
            "rutina_dia": rutina_serializable,
            "rutina_noche": getattr(npc, "rutina_noche", {}),
            "work_anchor": list(npc.work_anchor),
            "rest_anchor": list(npc.rest_anchor),
            "social_anchor": list(npc.social_anchor),
            "tool_label": npc.tool_label,
            "workplace": npc.workplace,
            "work_material": npc.work_material,
            "work_action": npc.work_action,
            "temper": npc.temper,
            "identity_key": npc.identity_key,
            "back_tool": npc.back_tool,
        }
        npcs_data.append(npc_record)
    
    from game.npc_memory import export_npc_memory
    memory_data = export_npc_memory()
    
    save_data = {
        "version": SAVE_VERSION,
        "seed": seed,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "player": player_data,
        "npcs": npcs_data,
        "npc_memory": memory_data,
    }
    
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    from game.debug_log import log_event
    log_event("SAVE_GAME", npc_count=len(npcs_data))
    return save_data

# Carga y reconstrucción completa
def load_game_data() -> Optional[Dict]:
    """
    Carga el archivo de guardado y retorna el diccionario completo.
    No aplica nada todavía, solo lee.
    """
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != SAVE_VERSION:
            print(f"[WARN] Versión de guardado diferente: {data.get('version')} -> se intentará migrar")
            return data
    except Exception as e:
        from game.debug_log import log_exception
        log_exception("LOAD_SAVE_ERROR", e)
        return None

def load_npcs_from_save(save_data: Dict, terrain_func: Callable, NPC_class) -> List:
    npcs_data = save_data.get("npcs", [])
    restored_npcs = []
    for npc_record in npcs_data:
        seed = npc_record["seed"]
        x = npc_record["x"]
        z = npc_record["z"]
        y = npc_record["y"]
        npc_id = npc_record["id_unico"]
        try:
            npc = NPC_class(seed, x, z, y, id_source="save", id_slot=0, npc_id=npc_id)
        except TypeError:
            npc = NPC_class(seed, x, z, y, id_source="save", id_slot=0)
            npc.id = npc_id
        npc.nombre = npc_record["nombre"]
        npc.titulo = npc_record["titulo"]
        npc.apodo = npc_record.get("apodo", "")
        npc.profession = npc_record["profession"]
        npc.skin_preset = npc_record["skin_preset"]
        npc.cultura = npc_record.get("cultura", "neutral")
        npc.rango = npc_record.get("rango", "aldeano")
        npc.x = npc_record["x"]
        npc.y = npc_record["y"]
        npc.z = npc_record["z"]
        npc.spawn_x = npc_record["spawn_x"]
        npc.spawn_z = npc_record["spawn_z"]
        npc.yaw = npc_record["yaw"]
        npc.health = npc_record["health"]
        npc.needs = npc_record["needs"]
        npc.stress = npc_record["stress"]
        npc.current_need = npc_record["current_need"]
        npc.intent = npc_record["intent"]
        npc.activity = npc_record["activity"]
        npc.activity_detail = npc_record["activity_detail"]
        npc.activity_progress = npc_record["activity_progress"]
        npc.memoria = npc_record["memoria"]
        if hasattr(npc, "pistas"):
            npc.pistas = npc_record.get("pistas", {})
        rutina_dia = {}
        for h_str, (accion, destino) in npc_record.get("rutina_dia", {}).items():
            rutina_dia[int(h_str)] = (accion, tuple(destino))
        npc.rutina_dia = rutina_dia
        npc.rutina_noche = npc_record.get("rutina_noche", {})
        npc.work_anchor = tuple(npc_record["work_anchor"])
        npc.rest_anchor = tuple(npc_record["rest_anchor"])
        npc.social_anchor = tuple(npc_record["social_anchor"])
        npc.tool_label = npc_record["tool_label"]
        npc.workplace = npc_record["workplace"]
        npc.work_material = npc_record["work_material"]
        npc.work_action = npc_record["work_action"]
        npc.temper = npc_record["temper"]
        npc.identity_key = npc_record["identity_key"]
        npc.back_tool = npc_record["back_tool"]
        npc.terrain_height_func = terrain_func
        npc.memory = npc_memory_for(npc)
        restored_npcs.append(npc)
    return restored_npcs

def apply_save_to_player(player, save_data: Dict) -> bool:
    player_data = save_data.get("player")
    if not player_data:
        return False
    player.pos_x = player_data["x"]
    player.pos_y = player_data["y"]
    player.pos_z = player_data["z"]
    player.yaw = player_data["yaw"]
    player.pitch = player_data["pitch"]
    player.camera_mode = player_data["camera_mode"]
    player.third_person_distance = player_data["third_person_distance"]
    player.health = player_data["health"]
    player.hunger = player_data["hunger"]
    player.stamina = player_data["stamina"]
    player.bag_name = player_data["bag_name"]
    player.bag_capacity = player_data["bag_capacity"]
    player.collected_empty_bag_keys = set(player_data["collected_empty_bag_keys"])
    player.inventory = player_data["inventory"]
    player.active_weapon = player_data["active_weapon"]
    player.respawn_x = player_data.get("respawn_x", player.pos_x)
    player.respawn_z = player_data.get("respawn_z", player.pos_z)
    if hasattr(player, "normalize_inventory"):
        player.normalize_inventory()
    if hasattr(player, "normalize_active_weapon"):
        player.normalize_active_weapon()
    from game.debug_log import log_event
    log_event("PLAYER_LOADED", x=player.pos_x, z=player.pos_z)
    return True

def load_game(player, terrain_func, NPC_class) -> bool:
    save_data = load_game_data()
    if not save_data:
        print("No se encontró partida guardada")
        return False
    memory_loaded = import_npc_memory(save_data.get("npc_memory"), merge=True)
    apply_save_to_player(player, save_data)
    npcs = load_npcs_from_save(save_data, terrain_func, NPC_class)
    from game.debug_log import log_event
    log_event("GAME_LOADED", npc_count=len(npcs))
    return True, npcs

# Migración de versiones antiguas (opcional)
def _migrate_v1_to_v2(old_data: Dict) -> Dict:
    new_data = {
        "version": SAVE_VERSION,
        "seed": old_data.get("seed", 1),
        "saved_at": old_data.get("saved_at", time.strftime("%Y-%m-%d %H:%M:%S")),
        "player": {
            "x": old_data.get("x", 0),
            "y": old_data.get("y", 0),
            "z": old_data.get("z", 0),
            "yaw": old_data.get("yaw", -90),
            "pitch": old_data.get("pitch", 0),
            "camera_mode": old_data.get("camera_mode", "first"),
            "third_person_distance": old_data.get("third_person_distance", 5.5),
            "health": old_data.get("health", 100),
            "hunger": old_data.get("hunger", 100),
            "stamina": old_data.get("stamina", 100),
            "bag_name": old_data.get("bag_name", "mochila basica"),
            "bag_capacity": old_data.get("bag_capacity", 18),
            "collected_empty_bag_keys": list(old_data.get("collected_empty_bag_keys", [])),
            "inventory": old_data.get("inventory", {}),
            "active_weapon": old_data.get("active_weapon", None),
            "respawn_x": old_data.get("respawn_x", 0),
            "respawn_z": old_data.get("respawn_z", 0),
        },
        "npcs": [],
        "npc_memory": old_data.get("npc_memory", {"version": "v1", "records": []}),
    }
    return new_data

# Ejemplo de integración en el bucle principal
def ejemplo_integracion():
    if has_save():
        success, npcs_cargados = load_game(player, terrain_func, NPC)
        if success:
            game_npcs = npcs_cargados
        else:
            game_npcs = generar_npcs_por_chunks()
