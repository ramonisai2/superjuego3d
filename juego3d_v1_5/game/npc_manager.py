
import json
import math
import os
import random
import subprocess
import time

FIRST_NAMES = ["Roy","Bolvo","Runia","Tergul","Aldor","Rokkan","Mork"]
TITLES = ["El Calvo","Rompepiedras","El Ocupado","El Errante"]
HUMAN_PROFESSIONS = [
    "carpintero",
    "herrero",
    "granjero",
    "cazador",
    "minero",
    "mercader",
    "guardia",
    "curandero",
]
NPC_MEMORY_REGISTRY = {}
NPC_MEMORY_MAX_NOTES = 8
NPC_AI_REPLY_CACHE = {}
NPC_AI_REPLY_CACHE_MAX = 96
NPC_AI_REPLY_MAX_CHARS = 240
NPC_AI_REPLY_QUEUE = []
NPC_AI_COMPLETED_REPLIES = {}
NPC_AI_QUEUE_MAX = 32
NPC_AI_QUEUE_DRAIN_MAX = 1
NPC_AI_REQUEST_COUNTER = 0
NPC_LOCAL_AI_CONFIG_FILENAME = "npc_local_ai_config.json"
NPC_AI_TELEMETRY = {
    "requests": 0,
    "backend_replies": 0,
    "fallback_replies": 0,
    "cache_hits": 0,
    "queue_rejected": 0,
    "errors": 0,
    "total_ms": 0.0,
    "max_ms": 0.0,
    "last_ms": 0.0,
    "last_source": "none",
    "last_error": None,
}

def _stable_digest(*parts):
    text = "|".join(str(p) for p in parts)
    value = 1469598103934665603
    for ch in text:
        value ^= ord(ch)
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"

def _coord_key(value):
    return int(round(float(value) * 100.0))

def build_npc_id(seed, x=0, z=0, source="world", slot=0):
    source_key = str(source).replace(":", "_").replace(" ", "_")
    digest = _stable_digest("npc", int(seed), _coord_key(x), _coord_key(z), source_key, int(slot))
    return f"npc_{source_key}_{digest[:12]}"

def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))

SKIN_ZONE_PRESETS = {
    "base": {
        "head": None,
        "torso": None,
        "pants": None,
        "visual_profession": None,
        "face_type": "neutral",
        "torso_type": "neutral",
        "nose_style": "human",
        "ear_style": "human",
    },
    "carpintero_viejo": {
        "head": "carpintero_viejo",
        "torso": "carpintero_viejo",
        "pants": "carpintero_viejo",
        "visual_profession": "carpintero",
        "face_type": "masculino",
        "torso_type": "masculino",
        "nose_style": "human",
        "ear_style": "human",
    },
    "ropa_carpintero": {
        "head": None,
        "torso": "carpintero_viejo",
        "pants": "carpintero_viejo",
        "visual_profession": "carpintero",
        "face_type": "neutral",
        "torso_type": "masculino",
        "nose_style": "human",
        "ear_style": "human",
    },
}

HUMAN_PROFESSION_PROFILES = {
    "carpintero": {
        "skin": "humano_carpintero_joven",
        "color": (0.42, 0.25, 0.12),
        "shape": "sturdy",
        "tool": "hammer_reserved",
        "tool_label": "martillo",
        "workplace": "taller",
        "material": "madera",
        "action": "reparar estructuras",
        "temper": "practico",
    },
    "herrero": {
        "skin": "humano_herrero",
        "color": (0.30, 0.31, 0.32),
        "shape": "broad",
        "tool": "hammer_reserved",
        "tool_label": "martillo de forja",
        "workplace": "forja",
        "material": "metal",
        "action": "mantener herramientas",
        "temper": "duro",
    },
    "granjero": {
        "skin": "humano_granjero",
        "color": (0.34, 0.48, 0.18),
        "shape": "standard",
        "tool": "hoe_reserved",
        "tool_label": "azada",
        "workplace": "cultivo",
        "material": "semillas",
        "action": "cuidar comida",
        "temper": "paciente",
    },
    "cazador": {
        "skin": "humano_cazador",
        "color": (0.16, 0.35, 0.18),
        "shape": "slim",
        "tool": "bow_reserved",
        "tool_label": "arco",
        "workplace": "bosque",
        "material": "pieles",
        "action": "rastrear presas",
        "temper": "alerta",
    },
    "minero": {
        "skin": "humano_minero",
        "color": (0.34, 0.34, 0.40),
        "shape": "compact",
        "tool": "pickaxe_reserved",
        "tool_label": "pico",
        "workplace": "mina",
        "material": "piedra",
        "action": "buscar mineral",
        "temper": "terco",
    },
    "mercader": {
        "skin": "humano_mercader",
        "color": (0.35, 0.22, 0.55),
        "shape": "refined",
        "tool": "satchel_reserved",
        "tool_label": "bolsa",
        "workplace": "mercado",
        "material": "mercancia",
        "action": "negociar rutas",
        "temper": "calculador",
    },
    "guardia": {
        "skin": "humano_guardia",
        "color": (0.55, 0.16, 0.14),
        "shape": "broad",
        "tool": "sword_reserved",
        "tool_label": "espada",
        "workplace": "puesto",
        "material": "acero",
        "action": "vigilar caminos",
        "temper": "disciplinado",
    },
    "curandero": {
        "skin": "humano_curandero",
        "color": (0.18, 0.56, 0.52),
        "shape": "slim",
        "tool": "staff_reserved",
        "tool_label": "baston",
        "workplace": "refugio",
        "material": "hierbas",
        "action": "atender heridas",
        "temper": "sereno",
    },
}

def choose_skin_zone_preset(seed, profession=None):
    visual_r = random.Random(int(seed) ^ 0x534B494E)
    if profession in HUMAN_PROFESSION_PROFILES:
        if profession == "carpintero" and visual_r.random() < 0.28:
            return "carpintero_viejo"
        return f"prof_{profession}"
    roll = visual_r.random()
    if roll < 0.18:
        return "carpintero_viejo"
    if roll < 0.34:
        return "ropa_carpintero"
    return "base"

def skin_zones_for_preset(preset_name, profession):
    if preset_name in SKIN_ZONE_PRESETS:
        preset = SKIN_ZONE_PRESETS[preset_name]
        return {
            "head": preset["head"],
            "torso": preset["torso"],
            "pants": preset["pants"],
        }
    profile = HUMAN_PROFESSION_PROFILES.get(profession, HUMAN_PROFESSION_PROFILES["granjero"])
    return {
        "head": None,
        "torso": profile["skin"],
        "pants": profile["skin"],
    }

def profile_for_profession(profession):
    return HUMAN_PROFESSION_PROFILES.get(profession, HUMAN_PROFESSION_PROFILES["granjero"])

def visible_tool_name(favorite_tool):
    if not favorite_tool:
        return None
    return str(favorite_tool).replace("_reserved", "")

def profession_identity(profile):
    return {
        "tool_label": profile.get("tool_label", "herramienta"),
        "workplace": profile.get("workplace", "camino"),
        "material": profile.get("material", "suministros"),
        "action": profile.get("action", "trabajar"),
        "temper": profile.get("temper", "neutral"),
    }

def need_status_text(need_name):
    return {
        "food": "necesito comida antes de seguir trabajando",
        "water": "necesito agua; asi nadie rinde",
        "energy": "me falta descanso",
        "security": "este lugar no se siente seguro",
        "social": "me vendria bien hablar con alguien",
        "calm": "por ahora estoy tranquilo",
    }.get(need_name, "estoy observando la zona")

def _stable_float01(*parts):
    return int(_stable_digest(*parts)[:12], 16) / float(0xFFFFFFFFFFFF)

def _stable_offset(seed, tag, min_radius, max_radius):
    angle = _stable_float01(seed, tag, "angle") * math.pi * 2.0
    radius = min_radius + _stable_float01(seed, tag, "radius") * (max_radius - min_radius)
    return math.cos(angle) * radius, math.sin(angle) * radius

def activity_for_need(npc):
    if npc.current_need == "food":
        return ("buscar_comida", "buscar comida cerca de la zona")
    if npc.current_need == "water":
        return ("buscar_agua", "buscar agua antes de seguir")
    if npc.current_need == "energy":
        return ("descansar", "volver a un punto tranquilo")
    if npc.current_need == "security":
        return ("buscar_seguridad", "acercarse a un lugar seguro")
    if npc.current_need == "social":
        return ("buscar_compania", "acercarse a rutas transitadas")
    return (f"oficio_{npc.profession}", npc.work_action)

def mood_for_npc(npc):
    trust = float(getattr(npc, "memory", {}).get("trust", 0.0))
    stress = float(getattr(npc, "stress", 0.0))
    hostility = float(getattr(npc, "hostilidad", 0.0))
    need = getattr(npc, "current_need", "calm")
    effect = getattr(npc, "activity_effect", "none")

    if need == "food":
        mood = "hambriento"
        detail = "piensa en conseguir comida"
    elif need == "water":
        mood = "sediento"
        detail = "busca agua antes de continuar"
    elif need == "energy":
        mood = "cansado"
        detail = "quiere descansar"
    elif need == "security":
        mood = "inquieto"
        detail = "prioriza sentirse seguro"
    elif need == "social":
        mood = "solitario"
        detail = "quiere hablar con alguien"
    elif effect.endswith("_recover"):
        mood = "recuperandose"
        detail = "esta atendiendo una necesidad"
    elif stress > 55.0:
        mood = "tenso"
        detail = "acumula demasiado estres"
    elif getattr(npc, "activity", "").startswith("oficio_"):
        mood = "concentrado"
        detail = f"esta enfocado en {npc.work_action}"
    else:
        mood = "calmado"
        detail = "no tiene una urgencia fuerte"

    suspicion = hostility * 0.55 + stress * 0.65 - trust * 0.45
    if suspicion > 70.0:
        stance = "desconfiado"
    elif suspicion > 42.0:
        stance = "reservado"
    else:
        stance = "abierto"
    return mood, stance, detail

def dialogue_tone_prefix(npc):
    if npc.stance == "desconfiado":
        return "No te conozco lo suficiente."
    if npc.stance == "reservado":
        return "Te dire lo necesario."
    return "Puedo hablar un momento."

def contextual_dialogue_line(npc, turn):
    npc.update_mood()
    trust = float(getattr(npc, "memory", {}).get("trust", 0.0))
    lines_by_need = {
        "food": [
            f"Con hambre no se trabaja bien; mi {npc.tool_label} pesa el doble.",
            f"Si encuentro comida, despues vuelvo a {npc.work_action}.",
        ],
        "water": [
            "La sed vuelve torpe hasta al mas cuidadoso.",
            f"Necesito agua antes de seguir cerca de {npc.workplace}.",
        ],
        "energy": [
            "Hoy el cuerpo pide descanso, no orgullo.",
            f"Si descanso un poco podre volver a {npc.work_action}.",
        ],
        "security": [
            "Algo aqui no me gusta. Camino con cuidado.",
            f"Prefiero asegurar la zona antes de pensar en {npc.work_material}.",
        ],
        "social": [
            "No todo se resuelve trabajando en silencio.",
            "A veces hablar evita problemas antes de que empiecen.",
        ],
        "calm": [
            f"Estoy {npc.mood}; mi prioridad sigue siendo {npc.work_action}.",
            f"Si ves {npc.work_material}, avisame. Eso me sirve para mi oficio.",
        ],
    }
    stance_lines = {
        "desconfiado": [
            "Mantente donde pueda verte.",
            "No confundas mis palabras con confianza.",
        ],
        "reservado": [
            f"Mi oficio es {npc.profession}; no necesito mucho ruido alrededor.",
            f"Trabajo mejor cerca de {npc.workplace}.",
        ],
        "abierto": [
            f"Ya hemos hablado {int(getattr(npc, 'memoria', 0))} veces; eso cuenta.",
            f"Si necesitas algo, empieza por decirlo claro.",
        ],
    }
    pool = list(lines_by_need.get(npc.current_need, lines_by_need["calm"]))
    pool.extend(stance_lines.get(npc.stance, stance_lines["reservado"]))
    if trust >= 8.0:
        pool.append(f"Te reconozco. No eres solo otro viajero para mi.")
    if getattr(npc, "activity_effect", "") != "travelling":
        pool.append(f"Ahora mismo estoy en: {npc.activity_detail}.")
    idx = int(_stable_float01(npc.id, turn, npc.current_need, npc.mood, npc.stance) * len(pool))
    return pool[max(0, min(len(pool) - 1, idx))]

def compact_memory_notes(record, limit=4):
    notes = record.get("notes", []) if isinstance(record, dict) else []
    compact = []
    for note in notes[-limit:]:
        if not isinstance(note, dict):
            continue
        compact.append({
            "event": str(note.get("event", "")),
            "mood": str(note.get("mood", "")),
            "stance": str(note.get("stance", "")),
            "detail": str(note.get("detail", ""))[:160],
        })
    return compact

def npc_ai_context_packet(npc):
    npc.update_mood()
    record = npc_memory_for(npc)
    return {
        "schema": "stage35_q_npc_ai_context_v1",
        "npc": {
            "id": npc.id,
            "identity": npc.identity_key,
            "name": npc.nombre,
            "title": npc.titulo,
            "profession": npc.profession,
            "temper": npc.temper,
            "tool": npc.tool_label,
        },
        "state": {
            "need": npc.current_need,
            "intent": npc.intent,
            "activity": npc.activity,
            "mood": npc.mood,
            "stance": npc.stance,
            "stress": round(npc.stress, 2),
            "trust": round(float(record.get("trust", 0.0)), 2),
        },
        "work": {
            "place": npc.workplace,
            "material": npc.work_material,
            "action": npc.work_action,
        },
        "memory": {
            "encounters": int(record.get("encounters", 0)),
            "recent": compact_memory_notes(record),
        },
        "dialogue_rules": [
            "Mantener el nombre, oficio y atributos del NPC sin cambiarlos.",
            "Responder con informacion del estado actual, no inventar poderes ni recuerdos inexistentes.",
            "Usar frases cortas compatibles con un juego voxel de aventura.",
            "No afirmar que el NPC es consciente fuera de la simulacion del juego.",
        ],
    }

def build_npc_dialogue_prompt(npc, player_text=""):
    packet = npc.ai_context_packet()
    recent = packet["memory"]["recent"]
    recent_text = "; ".join(note["detail"] for note in recent[-3:]) or "sin recuerdos recientes"
    rules = " ".join(packet["dialogue_rules"])
    return (
        "NPC_DIALOGUE_CONTEXT\n"
        f"Nombre: {packet['npc']['name']} {packet['npc']['title']}\n"
        f"Oficio: {packet['npc']['profession']} con {packet['npc']['tool']}\n"
        f"Estado: necesidad={packet['state']['need']}, animo={packet['state']['mood']}, "
        f"actitud={packet['state']['stance']}, actividad={packet['state']['activity']}\n"
        f"Trabajo: {packet['work']['action']} cerca de {packet['work']['place']} usando {packet['work']['material']}\n"
        f"Relacion: confianza={packet['state']['trust']}, encuentros={packet['memory']['encounters']}\n"
        f"Recuerdos recientes: {recent_text}\n"
        f"Jugador dice: {str(player_text or '').strip()[:220]}\n"
        f"Reglas: {rules}\n"
        "Respuesta esperada: una frase corta en primera persona del NPC."
    )

def _clean_ai_reply(text, limit=NPC_AI_REPLY_MAX_CHARS):
    line = " ".join(str(text or "").replace("\r", " ").replace("\n", " ").split())
    if not line:
        return ""
    return line[:limit].rstrip()

def _npc_ai_cache_key(npc, player_text):
    text = " ".join(str(player_text or "").lower().split())[:80]
    trust_bucket = int(float(getattr(npc, "memory", {}).get("trust", 0.0)) // 10)
    return (
        npc.id,
        text,
        npc.current_need,
        npc.mood,
        npc.stance,
        npc.activity,
        trust_bucket,
    )

def npc_ai_cache_stats():
    return {
        "entries": len(NPC_AI_REPLY_CACHE),
        "max_entries": NPC_AI_REPLY_CACHE_MAX,
        "max_reply_chars": NPC_AI_REPLY_MAX_CHARS,
    }

def clear_npc_ai_cache():
    NPC_AI_REPLY_CACHE.clear()

def npc_ai_queue_stats():
    return {
        "pending": len(NPC_AI_REPLY_QUEUE),
        "completed": len(NPC_AI_COMPLETED_REPLIES),
        "max_pending": NPC_AI_QUEUE_MAX,
        "drain_max": NPC_AI_QUEUE_DRAIN_MAX,
    }

def _record_npc_ai_telemetry(source, elapsed_ms=0.0, error=None):
    elapsed_ms = max(0.0, float(elapsed_ms or 0.0))
    NPC_AI_TELEMETRY["requests"] += 1
    NPC_AI_TELEMETRY["total_ms"] = round(float(NPC_AI_TELEMETRY["total_ms"]) + elapsed_ms, 3)
    NPC_AI_TELEMETRY["max_ms"] = round(max(float(NPC_AI_TELEMETRY["max_ms"]), elapsed_ms), 3)
    NPC_AI_TELEMETRY["last_ms"] = round(elapsed_ms, 3)
    NPC_AI_TELEMETRY["last_source"] = str(source or "unknown")
    NPC_AI_TELEMETRY["last_error"] = error
    if source in ("backend", "queue_backend"):
        NPC_AI_TELEMETRY["backend_replies"] += 1
    elif source in ("fallback", "queue_fallback", "interact"):
        NPC_AI_TELEMETRY["fallback_replies"] += 1
    elif source in ("cache", "queue_cache"):
        NPC_AI_TELEMETRY["cache_hits"] += 1
    elif source == "queue_rejected":
        NPC_AI_TELEMETRY["queue_rejected"] += 1
    if error:
        NPC_AI_TELEMETRY["errors"] += 1

def npc_ai_telemetry_stats():
    stats = dict(NPC_AI_TELEMETRY)
    requests = max(1, int(stats.get("requests", 0)))
    stats["avg_ms"] = round(float(stats.get("total_ms", 0.0)) / requests, 3)
    return stats

def clear_npc_ai_telemetry():
    for key in list(NPC_AI_TELEMETRY.keys()):
        if key in ("last_source",):
            NPC_AI_TELEMETRY[key] = "none"
        elif key in ("last_error",):
            NPC_AI_TELEMETRY[key] = None
        else:
            NPC_AI_TELEMETRY[key] = 0.0 if key.endswith("_ms") or key == "total_ms" else 0

def npc_ai_runtime_stats():
    return {
        "cache": npc_ai_cache_stats(),
        "queue": npc_ai_queue_stats(),
        "telemetry": npc_ai_telemetry_stats(),
    }

def npc_ai_pending_for(npc_id):
    for request in NPC_AI_REPLY_QUEUE:
        if request.get("npc_id") == npc_id:
            return request.get("request_id")
    return None

def clear_npc_ai_queue():
    NPC_AI_REPLY_QUEUE.clear()
    NPC_AI_COMPLETED_REPLIES.clear()

def queue_npc_ai_reply(npc, player_text="", use_cache=True):
    global NPC_AI_REQUEST_COUNTER
    npc.update_mood()
    key = _npc_ai_cache_key(npc, player_text)
    NPC_AI_REQUEST_COUNTER += 1
    request_id = f"npc_ai_req_{NPC_AI_REQUEST_COUNTER:06d}"
    if use_cache and key in NPC_AI_REPLY_CACHE:
        line = NPC_AI_REPLY_CACHE[key]
        _record_npc_ai_telemetry("queue_cache")
        NPC_AI_COMPLETED_REPLIES[request_id] = {
            "status": "ready",
            "npc_id": npc.id,
            "reply": line,
            "cached": True,
        }
        npc.remember_event("dialogue_ai_cached", line)
        npc.pending_ai_request = None
        npc.last_ai_reply = line
        npc.last_ai_status = "ready_cached"
        return request_id
    if len(NPC_AI_REPLY_QUEUE) >= NPC_AI_QUEUE_MAX:
        _record_npc_ai_telemetry("queue_rejected", error="queue_full")
        NPC_AI_COMPLETED_REPLIES[request_id] = {
            "status": "rejected",
            "npc_id": npc.id,
            "reply": "",
            "cached": False,
            "reason": "queue_full",
        }
        npc.pending_ai_request = None
        npc.last_ai_status = "rejected_queue_full"
        return request_id
    NPC_AI_REPLY_QUEUE.append({
        "request_id": request_id,
        "npc": npc,
        "npc_id": npc.id,
        "player_text": player_text,
        "prompt": build_npc_dialogue_prompt(npc, player_text),
        "packet": npc.ai_context_packet(),
        "cache_key": key,
        "use_cache": use_cache,
    })
    npc.remember_event("ai_queued", str(player_text or "")[:160])
    npc.pending_ai_request = request_id
    npc.last_ai_status = "queued"
    return request_id

def drain_npc_ai_queue(responder, max_items=NPC_AI_QUEUE_DRAIN_MAX):
    processed = []
    if not callable(responder):
        return processed
    max_items = max(0, int(max_items))
    for _ in range(min(max_items, len(NPC_AI_REPLY_QUEUE))):
        request = NPC_AI_REPLY_QUEUE.pop(0)
        start = time.perf_counter()
        npc = request["npc"]
        line = ""
        cached = False
        source = "queue_backend"
        error = None
        key = request["cache_key"]
        if request["use_cache"] and key in NPC_AI_REPLY_CACHE:
            line = NPC_AI_REPLY_CACHE[key]
            cached = True
            source = "queue_cache"
            npc.remember_event("dialogue_ai_cached", line)
        else:
            try:
                line = _clean_ai_reply(responder(request["packet"], request["prompt"]))
            except Exception as exc:
                error = f"responder_error:{exc.__class__.__name__}"
                line = ""
            if line:
                if request["use_cache"]:
                    NPC_AI_REPLY_CACHE[key] = line
                    if len(NPC_AI_REPLY_CACHE) > NPC_AI_REPLY_CACHE_MAX:
                        oldest_key = next(iter(NPC_AI_REPLY_CACHE))
                        NPC_AI_REPLY_CACHE.pop(oldest_key, None)
                npc.remember_event("dialogue_ai", line)
            else:
                source = "queue_fallback"
                error = error or getattr(responder, "last_error", None) or "empty_reply"
                line = f"{dialogue_tone_prefix(npc)} {contextual_dialogue_line(npc, npc.memoria)}"
                npc.remember_event("dialogue", line)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        _record_npc_ai_telemetry(source, elapsed_ms=elapsed_ms, error=error)
        result = {
            "status": "ready",
            "npc_id": request["npc_id"],
            "reply": line,
            "cached": cached,
        }
        npc.pending_ai_request = None
        npc.last_ai_reply = line
        npc.last_ai_status = "ready_cached" if cached else "ready"
        NPC_AI_COMPLETED_REPLIES[request["request_id"]] = result
        processed.append({"request_id": request["request_id"], **result})
    return processed

def pop_npc_ai_reply(request_id, forget=True):
    result = NPC_AI_COMPLETED_REPLIES.get(request_id)
    if result and forget:
        NPC_AI_COMPLETED_REPLIES.pop(request_id, None)
    return result

def npc_ai_status_for(npc):
    pending = getattr(npc, "pending_ai_request", None) or npc_ai_pending_for(npc.id)
    completed_ready = None
    for request_id, result in NPC_AI_COMPLETED_REPLIES.items():
        if result.get("npc_id") == npc.id:
            completed_ready = request_id
            break
    status = getattr(npc, "last_ai_status", "idle")
    if pending:
        status = "queued"
    elif completed_ready:
        status = "ready"
    return {
        "status": status,
        "pending_request": pending,
        "ready_request": completed_ready,
        "last_reply": getattr(npc, "last_ai_reply", ""),
    }

def npc_local_ai_reply(npc, player_text="", responder=None, use_cache=True):
    prompt = build_npc_dialogue_prompt(npc, player_text)
    if callable(responder):
        start = time.perf_counter()
        npc.update_mood()
        npc.remember_event("interaction")
        key = _npc_ai_cache_key(npc, player_text)
        if use_cache and key in NPC_AI_REPLY_CACHE:
            line = NPC_AI_REPLY_CACHE[key]
            npc.remember_event("dialogue_ai_cached", line)
            _record_npc_ai_telemetry("cache", elapsed_ms=(time.perf_counter() - start) * 1000.0)
            return line
        error = None
        try:
            line = _clean_ai_reply(responder(npc.ai_context_packet(), prompt))
            if line:
                if use_cache:
                    NPC_AI_REPLY_CACHE[key] = line
                    if len(NPC_AI_REPLY_CACHE) > NPC_AI_REPLY_CACHE_MAX:
                        oldest_key = next(iter(NPC_AI_REPLY_CACHE))
                        NPC_AI_REPLY_CACHE.pop(oldest_key, None)
                npc.remember_event("dialogue_ai", line)
                _record_npc_ai_telemetry("backend", elapsed_ms=(time.perf_counter() - start) * 1000.0)
                return line
        except Exception as exc:
            error = f"responder_error:{exc.__class__.__name__}"
            pass
        error = error or getattr(responder, "last_error", None) or "empty_reply"
        line = f"{dialogue_tone_prefix(npc)} {contextual_dialogue_line(npc, npc.memoria)}"
        npc.remember_event("dialogue", line)
        _record_npc_ai_telemetry("fallback", elapsed_ms=(time.perf_counter() - start) * 1000.0, error=error)
        return line
    _record_npc_ai_telemetry("interact")
    return npc.interactuar()

class LocalNPCModelAdapter:
    """Adaptador minimo para conectar un modelo local sin acoplar NPCs al motor."""
    def __init__(self, name="dry_run", enabled=False, max_prompt_chars=900, backend=None):
        self.name = name
        self.enabled = bool(enabled)
        self.max_prompt_chars = int(max_prompt_chars)
        self.backend = backend
        self.calls = 0
        self.last_error = None

    def status(self):
        return {
            "name": self.name,
            "enabled": self.enabled,
            "has_backend": callable(self.backend),
            "calls": self.calls,
            "max_prompt_chars": self.max_prompt_chars,
            "last_error": self.last_error,
        }

    def reply(self, packet, prompt):
        self.calls += 1
        prompt = str(prompt or "")[:self.max_prompt_chars]
        if not self.enabled:
            self.last_error = None
            state = packet.get("state", {})
            work = packet.get("work", {})
            need = state.get("need", "calm")
            action = work.get("action", "seguir trabajando")
            mood = state.get("mood", "calmado")
            return f"Estoy {mood}; ahora necesito {need} y debo {action}."
        if callable(self.backend):
            try:
                line = _clean_ai_reply(self.backend(packet, prompt))
                self.last_error = None if line else getattr(self.backend, "last_error", "empty_backend_reply")
                return line
            except Exception as exc:
                self.last_error = f"backend_error:{exc.__class__.__name__}"
                return ""
        self.last_error = "no_model_backend_configured"
        return ""

    def __call__(self, packet, prompt):
        return self.reply(packet, prompt)

class LocalCommandNPCBackend:
    """Backend por comando local: recibe JSON por stdin y responde texto o JSON."""
    def __init__(self, command=None, timeout=2.0, max_output_chars=NPC_AI_REPLY_MAX_CHARS):
        self.command = list(command or [])
        self.timeout = float(timeout)
        self.max_output_chars = int(max_output_chars)
        self.calls = 0
        self.last_error = None

    def status(self):
        return {
            "type": "command",
            "configured": bool(self.command),
            "command": self.command,
            "timeout": self.timeout,
            "calls": self.calls,
            "last_error": self.last_error,
        }

    def __call__(self, packet, prompt):
        self.calls += 1
        if not self.command:
            self.last_error = "no_command_configured"
            return ""
        payload = {
            "packet": packet,
            "prompt": str(prompt or ""),
            "max_chars": self.max_output_chars,
        }
        try:
            proc = subprocess.run(
                self.command,
                input=json.dumps(payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=self.timeout,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            self.last_error = "timeout"
            return ""
        except Exception as exc:
            self.last_error = f"command_error:{exc.__class__.__name__}"
            return ""
        if proc.returncode != 0:
            self.last_error = f"exit_{proc.returncode}"
            return ""
        raw = (proc.stdout or "").strip()
        if not raw:
            self.last_error = "empty_stdout"
            return ""
        try:
            data = json.loads(raw)
            raw = data.get("reply", raw) if isinstance(data, dict) else raw
        except Exception:
            pass
        self.last_error = None
        return _clean_ai_reply(raw, self.max_output_chars)

NPC_LOCAL_MODEL_ADAPTER = LocalNPCModelAdapter()
NPC_LOCAL_COMMAND_BACKEND = None

def get_npc_local_model_adapter():
    return NPC_LOCAL_MODEL_ADAPTER

def configure_npc_local_model(enabled=False, name="dry_run", max_prompt_chars=900):
    NPC_LOCAL_MODEL_ADAPTER.enabled = bool(enabled)
    NPC_LOCAL_MODEL_ADAPTER.name = str(name or "dry_run")
    NPC_LOCAL_MODEL_ADAPTER.max_prompt_chars = int(max_prompt_chars)
    NPC_LOCAL_MODEL_ADAPTER.last_error = None
    return NPC_LOCAL_MODEL_ADAPTER.status()

def set_npc_local_model_backend(backend=None, name=None, enabled=True):
    NPC_LOCAL_MODEL_ADAPTER.backend = backend if callable(backend) else None
    if name is not None:
        NPC_LOCAL_MODEL_ADAPTER.name = str(name or "dry_run")
    NPC_LOCAL_MODEL_ADAPTER.enabled = bool(enabled and callable(backend))
    NPC_LOCAL_MODEL_ADAPTER.last_error = None
    return NPC_LOCAL_MODEL_ADAPTER.status()

def configure_npc_command_backend(command=None, timeout=2.0, name="command_backend"):
    global NPC_LOCAL_COMMAND_BACKEND
    NPC_LOCAL_COMMAND_BACKEND = LocalCommandNPCBackend(command=command, timeout=timeout)
    return set_npc_local_model_backend(NPC_LOCAL_COMMAND_BACKEND, name=name, enabled=bool(command))

def clear_npc_local_model_backend():
    global NPC_LOCAL_COMMAND_BACKEND
    NPC_LOCAL_COMMAND_BACKEND = None
    NPC_LOCAL_MODEL_ADAPTER.backend = None
    NPC_LOCAL_MODEL_ADAPTER.enabled = False
    NPC_LOCAL_MODEL_ADAPTER.last_error = None
    return NPC_LOCAL_MODEL_ADAPTER.status()

def npc_local_model_status():
    status = NPC_LOCAL_MODEL_ADAPTER.status()
    status["command_backend"] = NPC_LOCAL_COMMAND_BACKEND.status() if NPC_LOCAL_COMMAND_BACKEND else None
    return status

def _npc_local_ai_config_path(path=None):
    if path:
        return os.path.abspath(str(path))
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(root, NPC_LOCAL_AI_CONFIG_FILENAME)

def _sanitize_command(command):
    if not isinstance(command, (list, tuple)):
        return []
    clean = []
    for part in command:
        text = str(part).strip()
        if text:
            clean.append(text)
    return clean

def _clamp_timeout(value, default=2.0):
    try:
        timeout = float(value)
    except Exception:
        timeout = float(default)
    return max(0.1, min(timeout, 30.0))

def _clamp_prompt_chars(value, default=900):
    try:
        chars = int(value)
    except Exception:
        chars = int(default)
    return max(120, min(chars, 6000))

def npc_local_model_config_snapshot():
    status = npc_local_model_status()
    command_status = status.get("command_backend") or {}
    return {
        "schema": "stage35_z_npc_local_ai_config_v1",
        "adapter": {
            "name": str(status.get("name") or "dry_run"),
            "enabled": bool(status.get("enabled")),
            "max_prompt_chars": _clamp_prompt_chars(status.get("max_prompt_chars")),
        },
        "command_backend": {
            "configured": bool(command_status.get("configured")),
            "command": _sanitize_command(command_status.get("command", [])),
            "timeout": _clamp_timeout(command_status.get("timeout", 2.0)),
        },
        "notes": [
            "Cargar esta configuracion no ejecuta el comando.",
            "El comando solo corre cuando se pide reply/probe explicitamente.",
        ],
    }

def normalize_npc_local_model_config(data):
    source = data if isinstance(data, dict) else {}
    adapter = source.get("adapter", {}) if isinstance(source.get("adapter", {}), dict) else {}
    command_backend = source.get("command_backend", {}) if isinstance(source.get("command_backend", {}), dict) else {}
    command = _sanitize_command(command_backend.get("command", []))
    default_name = "command_backend" if command else "dry_run"
    return {
        "schema": "stage35_z_npc_local_ai_config_v1",
        "adapter": {
            "name": str(adapter.get("name") or default_name),
            "enabled": bool(adapter.get("enabled", bool(command))),
            "max_prompt_chars": _clamp_prompt_chars(adapter.get("max_prompt_chars", 900)),
        },
        "command_backend": {
            "configured": bool(command),
            "command": command,
            "timeout": _clamp_timeout(command_backend.get("timeout", 2.0)),
        },
        "notes": list(source.get("notes", []))[:8] if isinstance(source.get("notes", []), list) else [],
    }

def apply_npc_local_model_config(config, enable_backend=None):
    global NPC_LOCAL_COMMAND_BACKEND
    clean = normalize_npc_local_model_config(config)
    adapter = clean["adapter"]
    command_backend = clean["command_backend"]
    command = command_backend["command"]
    enabled = adapter["enabled"] if enable_backend is None else bool(enable_backend)
    configure_npc_local_model(
        enabled=False,
        name=adapter["name"],
        max_prompt_chars=adapter["max_prompt_chars"],
    )
    if command:
        NPC_LOCAL_COMMAND_BACKEND = LocalCommandNPCBackend(command=command, timeout=command_backend["timeout"])
        set_npc_local_model_backend(NPC_LOCAL_COMMAND_BACKEND, name=adapter["name"], enabled=enabled)
        return npc_local_model_status()
    clear_npc_local_model_backend()
    return npc_local_model_status()

def save_npc_local_model_config(path=None, config=None):
    target = _npc_local_ai_config_path(path)
    folder = os.path.dirname(target)
    if folder:
        os.makedirs(folder, exist_ok=True)
    clean = normalize_npc_local_model_config(config) if config is not None else npc_local_model_config_snapshot()
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(clean, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {
        "ok": True,
        "path": target,
        "config": clean,
    }

def load_npc_local_model_config(path=None, apply_config=False, enable_backend=None):
    target = _npc_local_ai_config_path(path)
    if not os.path.exists(target):
        return {
            "ok": False,
            "path": target,
            "error": "config_not_found",
            "applied": False,
            "config": None,
        }
    try:
        with open(target, "r", encoding="utf-8") as handle:
            clean = normalize_npc_local_model_config(json.load(handle))
    except Exception as exc:
        return {
            "ok": False,
            "path": target,
            "error": f"config_read_error:{exc.__class__.__name__}",
            "applied": False,
            "config": None,
        }
    result = {
        "ok": True,
        "path": target,
        "error": None,
        "applied": False,
        "config": clean,
    }
    if apply_config:
        result["status"] = apply_npc_local_model_config(clean, enable_backend=enable_backend)
        result["applied"] = True
    return result

def probe_npc_local_model_backend(player_text="probe", packet=None, prompt=None):
    adapter = get_npc_local_model_adapter()
    sample_packet = packet or {
        "schema": "stage35_y_npc_ai_probe_v1",
        "npc": {
            "id": "npc_probe",
            "identity": "probe_carpintero",
            "name": "Probe",
            "title": "El Probador",
            "profession": "carpintero",
            "temper": "neutral",
            "tool": "martillo",
        },
        "state": {
            "need": "focus",
            "intent": "diagnosticar",
            "activity": "probe",
            "mood": "calmado",
            "stance": "abierto",
            "stress": 0.0,
            "trust": 0.0,
        },
        "work": {
            "place": "banco de pruebas",
            "material": "madera",
            "action": "confirmar conexion",
        },
        "memory": {
            "encounters": 0,
            "recent": [],
        },
        "dialogue_rules": [
            "Responder una frase corta para confirmar que el backend funciona.",
            "No cambiar identidad ni atributos del NPC de prueba.",
        ],
    }
    sample_prompt = prompt or (
        "NPC_BACKEND_PROBE\n"
        f"Jugador dice: {str(player_text or '').strip()[:160]}\n"
        "Respuesta esperada: una frase corta confirmando conexion."
    )
    before_calls = int(adapter.calls)
    start = time.perf_counter()
    reply = adapter.reply(sample_packet, sample_prompt)
    elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
    status = npc_local_model_status()
    return {
        "ok": bool(reply) and not bool(status.get("last_error")),
        "reply": reply,
        "elapsed_ms": elapsed_ms,
        "used_backend": bool(status.get("has_backend")) and bool(status.get("enabled")),
        "calls_added": int(adapter.calls) - before_calls,
        "last_error": status.get("last_error"),
        "status": status,
    }

def _memory_canonical(npc):
    return {
        "name": npc.nombre,
        "title": npc.titulo,
        "profession": npc.profession,
        "identity": npc.identity_key,
        "seed": int(npc.seed),
        "hostility": int(npc.hostilidad),
        "damage": int(getattr(npc, "daño", 0)),
        "tool": npc.back_tool,
        "tool_label": npc.tool_label,
        "temper": npc.temper,
        "skin_preset": npc.skin_preset,
    }

def npc_memory_for(npc):
    record = NPC_MEMORY_REGISTRY.get(npc.id)
    if record is None:
        record = {
            "id": npc.id,
            "canonical": _memory_canonical(npc),
            "encounters": 0,
            "trust": 0.0,
            "last_need": npc.current_need,
            "last_intent": npc.intent,
            "last_activity": getattr(npc, "activity", "wander"),
            "last_mood": getattr(npc, "mood", "calmado"),
            "last_stance": getattr(npc, "stance", "abierto"),
            "last_position": (round(npc.x, 2), round(npc.z, 2)),
            "notes": [],
        }
        NPC_MEMORY_REGISTRY[npc.id] = record
    else:
        canonical = record.setdefault("canonical", _memory_canonical(npc))
        npc.nombre = canonical.get("name", npc.nombre)
        npc.titulo = canonical.get("title", npc.titulo)
    record["last_need"] = npc.current_need
    record["last_intent"] = npc.intent
    record["last_activity"] = getattr(npc, "activity", "wander")
    record["last_mood"] = getattr(npc, "mood", "calmado")
    record["last_stance"] = getattr(npc, "stance", "abierto")
    record["last_position"] = (round(npc.x, 2), round(npc.z, 2))
    return record

def remember_npc_event(npc, event, detail=None):
    record = npc_memory_for(npc)
    if event == "interaction":
        record["encounters"] += 1
        record["trust"] = _clamp(record.get("trust", 0.0) + 1.5, 0.0, 100.0)
    note = {
        "event": event,
        "need": npc.current_need,
        "intent": npc.intent,
        "activity": getattr(npc, "activity", "wander"),
        "mood": getattr(npc, "mood", "calmado"),
        "stance": getattr(npc, "stance", "abierto"),
        "detail": detail or need_status_text(npc.current_need),
    }
    notes = record.setdefault("notes", [])
    notes.append(note)
    if len(notes) > NPC_MEMORY_MAX_NOTES:
        del notes[:-NPC_MEMORY_MAX_NOTES]
    return record

def npc_memory_snapshot(npc):
    record = npc_memory_for(npc)
    canonical = record.get("canonical", {})
    return {
        "id": record["id"],
        "identity": canonical.get("identity"),
        "name": canonical.get("name"),
        "title": canonical.get("title"),
        "profession": canonical.get("profession"),
        "encounters": record.get("encounters", 0),
        "trust": round(record.get("trust", 0.0), 2),
        "last_need": record.get("last_need", "calm"),
        "last_intent": record.get("last_intent", "wander"),
        "last_activity": record.get("last_activity", "wander"),
        "last_mood": record.get("last_mood", "calmado"),
        "last_stance": record.get("last_stance", "abierto"),
        "last_position": record.get("last_position"),
        "last_note": record.get("notes", [])[-1] if record.get("notes") else None,
    }

def _safe_memory_record(record):
    canonical = dict(record.get("canonical", {}))
    notes = list(record.get("notes", []))[-NPC_MEMORY_MAX_NOTES:]
    last_position = record.get("last_position", (0.0, 0.0)) or (0.0, 0.0)
    if len(last_position) < 2:
        last_position = (0.0, 0.0)
    return {
        "id": str(record.get("id", "")),
        "canonical": canonical,
        "encounters": int(record.get("encounters", 0)),
        "trust": round(_clamp(float(record.get("trust", 0.0))), 2),
        "last_need": str(record.get("last_need", "calm")),
        "last_intent": str(record.get("last_intent", "wander")),
        "last_activity": str(record.get("last_activity", "wander")),
        "last_mood": str(record.get("last_mood", "calmado")),
        "last_stance": str(record.get("last_stance", "abierto")),
        "last_position": [float(last_position[0]), float(last_position[1])],
        "notes": notes,
    }

def export_npc_memory():
    records = []
    for record in NPC_MEMORY_REGISTRY.values():
        safe = _safe_memory_record(record)
        if safe["id"]:
            records.append(safe)
    return {
        "version": "stage35_p_npc_memory_v2",
        "records": records,
    }

def import_npc_memory(payload, merge=True):
    if not payload:
        return 0
    records = payload.get("records", payload if isinstance(payload, list) else [])
    if not isinstance(records, list):
        return 0
    if not merge:
        NPC_MEMORY_REGISTRY.clear()
    loaded = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        npc_id = str(record.get("id", ""))
        if not npc_id:
            continue
        safe = _safe_memory_record(record)
        safe["id"] = npc_id
        NPC_MEMORY_REGISTRY[npc_id] = safe
        loaded += 1
    return loaded

def clear_npc_memory():
    NPC_MEMORY_REGISTRY.clear()

class NPC:
    def __init__(self, seed, x=0, z=0, y=0, npc_id=None, id_source="world", id_slot=0):
        r = random.Random(seed)
        self.id = npc_id or build_npc_id(seed, x, z, id_source, id_slot)
        self.seed = seed
        self.x = x
        self.y = y
        self.z = z
        self.spawn_x = x
        self.spawn_z = z
        self.nombre = r.choice(FIRST_NAMES)
        self.titulo = r.choice(TITLES)
        self.daño = r.randint(8,18)
        self.hostilidad = r.randint(0,100)
        self.height = 1.85
        self.collider_size = (0.62, 1.80, 0.62)
        self.visual_size = (1.15, 2.10, 1.00)
        self.yaw = 0.0
        self.profession = r.choice(HUMAN_PROFESSIONS)
        self.speed = 1.2 + r.random() * 0.8
        self.wander_radius = 10.0
        self.direction = r.uniform(0, 2 * math.pi)
        self.wander_timer = 0.0
        self.wander_change = 1.5 + r.random() * 1.5
        self.memoria = 0
        self.highlight = False
        self.terrain_height_func = None
        self.dialogos = [
            "Esta zona ha cambiado mucho.",
            "No todos los viajeros son de fiar.",
            "Si necesitas agua, ve hacia el oeste.",
            "No me molesten cuando estoy ocupado."
        ]
        self.descripcion = r.choice([
            "Un viajero de paso.",
            "Parece conocer estas tierras.",
            "Tiene una mirada cansada.",
            "Anda con cuidado, lleva cosas valiosas."
        ]) + f" Profesión: {self.profession}."
        self.target_x = self.x
        self.target_z = self.z
        self.max_health = 100.0
        self.health = 100.0
        needs_r = random.Random(int(seed) ^ 0x4E454544)
        self.needs = {
            "food": 72.0 + needs_r.random() * 18.0,
            "water": 70.0 + needs_r.random() * 20.0,
            "energy": 68.0 + needs_r.random() * 24.0,
            "security": 62.0 + needs_r.random() * 28.0,
            "social": 45.0 + needs_r.random() * 35.0,
        }
        self.need_rates = {
            "food": 0.008 + needs_r.random() * 0.006,
            "water": 0.011 + needs_r.random() * 0.008,
            "energy": 0.006 + needs_r.random() * 0.005,
            "social": 0.003 + needs_r.random() * 0.004,
        }
        self.stress = 0.0
        self.current_need = "calm"
        self.intent = "wander"
        self.activity = "wander"
        self.activity_detail = "explorar cerca"
        self.activity_step = 0
        self.activity_effect = "none"
        self.activity_progress = 0.0
        self.mood = "calmado"
        self.stance = "abierto"
        self.mood_detail = "no tiene una urgencia fuerte"
        self.pending_ai_request = None
        self.last_ai_reply = ""
        self.last_ai_status = "idle"
        self.needs_speed_factor = 1.0
        self.walk_phase = 0.0
        self.move_amount = 0.0
        self.skin_preset = choose_skin_zone_preset(seed, self.profession)
        profile = profile_for_profession(self.profession)
        preset = SKIN_ZONE_PRESETS.get(self.skin_preset)
        self.skin_zones = skin_zones_for_preset(self.skin_preset, self.profession)
        self.visual_profession = (preset["visual_profession"] if preset else self.profession) or self.profession
        self.face_type = preset["face_type"] if preset else "neutral"
        self.torso_type = preset["torso_type"] if preset else "neutral"
        self.nose_style = preset["nose_style"] if preset else "human"
        self.ear_style = preset["ear_style"] if preset else "human"
        self.profession_color = profile["color"]
        self.body_shape = profile["shape"]
        self.favorite_tool = profile["tool"]
        self.back_equipment_reserved = False
        self.back_tool = visible_tool_name(self.favorite_tool)
        identity = profession_identity(profile)
        self.tool_label = identity["tool_label"]
        self.workplace = identity["workplace"]
        self.work_material = identity["material"]
        self.work_action = identity["action"]
        self.temper = identity["temper"]
        self.identity_key = _stable_digest("identity", self.id, self.profession, self.skin_preset)[:12]
        work_dx, work_dz = _stable_offset(self.id, f"work_{self.profession}", 2.5, 7.5)
        rest_dx, rest_dz = _stable_offset(self.id, "rest", 1.5, 4.0)
        social_dx, social_dz = _stable_offset(self.id, "social", 3.0, 6.0)
        self.work_anchor = (self.spawn_x + work_dx, self.spawn_z + work_dz)
        self.rest_anchor = (self.spawn_x + rest_dx, self.spawn_z + rest_dz)
        self.social_anchor = (self.spawn_x + social_dx, self.spawn_z + social_dz)
        self.memory = npc_memory_for(self)
        self.memoria = int(self.memory.get("encounters", 0))
        self.update_mood()

    def update_needs(self, dt, threat_level=0.0):
        dt = _clamp(float(dt), 0.0, 2.0)
        threat_level = _clamp(float(threat_level), 0.0, 1.0)
        self.needs["food"] = _clamp(self.needs["food"] - self.need_rates["food"] * dt)
        self.needs["water"] = _clamp(self.needs["water"] - self.need_rates["water"] * dt)
        self.needs["energy"] = _clamp(self.needs["energy"] - self.need_rates["energy"] * dt)
        self.needs["social"] = _clamp(self.needs["social"] - self.need_rates["social"] * dt)
        if threat_level > 0.0:
            self.needs["security"] = _clamp(self.needs["security"] - (0.45 + threat_level * 2.4) * dt)
        else:
            self.needs["security"] = _clamp(self.needs["security"] + 0.018 * dt)

        need_name, need_value = min(self.needs.items(), key=lambda item: item[1])
        self.current_need = need_name if need_value < 38.0 else "calm"
        intent_by_need = {
            "food": "seek_food",
            "water": "seek_water",
            "energy": "rest",
            "security": "seek_safety",
            "social": "seek_company",
        }
        self.intent = intent_by_need.get(self.current_need, "wander")
        self.activity, self.activity_detail = activity_for_need(self)
        urgency = max(0.0, 35.0 - need_value)
        self.stress = _clamp(self.stress + urgency * 0.018 * dt + threat_level * 18.0 * dt - 0.55 * dt)
        self.needs_speed_factor = 0.72 + 0.28 * (self.needs["energy"] / 100.0)
        self.update_mood()

    def needs_snapshot(self):
        self.update_mood()
        memory = npc_memory_snapshot(self)
        return {
            "id": self.id,
            "identity": self.identity_key,
            "memory": memory,
            "name": self.nombre,
            "title": self.titulo,
            "profession": self.profession,
            "visual_profession": self.visual_profession,
            "tool": self.back_tool,
            "tool_label": self.tool_label,
            "workplace": self.workplace,
            "work_action": self.work_action,
            "temper": self.temper,
            "need": self.current_need,
            "intent": self.intent,
            "activity": self.activity,
            "activity_detail": self.activity_detail,
            "activity_effect": self.activity_effect,
            "activity_progress": round(self.activity_progress, 2),
            "mood": self.mood,
            "stance": self.stance,
            "mood_detail": self.mood_detail,
            "conversation_context": self.conversation_context(),
            "ai_context_ready": True,
            "ai_status": self.ai_status(),
            "work_anchor": (round(self.work_anchor[0], 2), round(self.work_anchor[1], 2)),
            "stress": round(self.stress, 2),
            "food": round(self.needs["food"], 2),
            "water": round(self.needs["water"], 2),
            "energy": round(self.needs["energy"], 2),
            "security": round(self.needs["security"], 2),
            "social": round(self.needs["social"], 2),
        }

    def remember_event(self, event, detail=None):
        self.memory = remember_npc_event(self, event, detail)
        self.memoria = int(self.memory.get("encounters", self.memoria))
        return self.memory

    def memory_snapshot(self):
        return npc_memory_snapshot(self)

    def update_mood(self):
        self.mood, self.stance, self.mood_detail = mood_for_npc(self)
        return self.mood

    def conversation_context(self):
        return {
            "mood": self.mood,
            "stance": self.stance,
            "need": self.current_need,
            "activity": self.activity,
            "detail": self.mood_detail,
            "tone": dialogue_tone_prefix(self),
            "trust": round(float(getattr(self, "memory", {}).get("trust", 0.0)), 2),
        }

    def ai_context_packet(self):
        return npc_ai_context_packet(self)

    def ai_status(self):
        return npc_ai_status_for(self)

    def dialogue_prompt(self, player_text=""):
        return build_npc_dialogue_prompt(self, player_text)

    def reply_to_player(self, player_text="", responder=None, use_cache=True):
        active_responder = responder if responder is not None else get_npc_local_model_adapter()
        return npc_local_ai_reply(self, player_text, responder=active_responder, use_cache=use_cache)

    def queue_reply_to_player(self, player_text="", use_cache=True):
        return queue_npc_ai_reply(self, player_text, use_cache=use_cache)

    def pop_queued_reply(self, request_id, forget=True):
        result = pop_npc_ai_reply(request_id, forget=forget)
        if result:
            self.pending_ai_request = None
            self.last_ai_reply = result.get("reply", "")
            self.last_ai_status = "idle" if result.get("status") == "ready" else result.get("status", "idle")
        return result

    def _activity_anchor(self):
        if self.current_need == "energy":
            return self.rest_anchor
        if self.current_need == "social":
            return self.social_anchor
        if self.current_need == "security":
            return (self.spawn_x, self.spawn_z)
        if self.current_need == "water":
            return (self.spawn_x - self.wander_radius * 0.55, self.spawn_z + self.wander_radius * 0.25)
        if self.current_need == "food":
            return (self.spawn_x + self.wander_radius * 0.35, self.spawn_z - self.wander_radius * 0.45)
        return self.work_anchor

    def choose_activity_target(self):
        anchor_x, anchor_z = self._activity_anchor()
        spread = 1.4 if self.current_need in ("energy", "security") else 2.8
        if self.current_need == "calm":
            spread = 3.5
        self.activity_step += 1
        jitter_x, jitter_z = _stable_offset(self.id, f"{self.activity}_{self.activity_step}", 0.4, spread)
        self.target_x = anchor_x + jitter_x
        self.target_z = anchor_z + jitter_z

    def apply_activity_effects(self, dt):
        anchor_x, anchor_z = self._activity_anchor()
        dist = math.hypot(self.x - anchor_x, self.z - anchor_z)
        self.activity_progress = max(0.0, min(1.0, 1.0 - dist / 4.0))
        if self.activity_progress <= 0.0:
            self.activity_effect = "travelling"
            return

        gain = dt * self.activity_progress
        if self.current_need == "food":
            self.needs["food"] = _clamp(self.needs["food"] + 2.8 * gain)
            self.activity_effect = "food_recover"
        elif self.current_need == "water":
            self.needs["water"] = _clamp(self.needs["water"] + 3.4 * gain)
            self.activity_effect = "water_recover"
        elif self.current_need == "energy":
            self.needs["energy"] = _clamp(self.needs["energy"] + 2.5 * gain)
            self.stress = _clamp(self.stress - 1.4 * gain)
            self.activity_effect = "rest_recover"
        elif self.current_need == "security":
            self.needs["security"] = _clamp(self.needs["security"] + 3.0 * gain)
            self.stress = _clamp(self.stress - 1.8 * gain)
            self.activity_effect = "security_recover"
        elif self.current_need == "social":
            self.needs["social"] = _clamp(self.needs["social"] + 2.4 * gain)
            self.stress = _clamp(self.stress - 0.9 * gain)
            self.activity_effect = "social_recover"
        else:
            self.needs["energy"] = _clamp(self.needs["energy"] + 0.10 * gain)
            self.needs["social"] = _clamp(self.needs["social"] + 0.05 * gain)
            self.stress = _clamp(self.stress - 0.35 * gain)
            self.activity_effect = f"work_{self.profession}"
        self.update_mood()

    def update(self, dt):
        self.update_needs(dt)
        moved = False
        if self.terrain_height_func:
            self.wander_timer += dt
            if self.wander_timer >= self.wander_change or math.hypot(self.target_x - self.x, self.target_z - self.z) < 0.3:
                self.wander_timer = 0.0
                self.wander_change = 1.5 + random.random() * 2.5
                self.choose_activity_target()

            dx = self.target_x - self.x
            dz = self.target_z - self.z
            dist = math.hypot(dx, dz)
            if dist > 0.05:
                step = self.speed * self.needs_speed_factor * dt
                move_x = dx / dist * min(step, dist)
                move_z = dz / dist * min(step, dist)
                self.x += move_x
                self.z += move_z
                self.yaw = math.degrees(math.atan2(move_x, move_z))
                moved = True

            # Mantener dentro del radio para que no se pierda
            dxs = self.x - self.spawn_x
            dzs = self.z - self.spawn_z
            if math.hypot(dxs, dzs) > self.wander_radius:
                ang = math.atan2(dzs, dxs) + math.pi
                self.x = self.spawn_x + math.cos(ang) * self.wander_radius
                self.z = self.spawn_z + math.sin(ang) * self.wander_radius
                self.direction = ang

            self.y = self.terrain_height_func(self.x, self.z) + self.height / 2
        self.apply_activity_effects(dt)
        target_move = 1.0 if moved else 0.0
        self.move_amount += (target_move - self.move_amount) * min(1.0, dt * 8.0)
        self.walk_phase += dt * (4.0 + self.speed * 2.0) * self.move_amount

    def render(self, highlight=False, debug_hitbox=False, detail_level="full"):
        from game.voxel_models import render_player_avatar, render_voxel_humanoid
        base_y = self.y - self.height / 2.0
        if hasattr(self, "admin_color"):
            body = self.admin_color
        else:
            # Color por profesión/hostilidad. Mantiene identidad sin usar modelos copiados.
            body = self.profession_color
        legendary = bool(getattr(self, "is_legendary", False))
        accent = (0.08, 0.08, 0.08) if not legendary else (1.0, 0.78, 0.10)
        detail_level = str(detail_level or "full")
        if detail_level == "far" and not highlight and not debug_hitbox:
            render_voxel_humanoid(
                self.x, base_y, self.z,
                yaw=self.yaw,
                body_color=body,
                skin_color=(0.78, 0.58, 0.40),
                accent_color=accent,
                legendary=legendary,
                debug_hitbox=False,
                selected=False,
                walk_phase=self.walk_phase,
                move_amount=min(0.45, self.move_amount),
                swimming=False,
            )
            return
        back_tool = None if detail_level != "full" else self.back_tool
        render_voxel_humanoid(
            self.x, base_y, self.z,
            yaw=self.yaw,
            body_color=body,
            skin_color=(0.78, 0.58, 0.40),
            accent_color=accent,
            legendary=legendary,
            debug_hitbox=debug_hitbox,
            selected=highlight,
            walk_phase=self.walk_phase,
            move_amount=self.move_amount,
            swimming=False,
        )

    def interactuar(self):
        self.update_mood()
        self.remember_event("interaction")
        if self.memoria == 1:
            line = f"Soy {self.nombre} {self.titulo}. Trabajo como {self.profession} y llevo mi {self.tool_label}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 2:
            line = f"Mi asunto ahora es {self.work_action}; suelo moverme cerca de {self.workplace}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 3:
            line = f"Estado: {self.mood}. {need_status_text(self.current_need)}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 4:
            line = f"Actitud: {self.stance}. {self.mood_detail}."
            self.remember_event("dialogue", line)
            return line
        line = f"{dialogue_tone_prefix(self)} {contextual_dialogue_line(self, self.memoria)}"
        self.remember_event("dialogue", line)
        return line


def generar_npcs_chunk(cx, cz, semilla):
    r = random.Random((cx*92821) ^ (cz*68917) ^ semilla)
    npcs = []
    cantidad = r.randint(0, 3)
    for i in range(cantidad):
        seed = r.randint(1,999999)
        x = cx*100 + r.randint(0,99)
        z = cz*100 + r.randint(0,99)
        npcs.append(NPC(seed, x, z, id_source=f"chunk_{cx}_{cz}", id_slot=i))
    return npcs
