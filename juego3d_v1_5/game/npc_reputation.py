# npc_ai_runtime.py

# Caché para almacenar respuestas del NPC
NPC_AI_REPLY_CACHE: Dict[tuple, str] = {}
NPC_AI_REPLY_CACHE_MAX = 96
NPC_AI_REPLY_QUEUE: List[dict] = []

# Función para añadir una entrada al caché
def add_to_cache(npc_id: str, player_text: str, response: str) -> None:
    key = (npc_id, player_text)
    NPC_AI_REPLY_CACHE[key] = response
    if len(NPC_AI_REPLY_CACHE) > NPC_AI_REPLY_CACHE_MAX:
        oldest_key = next(iter(NPC_AI_REPLY_CACHE))
        del NPC_AI_REPLY_CACHE[oldest_key]

# Función para limpiar el caché (opcional, puedes llamarla periódicamente)
def clear_cache() -> None:
    NPC_AI_REPLY_CACHE.clear()

# Actualizar la función queue_npc_ai_reply
def queue_npc_ai_reply(npc, player_text="", use_cache=True) -> str:
    global NPC_AI_REQUEST_COUNTER
    key = _npc_ai_cache_key(npc, player_text)
    if use_cache and key in NPC_AI_REPLY_CACHE:
        # Respuesta desde caché
        line = NPC_AI_REPLY_CACHE[key]
        request_id = f"cached_{NPC_AI_REQUEST_COUNTER}"
        NPC_AI_COMPLETED_REPLIES[request_id] = {"status":"ready", "reply":line, "cached":True}
        NPC_AI_REQUEST_COUNTER += 1
        return request_id

    if len(NPC_AI_REPLY_QUEUE) >= NPC_AI_QUEUE_MAX:
        return None  # cola llena

    NPC_AI_REQUEST_COUNTER += 1
    request_id = f"npc_ai_req_{NPC_AI_REQUEST_COUNTER:06d}"

    # Añadir la entrada al caché antes de enviar a la cola
    add_to_cache(npc.id, player_text, "")

    NPC_AI_REPLY_QUEUE.append({
        "request_id": request_id, "npc": npc, "player_text": player_text,
        "prompt": build_npc_dialogue_prompt(npc, player_text),
        "cache_key": key, "use_cache": use_cache
    })

    return request_id

# Bucle principal del juego
hora_global = 12  # Inicia en mediodía

while True:
    dt = ...  # Tiempo transcurrido desde la última iteración (por ejemplo, 0.01667 para 60 FPS)
    hora_global += dt / 60.0
    if hora_global >= 24:
        hora_global -= 24

    update_entities_runtime(hora_global)
    # Otros procesos del juego...

def update_entities_runtime(hora_global):
    # Actualizar entidades generales...
    update_npc_with_budget(npc_list, hora_global)

# Función que actualiza los NPCs según su presupuesto
def update_npc_with_budget(npc_list, hora_global):
    for npc in npc_list:
        # Actualizar necesidades basadas en el tiempo
        if hora_global % 24 == 0:  # Ejemplo: cada día resetea las necesidades
            npc.reset_needs()

        # Actualizar estado según la necesidad actual
        activity, description = activity_for_need(npc)
        npc.activity = activity
        npc.activity_detail = description

        # Actualizar memoria basada en acciones del jugador
        if npc.id in player_actions:
            remember_npc_event(npc, player_actions[npc.id])

        # Otras actualizaciones según tu lógica del juego...

# Función para guardar el juego
def save_game():
    game_data = {
        "npcs": [npc.to_dict() for npc in npc_list],
        # Otros datos del juego...
    }

    with open("savegame.json", "w") as f:
        json.dump(game_data, f)

# Función para cargar el juego
def load_game():
    global npc_list
    npc_list = []

    with open("savegame.json", "r") as f:
        game_data = json.load(f)

    for npc_data in game_data["npcs"]:
        npc = NPC(npc_data["id"], npc_data["x"], npc_data["y"], npc_data["z"])
        npc.from_dict(npc_data)
        npc_list.append(npc)


class NPC:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        # Otros atributos del NPC...

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            # Otros atributos del NPC...
        }

    def from_dict(self, data):
        self.id = data["id"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        # Asignar otros atributos del NPC...

    def update_needs(self):
        if self.current_need == "food":
            self.stress += 0.1
        elif self.current_need == "water":
            self.stress += 0.2
        # Otros tipos de necesidades...

# Función para actualizar la memoria del NPC y obtenerla
def test_update_and_get_memory():
    npc_id = "npc123"
    memory_update = {"trust": 90.0}

    # Actualizar la memoria del NPC
    NPC_LOCAL_MODEL_ADAPTER.update_npc_memory(npc_id, memory_update)

    # Obtener la memoria del NPC
    npc_memory = NPC_LOCAL_MODEL_ADAPTER.get_npc_memory(npc_id)

    assert npc_memory == memory_update, f"Expected {memory_update}, but got {npc_memory}"

# Ejecutar las pruebas
test_update_and_get_memory()

