"""Runtime de dialogo e IA local para NPCs.

Este modulo mantiene cache, cola, telemetria y adaptadores de modelo local
fuera de npc_manager.py para que el gestor de NPCs siga pequeno y legible.
"""

import json
import os
import subprocess
import time

from game.npc_identity import stable_float01 as _stable_float01
from game.npc_memory import compact_memory_notes, npc_memory_for
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

def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))

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


